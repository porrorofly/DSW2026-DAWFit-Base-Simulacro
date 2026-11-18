from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
)
from app.models import Actividad, Usuario


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión (Ya implementado)."""

    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="Introduce tu correo electrónico."),
            Email(message="Formato de correo no válido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="Introduce tu contraseña.")],
    )
    remember = BooleanField("Mantener sesión iniciada")
    submit = SubmitField("Entrar al Club")


class ActividadForm(FlaskForm):
    """Formulario para crear y editar actividades deportivas."""

    nombre = StringField(
        "Nombre de la Actividad",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres."),
        ],
    )
    deporte = StringField(
        "Modalidad Deportiva (ej. Pádel, Natación, Crossfit)",
        validators=[
            DataRequired(message="El deporte es obligatorio."),
            Length(min=3, max=50, message="Entre 3 y 50 caracteres."),
        ],
    )

    cuota = FloatField("Cuota Mensual (€)", validators=[DataRequired(),NumberRange(min=5.0,max=150,message="La cuota debe de ser más de 5€ y menos de 150€")])
    plazas_libres = IntegerField("Plazas Libres", default=10,validators=[NumberRange(min=0,message="El mínimo de plazas libres es 0")])
    archivo_imagen = FileField(
        "Cartel de la Actividad (JPG, PNG)",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Solo se admiten imágenes JPG, JPEG o PNG.")],
    )
    submit = SubmitField("Guardar Actividad")
    def __init__(self, *args, id_actual=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.id_actual = id_actual
    def validate_nombre(self, field):
        existente = Actividad.query.filter_by(nombre=field.data).first()
        if existente and existente.id != self.id_actual:
            raise ValidationError("Esa actividad ya está registrada.")


class RegistroForm(FlaskForm):
    """Formulario de alta para nuevos socios."""

    username = StringField(
        "Nombre de Usuario",
        validators=[
            DataRequired(message="El nombre de usuario es obligatorio."),
            Length(min=3, max=50, message="Debe tener entre 3 y 50 caracteres."),
        ],
    )
    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Introduce un correo válido."),
        ],
    )
    edad=IntegerField(
        "Edad",
        validators=[
            DataRequired(message="Edad obligoria"),
            NumberRange(min=16,message="Debe de ser mayor de 16 años")
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="Mínimo 6 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    
    submit = SubmitField("Registrarme como Socio")

    def validate_username(self, field):
        if Usuario.query.filter_by(username=field.data).first():
            raise ValidationError("Ese nombre de usuario ya está registrado.")

    def validate_email(self, field):
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError("Ese correo electrónico ya está en uso.")


class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField(
        "Contraseña actual",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="Mínimo 6 caracteres."),
        ],
    )    
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Actualizar Contraseña")

class SearchForm(FlaskForm):
    busqueda=StringField(
        "Buscar"
    )
    solo_con_plazas=BooleanField("Tiene plazas")
    submmit=SubmitField("Enviar")
