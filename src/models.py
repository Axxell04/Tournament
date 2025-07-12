from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Date, Time, SmallInteger, ForeignKey, CHAR, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import random
import secrets
import shortuuid

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

## Función para generar cédulas falsas
def gen_ced_rnd():
    return str(random.randint(1000000000, 9999999999))

class User(UserMixin):
    def __init__(self, cedula, nombre, contraseña, rol, **kargs):
        self.cedula = cedula
        self.nombre = nombre
        self.contraseña = contraseña
        self.rol = rol
        for key, value in kargs.items():
            setattr(self, key, value) 
    
    def get_id(self):
        return self.cedula
        
    def to_dict(self):
        res_dict = {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "rol": self.rol
        }
        if hasattr(self, "torneo"):
            res_dict.update({"torneo": self.torneo})
        elif hasattr(self, "equipo"):
            res_dict.update({"equipo": self.equipo})
            
        return res_dict
    
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

class Torneo(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    nombre: Mapped[str] = mapped_column(String(50))
    modalidad: Mapped[str] = mapped_column(String(50))
    descripcion: Mapped[str] = mapped_column(String(50))
    ubicacion: Mapped[str] = mapped_column(String(50))
    id_organizador: Mapped[str] = mapped_column(ForeignKey("organizador.cedula"))
    organizador: Mapped["Organizador"] = relationship("Organizador", back_populates="torneo")
    equipos: Mapped[list["Equipo"]] = relationship("Equipo", back_populates="torneo")
    
    def __init__(self, nombre, modalidad, descripcion, ubicacion, organizador):
        self.nombre = nombre
        self.modalidad = modalidad
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.organizador = organizador
    
    def to_dict(self):
        return({
            'id': self.id,
            'nombre': self.nombre,
            'modalidad': self.modalidad,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'organizador': self.organizador.to_dict()
        })

class Organizador(db.Model):
    cedula: Mapped[str] = mapped_column(CHAR(10), primary_key=True, default=gen_ced_rnd)
    nombre: Mapped[str] = mapped_column(String(50))
    contraseña: Mapped[str] = mapped_column(String(255))
    torneo: Mapped["Torneo"] = relationship("Torneo", back_populates="organizador")
    
    def __init__(self, cedula, nombre, contraseña):
        self.cedula = cedula
        self.nombre = nombre
        self.contraseña = contraseña
        
    def to_dict(self):
        return({
            'id': self.id,
            'nombre': self.nombre
        })
    
    @classmethod
    def to_rol(self):
        """
        Retorna el nombre de la clase del objeto \n
        Organizador -> 'organizador'
        """
        return __class__.__name__.lower()

class Equipo(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)
    ciudad: Mapped[str] = mapped_column(String(50))
    id_dirigente: Mapped[str] = mapped_column(ForeignKey("dirigente.cedula"))
    dirigente: Mapped["Dirigente"] = relationship("Dirigente", back_populates="equipo")
    id_entrenador: Mapped[str] = mapped_column(ForeignKey("entrenador.cedula"), nullable=True)
    entrenador: Mapped["Entrenador"] = relationship("Entrenador", back_populates="equipo")
    id_torneo: Mapped[int] = mapped_column(ForeignKey("torneo.id"), nullable=True)
    torneo: Mapped["Torneo"] = relationship("Torneo", back_populates="equipos")
    jugadores: Mapped[list["Jugador"]] = relationship("Jugador", back_populates="equipo")
    llaves: Mapped[list["LlaveEquipo"]] = relationship("LlaveEquipo", back_populates="equipo")
    
    def __init__(self, nombre, ciudad, dirigente, torneo):
        self.nombre = nombre
        self.ciudad = ciudad
        self.dirigente = dirigente
        self.torneo = torneo
        
class LlaveEquipo(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    token: Mapped[str] = mapped_column(String(32), default=lambda x:secrets.token_hex(16))
    usada: Mapped[bool] = mapped_column(Boolean(), default=False)
    id_equipo: Mapped[str] = mapped_column(ForeignKey("equipo.id"))
    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="llaves")
    
    def __init__(self, equipo):
        self.equipo = equipo
        

class Dirigente(db.Model):
    cedula: Mapped[str] = mapped_column(CHAR(10), primary_key=True, default=gen_ced_rnd)
    nombre: Mapped[str] = mapped_column(String(50))
    contraseña: Mapped[str] = mapped_column(String(255))
    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="dirigente")
    
    def __init__(self, cedula, nombre, contraseña):
        self.cedula = cedula
        self.nombre = nombre
        self.contraseña = contraseña
    
    @classmethod
    def to_rol(self):
        """
        Retorna el nombre de la clase del objeto \n
        Dirigente -> 'dirigente'
        """
        return __class__.__name__.lower()

