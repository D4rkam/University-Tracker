from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Materia(models.Model):
    """
    Representa una asignatura o materia dentro del plan de estudios de un usuario.
    Almacena información sobre el estado de cursada, notas finales y ubicación en el plan (año/cuatrimestre).
    """

    ESTADOS_MATERIA = [
        ("AP", "Aprobada"),
        ("RP", "Reprobada"),
        ("CU", "Cursando"),
        ("NP", "No Iniciada"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="materias",
    )
    nombre = models.CharField(max_length=200, help_text="Ej: Análisis Matemático I")
    anio_plan = models.PositiveSmallIntegerField(
        verbose_name="Año de la carrera",
        default=1,
    )
    cuatrimestre = models.PositiveSmallIntegerField(
        choices=[(1, "Primer cuatrimestre"), (2, "Segundo cuatrimestre"), (0, "Anual")],
        verbose_name="Cuatrimestre",
        default=0,
    )

    estado = models.CharField(max_length=2, choices=ESTADOS_MATERIA, default="NP")

    nota_final = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Nota de examen final o promoción",
    )
    descripcion = models.TextField(blank=True, null=True)
    correlativas = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="es_correlativa_de"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ["anio_plan", "nombre"]

    def __str__(self):
        estado_icon = (
            "✅"
            if self.estado == "AP"
            else "❌"
            if self.estado == "RP"
            else "🕒"
            if self.estado == "CU"
            else "💤"
        )
        return f"{estado_icon} {self.nombre} ({self.get_estado_display()})"

    def get_promedio_parciales(self):
        evaluaciones = self.evaluaciones.filter(nota__isnull=False)
        if not evaluaciones.exists():
            return None
        total = sum(e.nota for e in evaluaciones)
        return total / evaluaciones.count()


class Evaluacion(models.Model):
    """
    Representa una instancia de evaluación (Parcial, TP, Recuperatorio) asociada a una materia específica.
    Permite llevar un registro detallado de las notas parciales durante la cursada.
    """

    TIPOS_EVALUACION = [
        ("PAR1", "1er Parcial"),
        ("PAR2", "2do Parcial"),
        ("PAR3", "3er Parcial"),
        ("REC1", "Recuperatorio 1"),
        ("REC2", "Recuperatorio 2"),
        ("TP", "Trabajo Práctico"),
        ("OTRO", "Otro"),
    ]

    CONTENIDOS = [("T", "Teoria"), ("P", "Práctica"), ("TP", "Teoría y Práctica")]

    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name="evaluaciones",
    )
    instancia = models.CharField(
        max_length=50, choices=TIPOS_EVALUACION, default="PAR1"
    )
    tipo_contenido = models.CharField(
        max_length=50,
        choices=CONTENIDOS,
        default="T",
    )
    fecha = models.DateField(null=True, blank=True)
    nota = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    observaciones = models.TextField(
        blank=True,
        max_length=100,
        help_text="Ej: 'Aprobado con lo justo'",
    )

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ["fecha", "instancia"]

    def __str__(self):
        return ""


class Facultad(models.Model):
    """
    Modelo para almacenar las Facultades o Universidades disponibles en el sistema.
    Se gestiona desde el panel de administración.
    """

    nombre = models.CharField(max_length=200, unique=True)
    siglas = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"

    def __str__(self):
        return f"{self.nombre} ({self.siglas})" if self.siglas else self.nombre


class Carrera(models.Model):
    """
    Modelo para almacenar las Carreras (Ingenierías, Licenciaturas, etc.) asociadas a una Facultad.
    """

    facultad = models.ForeignKey(
        Facultad, on_delete=models.CASCADE, related_name="carreras"
    )
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    """
    Extensión del modelo User de Django para almacenar información académica adicional.
    Vincula al usuario con una Facultad y una Carrera específica.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Facultad",
    )
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Carrera",
    )

    def __str__(self):
        facultad_nombre = self.facultad.nombre if self.facultad else "Sin Facultad"
        carrera_nombre = self.carrera.nombre if self.carrera else "Sin Carrera"
        return f"{self.user.username} - {carrera_nombre} ({facultad_nombre})"
