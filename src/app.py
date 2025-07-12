from urllib.parse import quote_plus
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, get_flashed_messages
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from models import db, Entrenador, Equipo, LlaveEquipo, Estadio, Jugador, Organizador, Dirigente, Partido, Resultado, Torneo, User
from manager_models import ManagerUser
from config import config

app = Flask(__name__)

app.config.from_object(config["development"])

login_manager_app = LoginManager()
login_manager_app.init_app(app)

db.init_app(app)

with app.app_context():
    db.create_all()
    
@login_manager_app.user_loader
def load_user(id_user):
    return ManagerUser.get_by_id(id_user)
    
## RESPONSES ##
with app.app_context():
    RES_ERROR_PARAMS = jsonify(message = "Error", description = "Error en los parámetros de la petición"), 400
## RESPONSES ##

## VALIDATIONS ##
with app.app_context():
    def validate_rol(current_user:User, target_rol: str, target_template: str):
        if current_user.rol == target_rol:
            return render_template(target_template)
        
        if current_user.rol == Organizador.to_rol():
            return redirect(url_for("inicio_organizador"))
        elif current_user.rol == Dirigente.to_rol():
            return redirect(url_for("inicio_dirigente"))
        elif current_user.rol == Jugador.to_rol():
            return redirect(url_for("inicio_jugador"))
        elif current_user.is_anonymous:
            return redirect(url_for("inicio"))
        else:
            return redirect(url_for("inicio"))
## VALIDATIONS ##
    
    
## INICIO ##
@app.route("/", methods=["GET"])
def inicio():
    torneos = db.session.execute(db.select(Torneo)).scalars().all()
    return render_template("inicios/inicio.html", torneos=torneos)

@app.route("/organizador")
@login_required
def inicio_organizador():
    res = validate_rol(current_user, Organizador.to_rol(), "inicios/inicio_org.html")
    
    return res

@app.route("/dirigente")
@login_required
def inicio_dirigente():
    res = validate_rol(current_user, Dirigente.to_rol(), "inicios/inicio_dir.html")
    
    return res

@app.route("/jugador")
@login_required
def inicio_jugador():
    res = validate_rol(current_user, Jugador.to_rol(), "inicios/inicio_jug.html")
    
    return res

## INICIO ##


### REGISTRO ###

@app.route("/registro/organizador", methods=["GET", "POST"])
def registro_organizador():
    if request.method == "GET":
        return render_template("registros/registro_org.html")
    
    elif request.method == "POST":
        reg_user = None
        try:
            cedula = request.form["cedula"]
            nombre = request.form["nombre"]
            contraseña = request.form["contraseña"]
            
            reg_user = User(cedula, nombre, contraseña, Organizador.to_rol())
        except:
            return RES_ERROR_PARAMS
        ManagerUser.register(reg_user)
        return redirect(url_for("login"))

@app.route("/registro/dirigente", methods=["GET", "POST"])
def registro_dirigente():
    if request.method == "GET":
        action_form = request.path
        next = request.args.get("next")
        if next:
            action_form = f"{action_form}?next={next}"
        return render_template("registros/registro_dir.html", action_form=action_form)
    
    elif request.method == "POST":
        reg_user = None
        try:
            cedula = request.form["cedula"]
            nombre = request.form["nombre"]
            contraseña = request.form["contraseña"]
            
            reg_user = User(cedula, nombre, contraseña, Dirigente.to_rol())
        except:
            return RES_ERROR_PARAMS
        ManagerUser.register(reg_user)
        next = request.args.get("next")
        if next:
            return redirect(url_for("login", next=next))
        
        return redirect(url_for("login"))
    
### REGISTRO ###


