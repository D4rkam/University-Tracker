import csv
import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CsvUploadForm,
    CustomUserCreationForm,
    EvaluacionForm,
    MateriaForm,
    MateriaManualForm,
    PerfilUpdateForm,
)
from .models import Evaluacion, Facultad, Materia, Perfil


def get_carreras_data():
    """
    Helper para serializar las carreras agrupadas por facultad.
    Retorna un diccionario {facultad_id: [{id, nombre}, ...]} para usar en el frontend (JS).
    """
    data = {}
    for facultad in Facultad.objects.prefetch_related("carreras"):
        data[facultad.id] = [
            {"id": c.id, "nombre": c.nombre} for c in facultad.carreras.all()
        ]
    return data


@login_required
def dashboard(request):
    """
    Vista principal del usuario. Muestra:
    - Progreso de la carrera por año.
    - Promedio general.
    - Calendario de próximas evaluaciones.
    """
    materias = (
        Materia.objects.filter(usuario=request.user)
        .prefetch_related("correlativas", "es_correlativa_de", "evaluaciones")
        .order_by("anio_plan", "cuatrimestre", "nombre")
    )

    anios = []

    anios_disponibles = (
        materias.values_list("anio_plan", flat=True).distinct().order_by("anio_plan")
    )

    for anio_num in anios_disponibles:
        materias_del_anio = materias.filter(anio_plan=anio_num)

        # Calculamos progreso del año
        total = materias_del_anio.count()
        aprobadas = materias_del_anio.filter(estado="AP").count()
        porcentaje = int((aprobadas / total) * 100) if total > 0 else 0

        anios.append(
            {"numero": anio_num, "materias": materias_del_anio, "progreso": porcentaje}
        )

    # Calculamos promedio general de la carrera
    # Solo tomamos materias aprobadas con nota final
    promedio_general = materias.filter(estado="AP", nota_final__isnull=False).aggregate(
        Avg("nota_final")
    )["nota_final__avg"]

    # Obtener todas las evaluaciones con fecha para el calendario
    evaluaciones_calendario = (
        Evaluacion.objects.filter(materia__usuario=request.user, fecha__isnull=False)
        .select_related("materia")
        .order_by("fecha")
    )

    # Obtener años únicos de las evaluaciones para el filtro
    anios_evaluaciones = evaluaciones_calendario.dates("fecha", "year")

    context = {
        "anios": anios,
        "promedio_general": round(promedio_general, 2) if promedio_general else 0,
        "evaluaciones_calendario": evaluaciones_calendario,
        "anios_evaluaciones": anios_evaluaciones,
    }

    return render(request, "carrera/dashboard.html", context)


@login_required
def cargar_plan(request):
    """
    Permite al usuario cargar materias a su plan de estudios.
    Maneja dos flujos en la misma vista:
    1. Carga Masiva vía archivo CSV.
    2. Carga Manual de una materia individual.
    """
    # Deberiamos obtener el plan de estudios desde un archivo CSV subido por el usuario
    if request.method == "POST":
        if "archivo" in request.FILES:
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file_csv = request.FILES["archivo"]

                if not file_csv.name.endswith(".csv"):
                    messages.error(request, "El archivo debe ser un archivo CSV.")
                    return redirect("cargar_plan")

                file_data = file_csv.read().decode("utf-8").splitlines()
                reader = csv.reader(file_data)

                next(reader)  # Saltar la cabecera

                for row in reader:
                    if len(row) < 3:
                        continue  # Saltar filas incompletas
                    anio_plan, cuatrimestre, nombre = row
                    Materia.objects.create(
                        usuario=request.user,
                        nombre=nombre,
                        anio_plan=int(anio_plan),
                        cuatrimestre=int(cuatrimestre),
                    )
                messages.success(request, "Materias cargadas exitosamente.")
                return redirect("home")
        else:
            # Carga manual
            form_manual = MateriaManualForm(request.POST)
            if form_manual.is_valid():
                materia = form_manual.save(commit=False)
                materia.usuario = request.user
                materia.save()
                messages.success(request, "Materia agregada correctamente.")
                return redirect("cargar_plan")
            else:
                form = CsvUploadForm()
                return render(
                    request,
                    "carrera/cargar_plan.html",
                    {"form": form, "form_manual": form_manual},
                )
    else:
        form = CsvUploadForm()
        form_manual = MateriaManualForm()

    return render(
        request,
        "carrera/cargar_plan.html",
        {"form": form, "form_manual": form_manual},
    )


def register(request):
    """
    Vista de registro de nuevos usuarios.
    Incluye la selección dinámica de Facultad y Carrera.
    """
    if request.user.is_authenticated:
        return redirect("home")

    # Cargar datos de carreras desde la DB
    carreras_data = get_carreras_data()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}!")
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form, "carreras_data": json.dumps(carreras_data)},
    )


@login_required
def editar_materia(request, materia_id):
    """
    Permite editar los detalles de una materia (estado, nota final)
    y listar sus evaluaciones asociadas.
    """
    # Buscamos la materia, PERO solo si pertenece al usuario logueado.
    # Si intenta entrar a la materia ID=500 de otro, le dará Error 404.
    materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)

    # Formulario principal de la materia
    if request.method == "POST":
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, "Materia actualizada correctamente.")
            return redirect("editar_materia", materia_id=materia.id)
    else:
        form = MateriaForm(instance=materia)

    # También pasamos las evaluaciones existentes para mostrarlas en la lista
    evaluaciones = materia.evaluaciones.all()

    return render(
        request,
        "carrera/editar_materia.html",
        {"form": form, "materia": materia, "evaluaciones": evaluaciones},
    )


@login_required
def agregar_evaluacion(request, materia_id):
    """
    Agrega una nueva instancia de evaluación (Parcial, TP, etc.) a una materia.
    """
    materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)

    if request.method == "POST":
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            # Guardamos la evaluación pero sin subirla a la DB todavía
            evaluacion = form.save(commit=False)
            # Le asignamos la materia manualmente (relación)
            evaluacion.materia = materia
            evaluacion.save()
            messages.success(request, "Nota agregada.")
            # Volvemos a la pantalla de edición de ESA materia
            return redirect("editar_materia", materia_id=materia.id)
    else:
        form = EvaluacionForm()

    return render(
        request, "carrera/agregar_evaluacion.html", {"form": form, "materia": materia}
    )


@login_required
def borrar_evaluacion(request, evaluacion_id):
    """
    Elimina una evaluación específica.
    Soporta peticiones AJAX para borrado sin recarga completa.
    """
    # Vista rápida para borrar una nota
    evaluacion = get_object_or_404(
        Evaluacion, id=evaluacion_id, materia__usuario=request.user
    )
    materia_id = evaluacion.materia.id
    evaluacion.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    messages.success(request, "Evaluación eliminada.")
    return redirect("editar_materia", materia_id=materia_id)


@login_required
def editar_perfil(request):
    """
    Permite al usuario actualizar su información académica (Facultad y Carrera).
    """
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    # Cargar datos de carreras desde la DB
    carreras_data = get_carreras_data()

    if request.method == "POST":
        form = PerfilUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("home")
    else:
        form = PerfilUpdateForm(instance=perfil)

    return render(
        request,
        "carrera/perfil.html",
        {"form": form, "carreras_data": json.dumps(carreras_data)},
    )
