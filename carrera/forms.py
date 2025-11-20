from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Carrera, Evaluacion, Facultad, Materia, Perfil


class CsvUploadForm(forms.Form):
    """
    Formulario simple para la carga de archivos CSV.
    Se utiliza en la vista 'cargar_plan'.
    """

    archivo = forms.FileField(
        label="Selecciona tu plan de estudios (CSV)",
        help_text="Formato requerido: Año, Cuatrimestre (0,1,2), Nombre de Materia",
    )


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de registro de usuario personalizado.
    Extiende UserCreationForm para incluir:
    - Email (obligatorio)
    - Selección de Facultad (ModelChoiceField)
    - Selección de Carrera (filtrada dinámicamente por JS y validada en __init__)
    """

    facultad = forms.ModelChoiceField(
        queryset=Facultad.objects.all(),
        label="Facultad / Universidad",
        empty_label="Selecciona tu facultad",
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),
        label="Carrera",
        help_text="Selecciona tu facultad para ver las carreras",
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

        if "facultad" in self.data:
            try:
                facultad_id = int(self.data.get("facultad"))
                self.fields["carrera"].queryset = Carrera.objects.filter(
                    facultad_id=facultad_id
                ).order_by("nombre")
            except (ValueError, TypeError):
                pass

        # Limpiamos help_text solo de los campos de usuario por defecto si se desea
        # pero mantenemos los nuestros
        for field_name, field in self.fields.items():
            if field_name not in ["facultad", "carrera"]:
                field.help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Perfil.objects.create(
                user=user,
                facultad=self.cleaned_data["facultad"],
                carrera=self.cleaned_data["carrera"],
            )
        return user
        # Or for specific fields:
        # self.fields['password1'].help_text = None
        # self.fields['password2'].help_text = None


class MateriaForm(forms.ModelForm):
    """
    Formulario para editar una materia existente.
    Permite modificar estado, nota final, duración y año del plan.
    """

    class Meta:
        model = Materia
        # Campos que el usuario puede editar
        fields = ["estado", "nota_final", "cuatrimestre", "anio_plan"]
        labels = {
            "cuatrimestre": "Duración",
        }
        widgets = {
            "estado": forms.Select(attrs={"class": "form-select"}),
            # Ocultamos la nota final si no está aprobada (opcional, pero limpio)
        }


class EvaluacionForm(forms.ModelForm):
    """
    Formulario para crear o editar una evaluación (Parcial, TP, etc.).
    Incluye widgets HTML5 para selección de fecha.
    """

    class Meta:
        model = Evaluacion
        fields = ["instancia", "tipo_contenido", "nota", "fecha", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),  # Selector de fecha HTML5
            "observacion": forms.TextInput(attrs={"placeholder": "Ej: Muy difícil"}),
        }


class PerfilUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar el perfil del usuario.
    Permite cambiar Email, Facultad y Carrera.
    Maneja la lógica de filtrado de carreras según la facultad seleccionada.
    """

    email = forms.EmailField(label="Email", required=True)
    facultad = forms.ModelChoiceField(
        queryset=Facultad.objects.all(),
        label="Facultad",
        empty_label="Selecciona tu facultad",
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),
        label="Carrera",
        help_text="Selecciona tu facultad para ver las carreras",
    )

    class Meta:
        model = Perfil
        fields = ["facultad", "carrera"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

        if "facultad" in self.data:
            try:
                facultad_id = int(self.data.get("facultad"))
                self.fields["carrera"].queryset = Carrera.objects.filter(
                    facultad_id=facultad_id
                ).order_by("nombre")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.facultad:
            self.fields["carrera"].queryset = self.instance.facultad.carreras.order_by(
                "nombre"
            )

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if commit:
            perfil.save()
            user = perfil.user
            user.email = self.cleaned_data["email"]
            user.save()
        return perfil


class MateriaManualForm(forms.ModelForm):
    """
    Formulario para la carga manual de una nueva materia.
    Se utiliza en la vista 'cargar_plan' junto con el formulario CSV.
    """

    class Meta:
        model = Materia
        fields = ["nombre", "anio_plan", "cuatrimestre", "estado", "nota_final"]
        labels = {
            "cuatrimestre": "Duración",
        }
        widgets = {
            "estado": forms.Select(attrs={"class": "form-select"}),
        }