### LOGIN ###

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        action_form = request.path
        registro_url = None

        next = request.args.get("next")
        if next:
            flash("Inicie sesión para continuar")
            action_form = f"{action_form}?next={next}"
            if "/nuevo/equipo" in next:
                registro_url = url_for("registro_dirigente", next=next)
                
        return render_template("logins/login.html", action_form=action_form, registro_url=registro_url)
    
    elif request.method == "POST":
        log_user = None
        try:
            cedula = request.form["cedula"]
            contraseña = request.form["contraseña"]
        
            log_user = User(cedula, None, contraseña, None)
        except:
            return RES_ERROR_PARAMS
        
        res_login = ManagerUser.login(log_user)
        
        if res_login:
            login_user(res_login)
            next = request.args.get("next")
            if next:
                return redirect(next)
            
            endpoint_redirect = ""
            if res_login.rol == Organizador.to_rol():
                endpoint_redirect = "inicio_organizador"
            elif res_login.rol == Dirigente.to_rol():
                endpoint_redirect = "inicio_dirigente"
            elif res_login.rol == Jugador.to_rol():
                endpoint_redirect = "inicio_jugador"
            return redirect(url_for(endpoint_redirect))
        elif res_login == False:
            flash("Contraseña incorrecta")
        elif res_login == None:
            flash("Usuario no existe")
        url_redirect = request.path
        next = request.args.get("next")
        if next:
            url_redirect = f"{url_redirect}?next={next}"
            
        return redirect(url_redirect)

### LOGIN ###


### LOGOUT ###
    
@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("inicio"))
        
### LOGOUT ###



### CREAR ###

@app.route("/crear/torneo", methods=["POST"])
@login_required
def crear_torneo():
    if current_user.rol != Organizador.to_rol():
        return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
    
    try:
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        modalidad = request.form["modalidad"]
        ubicacion = request.form["ubicacion"]
        
        organizador = db.session.get(Organizador, current_user.cedula)
        torneo = Torneo(nombre, modalidad, descripcion, ubicacion, organizador)
        db.session.add(torneo)
        db.session.commit()
    except:
        return RES_ERROR_PARAMS

    return redirect(url_for("inicio_organizador"))

@app.route("/crear/equipo", methods=["POST"])
@login_required
def crear_equipo():
    if current_user.rol != Dirigente.to_rol():
        return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
    
    try:
        nombre = request.form["nombre"]
        ciudad = request.form["ciudad"]
        
        dirigente = db.session.get(Dirigente, current_user.cedula)
        equipo = Equipo(nombre, ciudad, dirigente, None)
        db.session.add(equipo)
        db.session.commit()
    except Exception as e:
        print(e)
        return RES_ERROR_PARAMS
    
    return redirect(url_for("inicio_dirigente"))

### CREAR ###



### EDITAR ###

@app.route("/editar/torneo", methods=["POST"])
@login_required
def editar_torneo():
    if current_user.rol != Organizador.to_rol():
        return jsonify(message = "Success", description = "No tiene los permisos necesarios"), 401
    
    try:
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        modalidad = request.form["modalidad"]
        ubicacion = request.form["ubicacion"]
        
        torneo = db.session.get(Torneo, current_user.torneo.id)
        if torneo:
            torneo.nombre = nombre
            torneo.descripcion = descripcion
            torneo.modalidad = modalidad
            torneo.ubicacion = ubicacion
            
            db.session.commit()
    except:
        return RES_ERROR_PARAMS
    
    return redirect(url_for("inicio_organizador"))

@app.route("/editar/equipo", methods=["POST"])
@login_required
def editar_equipo():
    if current_user.rol != Dirigente.to_rol():
        return jsonify(message = "Error", description = "No tienen los permisos necesarios"), 401

    try:
        nombre = request.form["nombre"]
        ciudad = request.form["ciudad"]
        
        equipo = db.session.get(Equipo, current_user.equipo.id)
        equipo.nombre = nombre
        equipo.ciudad = ciudad
        db.session.commit()
    except:
        return RES_ERROR_PARAMS
    
    return redirect(url_for("inicio_dirigente"))

### EDITAR ###



### ELIMINAR ###

@app.route("/eliminar/torneo", methods=["POST"])
@login_required
def eliminar_torneo():
    if current_user.rol != Organizador.to_rol():
        return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
    
    torneo = db.session.get(Torneo, current_user.torneo.id)
    if torneo:
        db.session.delete(torneo)
        db.session.commit()
    
    return redirect(url_for("inicio_organizador"))

@app.route("/eliminar/equipo", methods=["POST"])
@login_required
def eliminar_equipo():
    if current_user.rol != Dirigente.to_rol():
        return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
    
    equipo = db.session.get(Equipo, current_user.equipo.id)
    if equipo:
        db.session.delete(equipo)
        db.session.commit()
    
    return redirect(url_for("inicio_dirigente"))

### ELIMINAR ###



### TORNEO ###

@app.route("/torneo/<string:id>")
def torneo_id(id:str):
    torneo = db.session.get(Torneo, id)
    if torneo:
        return render_template("torneos/torneo.html", torneo=torneo)
    else:
        return "El torneo no existe"
    
