from werkzeug.security import generate_password_hash
from models import db, User, Organizador, Dirigente, Jugador

class ManagerUser():
    @classmethod
    def get_by_id(self, id: str):
        for rol in (Organizador, Dirigente, Jugador):
            res_user = db.session.get(rol, id)
            if res_user:
                break
        
        if res_user:
            match_user = None
            rol = res_user.to_rol()
            if rol == Organizador.to_rol():
                match_user = User(res_user.cedula, res_user.nombre, True, rol, torneo=res_user.torneo)
            elif rol == Dirigente.to_rol():
                match_user = User(res_user.cedula, res_user.nombre, True, rol, equipo=res_user.equipo)
            elif rol == Jugador.to_rol():
                match_user = User(res_user.cedula, res_user.nombre, True, rol, fecha_nacimiento=res_user.fecha_nacimiento, posicion=res_user.posicion, equipo=res_user.equipo)
            
            return match_user
        else:
            return None
        
    
    @classmethod
    def register(self, user:User):
        new_user = None
        if user.rol == Organizador.to_rol():
            new_user = Organizador(user.cedula, user.nombre, generate_password_hash(user.contraseña))
        elif user.rol == Dirigente.to_rol():
            new_user = Dirigente(user.cedula, user.nombre, generate_password_hash(user.contraseña))
        elif user.rol == Jugador.to_rol():
            new_user = Jugador(user.cedula, user.nombre, generate_password_hash(user.contraseña), user.fecha_nacimiento, user.posicion, user.equipo)
        
        if new_user: 
            db.session.add(new_user)
            db.session.commit()
    
    @classmethod
    def login(self, user:User):
        """
        Si el registro es exitoso -> User \n
        Si la contraseña es incorrecta -> False \n
        Si el usuario no existe -> None
        """
        res_user = None
        for rol in (Organizador, Dirigente, Jugador):
            res_user = db.session.get(rol, user.cedula)
            if res_user:
                break
        
        if res_user:
            if User.check_password(res_user.contraseña, user.contraseña):
                match_user = None
                rol = res_user.to_rol()
                if rol == Organizador.to_rol():
                    match_user = User(res_user.cedula, res_user.nombre, True, rol, torneo=res_user.torneo)
                elif rol == Dirigente.to_rol():
                    match_user = User(res_user.cedula, res_user.nombre, True, rol, equipo=res_user.equipo)
                elif rol == Jugador.to_rol():
                    match_user = User(res_user.cedula, res_user.nombre, True, rol, fecha_nacimiento=res_user.fecha_nacimiento, posicion=res_user.posicion, equipo=res_user.equipo)
                return match_user
            else:
                return False
        else:
            return None
                    