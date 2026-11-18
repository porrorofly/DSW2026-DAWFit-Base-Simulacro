from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from app.models import db, Actividad
from app.forms import SearchForm

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return redirect(url_for("public.mostrar_actividades"))


@public_bp.route("/actividades")
def mostrar_actividades():
    busqueda=request.args.get("busqueda","").strip()
    solo_con_plazas=request.args.get("solo_con_plazas")
    consulta = Actividad.query
    if busqueda:
        consulta=consulta.filter(Actividad.nombre.contains(busqueda))
    if solo_con_plazas:
        consulta=consulta.filter(Actividad.plazas_libres>0)
    actividades = consulta.all()

    deporte_fav = request.cookies.get("deporte_fav")
    
    return render_template(
        "catalogo.html",
        lista_actividades=actividades,
        deporte_fav=deporte_fav,
        busqueda=busqueda,
        solo_con_plazas=solo_con_plazas
       
    )


@public_bp.route("/actividad/<int:act_id>")
def ver_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)
    return render_template("actividad_detalle.html", actividad=actividad)



@public_bp.route("/preferencia/<string:deporte>")
def guardar_preferencia(deporte):
    respuesta = make_response(redirect(url_for("public.mostrar_actividades")))
    
    # Adjuntamos la cookie aplicando buenas prácticas de seguridad y duración (7 días)
    respuesta.set_cookie(
        "deporte_fav",
        value=deporte,
        max_age=15 * 24 * 60 * 60, # 7 días expresados en segundos
        httponly=True,            # Impide que JavaScript lea la cookie (prevención XSS)
        samesite="Lax"            # Evita el envío en peticiones cruzadas externas (CSRF)
    )
    flash(f"Deporte favorito guardado {deporte}","exito")
    return respuesta
  


@public_bp.route("/limpiar-preferencia")
def limpiar_preferencia():
    respuesta=make_response(redirect(url_for("public.mostrar_actividades")))
    respuesta.delete_cookie("deporte_fav")
    flash("Preferencia eliminada","info")
    return respuesta
  


@public_bp.route("/reservas/apuntar/<int:act_id>", methods=["POST"])
@login_required
def apuntar_actividad(act_id):
    reservas = session.get("reservas", [])
    actividad=db.get_or_404(Actividad, act_id)
    max_reservas=3
    
    if actividad.plazas_libres <= 0:
        flash("Esa actividad ya está llena.", "error")
        return redirect(url_for("public.mostrar_actividades"))
    else:
        if act_id in reservas:
            flash("Esa actividad ya la tienes en reservas.", "error")
            return redirect(url_for("public.mostrar_actividades"))
        else:
            if len(reservas)<max_reservas:
                reservas.append(act_id)
                session["reservas"]=reservas
                session.permanent=True
                session.modified=True
                flash("Se añadió la actividad a las reservas.", "exito")
            else:
                flash("Tiene superado el límite de actividades reservadas.", "error")
    return redirect(url_for("public.mostrar_actividades"))



@public_bp.route("/reservas")
@login_required
def ver_reservas():
    ids=session.get("reservas",[])
    actividades=Actividad.query.filter(Actividad.id.in_(ids)).all()
    ids_validos = [actividad.id for actividad in actividades]
    if len(ids_validos) != len(ids):
        session["reservas"] = ids_validos
        session.modified = True
    total_sin_descuento=0
    for actividad in actividades:
        total_sin_descuento+=actividad.cuota
    descuento_aplicado= len(actividades)==3
    if descuento_aplicado:
        total_final=total_sin_descuento-(total_sin_descuento*0.2)
        
    else:
        total_final=total_sin_descuento
    total_final=round(total_final,2)    
    return render_template(
        "reservas.html",
        actividades=actividades,
        total_sin_descuento=total_sin_descuento,
        descuento_aplicado=descuento_aplicado,
        total_final=total_final,
    )


@public_bp.route("/reservas/cancelar/<int:act_id>", methods=["POST"])
@login_required
def cancelar_reserva(act_id):
    reservas = session.get("reservas", [])
    if act_id in reservas:
        reservas.remove(act_id)
        session["reservas"] = reservas
        session.modified = True
        flash("Actividad quitada de las reservas.", "éxito")
    else:
        flash("Esa actividad no estaba en reservas.", "error")
    return redirect(url_for("public.ver_reservas"))


@public_bp.route("/reservas/confirmar", methods=["POST"])
@login_required
def confirmar_reservas():
    return redirect(url_for("public.mostrar_actividades"))