@app.route("/torneo/<string:id>/nuevo/equipo", methods=["GET", "POST"])
@login_required
def torneo_id_nuevo_equipo(id:str):
    torneo = db.session.get(Torneo, id)

    if request.method == "GET":
        if current_user.rol != Dirigente.to_rol():
            logout_user()
            flash("Necesita rol de Dirigente para acceder")
            return redirect(url_for("login", next=request.path))
        if not torneo:
            return "El torneo no existe"
        
        equipo = None
        if current_user.equipo:
            equipo = db.session.get(Equipo, current_user.equipo.id)
        if equipo:
            if equipo.torneo != torneo:
                equipo.torneo = torneo
                db.session.commit()
                flash(f'Inscrito en el torneo "{torneo.nombre}"')
            else:
                flash(f'Su equipo ya se encontraba inscrito en el torneo {torneo.nombre}')
            return redirect(url_for("inicio_dirigente"))
        
        return render_template("torneos/torneo_nuevo_equipo.html")
    
    elif request.method == "POST":
        if current_user.rol != Dirigente.to_rol():
            return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
        
        try:
            nombre = request.form["nombre"]
            ciudad = request.form["ciudad"]
            
            dirigente = db.session.get(Dirigente, current_user.cedula)
            equipo = Equipo(nombre, ciudad, dirigente, torneo)
            db.session.add(equipo)
            db.session.commit()
            flash(f'Inscrito en el torneo "{torneo.nombre}"')
            return redirect(url_for("inicio_dirigente"))
        except:
            return RES_ERROR_PARAMS
    
@app.route("/torneo/<string:id>/generar/encuentros", methods=["POST"])
def torneo_id_generar_encuentros(id:str):
    torneo = db.session.get(Torneo, current_user.torneo.id)
    if torneo:
        for equipo in torneo.equipos:
            print(equipo.nombre)
            
    return redirect(url_for("torneo_id", id=id))
        
    
### TORNEO ###



### EQUIPO ###

@app.route("/equipo/<string:id>", methods=["GET", "POST"])
def equipo_id(id:str):
    equipo = db.session.get(Equipo, id)
    if not equipo:
        return "El equipo no existe"

    return render_template("equipos/equipo.html", equipo=equipo)

@app.route("/equipo/<string:id>/generar/llave", methods=["POST"])
@login_required
def equipo_id_generar_llave(id:str):
    if current_user.rol != Dirigente.to_rol():
        return jsonify(message = "Error", description = "No tiene los permisos necesarios"), 401
    
    equipo = db.session.get(Equipo, current_user.equipo.id)
    if equipo:
        llave_equipo = LlaveEquipo(equipo)
        db.session.add(llave_equipo)
        db.session.commit()
    
    return redirect(url_for("inicio_dirigente"))

@app.route("/equipo/<string:id>/usar/llave/<string:token>", methods=["GET", "POST"])
def equipo_id_usar_llave(id:str, token:str):
    equipo = db.session.get(Equipo, id)
    llave_equipo: LlaveEquipo = db.session.execute(db.select(LlaveEquipo).where(LlaveEquipo.token == token)).scalar()
    if not equipo:
        return "El equipo no existe"
    
    if request.method == "GET":
        if llave_equipo.usada:
            return "La llave ya fue utilizada", 404
        
        return render_template("equipos/equipo_usar_llave.html")
    
    elif request.method == "POST":
        if llave_equipo.usada:
            return jsonify(message = "Error", description = "La llave ya fue utilizada"), 404
        
        try:
            cedula = request.form["cedula"]
            nombre = request.form["nombre"]
            contraseña = request.form["contraseña"]
            fecha_nacimiento = request.form["fecha_nacimiento"]
            posicion = request.form["posicion"]
            
            reg_user = User(cedula, nombre, contraseña, Jugador.to_rol(), fecha_nacimiento=fecha_nacimiento, posicion=posicion, equipo=equipo)
            ManagerUser.register(reg_user)
            llave_equipo.usada = True
            db.session.commit()
        except:
            return RES_ERROR_PARAMS
        
        return "Inscripción exitosa"
        
    

### EQUIPO ###


    
def error_401(error):
    return redirect(url_for("login", next=request.path))

app.register_error_handler(401, error_401)


## EJECUCIÓN 
app.run(debug=True, host="0.0.0.0")

