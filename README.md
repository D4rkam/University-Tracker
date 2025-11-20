# 🎓 University Tracker

**University Tracker** es una aplicación web desarrollada en **Django** diseñada para ayudar a estudiantes universitarios a gestionar su progreso académico de manera eficiente. Permite realizar un seguimiento detallado de materias, notas, promedios y fechas de exámenes en una interfaz moderna y amigable (Dark Mode).

---

## ✨ Características Principales

### 📊 Dashboard Interactivo
- **Progreso por Año:** Visualización gráfica del porcentaje de materias aprobadas por cada año de la carrera.
- **Promedio General:** Cálculo automático del promedio basado en las notas finales cargadas.
- **Calendario de Evaluaciones:** Lista cronológica de próximos parciales, finales o entregas.

### 📚 Gestión de Materias
- **Carga Masiva (CSV):** Importa tu plan de estudios completo subiendo un archivo CSV simple.
- **Carga Manual:** Agrega materias individualmente especificando nombre, año y duración.
- **Estados de Materia:** Gestiona el estado de cada asignatura:
  - 💤 No Iniciada
  - Cursando
  - ✅ Aprobada (Final/Promoción)
  - ❌ Reprobada
- **Detalles Académicos:** Registra notas de cursada, notas finales y correlatividades.

### 📝 Evaluaciones
- Agrega múltiples instancias de evaluación por materia (Parciales, Recuperatorios, TPs).
- Registra notas, fechas y observaciones.
- Diferenciación entre contenido Teórico y Práctico.

### 👤 Perfil y Configuración
- **Gestión de Perfil:** Actualiza tu Facultad y Carrera.
- **Base de Datos Dinámica:** Las Facultades y Carreras son gestionables desde el panel de administración, permitiendo escalabilidad para múltiples universidades.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.12+, Django 5.x
- **Base de Datos:** SQLite (Por defecto, escalable a PostgreSQL/MySQL)
- **Frontend:** HTML5, CSS3
- **Estilos:** [Tailwind CSS](https://tailwindcss.com/) (vía CDN)
- **Librerías Adicionales:**
  - `FilePond` (para carga de archivos elegante)

---

## 🚀 Instalación y Configuración

Sigue estos pasos para correr el proyecto localmente:

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd university-tracker
```

### 2. Crear y activar entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install django
# Si existe un requirements.txt:
# pip install -r requirements.txt
```

### 4. Migraciones de Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Superusuario (Admin)
Para acceder al panel de administración y cargar Facultades/Carreras:
```bash
python manage.py createsuperuser
```

### 6. Correr el servidor
```bash
python manage.py runserver
```
Accede a `http://127.0.0.1:8000/` en tu navegador.

---

## 📖 Guía de Uso

### Carga de Facultades y Carreras (Admin)
Antes de que los usuarios se registren, el administrador debe cargar las opciones disponibles:
1. Ve a `http://127.0.0.1:8000/admin/` e inicia sesión.
2. En la sección **Carrera**, agrega **Facultades**.
3. Luego, agrega **Carreras** y asócialas a sus respectivas facultades.

### Importación de Plan de Estudios (CSV)
Para cargar materias masivamente, crea un archivo `.csv` (sin encabezados o saltando la primera línea si el sistema lo requiere) con el siguiente formato:

| Columna 1 (Año) | Columna 2 (Duración) | Columna 3 (Nombre) |
| :--- | :--- | :--- |
| 1 | 0 | Análisis Matemático I |
| 1 | 1 | Sistemas y Organizaciones |
| 2 | 2 | Física II |

**Referencias de Duración:**
- `0`: Anual
- `1`: 1er Cuatrimestre
- `2`: 2do Cuatrimestre

---

## 📂 Estructura del Proyecto

```
university-tracker/
│
├── manage.py               # Script de gestión de Django
├── db.sqlite3              # Base de datos local
│
├── universitytracker/      # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── carrera/                # Aplicación principal (Core)
│   ├── admin.py            # Configuración del panel admin
│   ├── models.py           # Modelos (Materia, Evaluacion, Perfil, Facultad, Carrera)
│   ├── views.py            # Lógica de las vistas (Dashboard, Carga, etc.)
│   ├── forms.py            # Formularios (CSV, Manual, Registro)
│   ├── urls.py             # Rutas de la aplicación
│   │
│   └── templates/          # Archivos HTML
│       ├── carrera/        # Templates específicos de la app
│       │   ├── dashboard.html
│       │   ├── cargar_plan.html
│       │   ├── perfil.html
│       │   └── ...
│       └── registration/   # Templates de autenticación (Login/Signup)
│
└── ...
```

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Si deseas mejorar el proyecto:
1. Haz un Fork del proyecto.
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`).
3. Haz Commit de tus cambios (`git commit -m 'Agregada nueva funcionalidad'`).
4. Haz Push a la rama (`git push origin feature/NuevaFuncionalidad`).
5. Abre un Pull Request.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Siéntete libre de usarlo y modificarlo para tus necesidades académicas.