class Entrenador(db.Model):
    cedula: Mapped[str] = mapped_column(CHAR(10),primary_key=True, default=gen_ced_rnd)
    nombre: Mapped[str] = mapped_column(String(50))
    contraseña: Mapped[str] = mapped_column(String(255))
    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="entrenador")
    
    def __init__(self, cedula, nombre, contraseña):
        self.cedula = cedula
        self.nombre = nombre
        self.contraseña = contraseña
    
    @classmethod
    def to_rol(self):
        """
        Retorna el nombre de la clase del objeto \n
        Entrenador -> 'entrenador'
        """
        return __class__.__name__.lower()
    


class Jugador(db.Model):
    cedula: Mapped[str] = mapped_column(CHAR(10), primary_key=True, default=gen_ced_rnd)
    nombre: Mapped[str] = mapped_column(String(50))
    contraseña: Mapped[str] = mapped_column(String(255))
    fecha_nacimiento: Mapped[str] = mapped_column(Date())
    posicion: Mapped[str] = mapped_column(String(50))
    id_equipo: Mapped[int] = mapped_column(ForeignKey("equipo.id"))
    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="jugadores")
    
    def __init__(self, cedula, nombre, contraseña, fecha_nacimiento, posicion, equipo):
        self.cedula = cedula
        self.nombre = nombre
        self.contraseña = contraseña
        self.fecha_nacimiento = fecha_nacimiento
        self.posicion = posicion
        self.equipo = equipo
    
    @classmethod
    def to_rol(self):
        """
        Retorna el nombre de la clase del objeto \n
        Jugador -> 'jugador'
        """
        return __class__.__name__.lower()

class Partido(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    fecha: Mapped[str] = mapped_column(Date())
    hora: Mapped[str] = mapped_column(Time())
    id_estadio: Mapped[int] = mapped_column(ForeignKey("estadio.id"))
    estadio: Mapped["Estadio"] = relationship("Estadio")
    resultado: Mapped["Resultado"] = relationship("Resultado", back_populates="partido")
    id_equipo_local: Mapped[int] = mapped_column(ForeignKey("equipo.id"))
    equipo_local: Mapped["Equipo"] = relationship("Equipo", foreign_keys=[id_equipo_local])
    id_equipo_visitante: Mapped[int] = mapped_column(ForeignKey("equipo.id"))
    equipo_visitante: Mapped["Equipo"] = relationship("Equipo", foreign_keys=[id_equipo_visitante])

class Estadio(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    nombre: Mapped[str] = mapped_column(String(50), nullable=True)
    ubicacion: Mapped[str] = mapped_column(String(50))
    
class Resultado(db.Model):
    id: Mapped[str] = mapped_column(String(30), primary_key=True, default=shortuuid.uuid)
    id_partido: Mapped[int] = mapped_column(ForeignKey("partido.id"))
    partido: Mapped["Partido"] = relationship("Partido", back_populates="resultado")
    goles_local: Mapped[int] = mapped_column(SmallInteger(), default=0)
    goles_visitante: Mapped[int] = mapped_column(SmallInteger(), default=0)