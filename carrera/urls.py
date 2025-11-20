from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    agregar_evaluacion,
    borrar_evaluacion,
    cargar_plan,
    dashboard,
    editar_materia,
    editar_perfil,
    register,
)

urlpatterns = [
    path("", dashboard, name="home"),
    path("perfil/", editar_perfil, name="editar_perfil"),
    path("cargar-plan/", cargar_plan, name="cargar_plan"),
    path("editar-materia/<int:materia_id>/", editar_materia, name="editar_materia"),
    path(
        "agregar-evaluacion/<int:materia_id>/",
        agregar_evaluacion,
        name="agregar_evaluacion",
    ),
    path(
        "borrar-evaluacion/<int:evaluacion_id>/",
        borrar_evaluacion,
        name="borrar_evaluacion",
    ),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", register, name="signup"),
]
