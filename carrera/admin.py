from django.contrib import admin

from .models import Carrera, Evaluacion, Facultad, Materia, Perfil


# django inlines
class EvaluacionInline(admin.TabularInline):
    """
    Permite editar evaluaciones directamente desde la vista de detalle de una Materia.
    """

    model = Evaluacion
    extra = 1
    min_num = 0
    fields = ("instancia", "tipo_contenido", "nota", "fecha", "observaciones")
    readonly_fields = ("fecha",)


class CarreraInline(admin.TabularInline):
    """
    Permite agregar carreras directamente desde la vista de detalle de una Facultad.
    """

    model = Carrera
    extra = 1


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Facultades.
    Incluye la edición en línea de sus carreras asociadas.
    """

    inlines = [CarreraInline]
    list_display = ("nombre", "siglas")
    search_fields = ("nombre", "siglas")


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Carreras.
    Permite filtrar por facultad.
    """

    list_display = ("nombre", "facultad")
    list_filter = ("facultad",)
    search_fields = ("nombre",)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Perfiles de usuario.
    Permite ver rápidamente qué carrera estudia cada usuario.
    """

    list_display = ("user", "facultad", "carrera")
    list_filter = ("facultad", "carrera")
    search_fields = ("user__username", "user__email")


class MateriaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Materias.
    Incluye la edición en línea de sus evaluaciones.
    """

    inlines = [EvaluacionInline]
    list_display = (
        "nombre",
        "anio_plan",
        "estado",
        "nota_final",
        "calcular_promedio_parciales",
    )
    list_filter = ("estado", "anio_plan", "cuatrimestre")
    search_fields = ("nombre",)
    ordering = ("anio_plan", "nombre")
    filter_horizontal = ("correlativas",)
    readonly_fields = ("calcular_promedio_parciales",)

    def calcular_promedio_parciales(self, obj):
        promedio = obj.get_promedio_parciales()
        return f"{promedio:.2f}" if promedio is not None else "-"

    calcular_promedio_parciales.short_description = "Promedio de Parciales"


# Register your models here.
admin.site.register(Materia, MateriaAdmin)
admin.site.site_header = "Seguimiento Universitario Admin"
admin.site.site_title = "Seguimiento Universitario Panel Admin"
admin.site.index_title = (
    "Bienvenido al Panel de Administración del Seguimiento Universitario"
)
