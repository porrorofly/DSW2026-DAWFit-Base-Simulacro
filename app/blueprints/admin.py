import os
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models import db, login_manager, Actividad
from app.forms import ActividadForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def solo_monitores():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()  
    if not current_user.es_monitor:
        abort(403) 

@admin_bp.route("/actividad/nueva", methods=["GET", "POST"])
def crear_actividad():
    form = ActividadForm()
    if form.validate_on_submit():
        actividad=Actividad(
            nombre=form.nombre.data,
            deporte=form.deporte.data,
            cuota=form.cuota.data,
            plazas_libres=form.plazas_libres.data
        )
        archivo=form.archivo_imagen.data
        if archivo and archivo.filename:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = f"{actividad.deporte.lower()}_{nombre_seguro}"
            actividad.imagen = nombre_final
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_final)
            
            archivo.save(ruta)
        db.session.add(actividad)
        db.session.commit()
        flash(f"Actividad «{actividad.titulo}» creada correctamente.", "exito")            
    return redirect(url_for("public.mostrar_actividades"))


@admin_bp.route("/actividad/<int:act_id>/editar", methods=["GET", "POST"])
def editar_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)
    form = ActividadForm(obj=actividad,id_actual=actividad.id)

    if form.validate_on_submit():
        actividad.nombre = form.nombre.data
        actividad.deporte = form.deporte.data
        actividad.cuota = form.cuota.data
        actividad.plazas_libres = form.plazas_libres.data

        archivo = form.archivo_imagen.data
        if archivo and archivo.filename:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = f"{actividad.deporte.lower()}_{nombre_seguro}"

            if actividad.imagen and actividad.imagen != nombre_final:
                ruta_antigua = os.path.join(current_app.config["UPLOAD_FOLDER"], actividad.imagen)
                if os.path.exists(ruta_antigua):
                    os.remove(ruta_antigua)

            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_final)
            archivo.save(ruta)
            actividad.imagen = nombre_final

        db.session.commit()
        flash(f"Libro «{actividad.nombre}» actualizado correctamente.", "exito")
        return redirect(url_for("public.mostrar_actividades"))

    return render_template(
        "actividad_form.html",
        form=form,
        titulo="Editar Actividad",
        actividad=actividad,
    )


@admin_bp.route("/actividad/<int:act_id>/eliminar", methods=["POST"])
def eliminar_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)
    if actividad.plazas_libres==0:
        if actividad.imagen:
            ruta =os.path.join(current_app.config["UPLOAD_FOLDER"], actividad.imagen)
            if os.path.exists(ruta):
                os.remove(ruta)
        nombre=actividad.nombre
        db.session.delete(actividad)
        db.session.commit()   
        flash(f"Se ha eliminado el libro con el título  «{nombre}»", "exito")
        return redirect(url_for("public.mostrar_libros"))
                  
    else:
        flash(f"No se puede eliminar «{actividad.nombre}»: aún tiene {actividad.plazas_libres} plazas libres.", "error")
        return redirect(url_for("public.mostrar_actividades"))
    
