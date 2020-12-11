from flask import Flask, render_template, redirect, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template,redirect,url_for,flash, request
from flask_login import UserMixin
from datetime import datetime
app=Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'gestorproaqp@gmail.com',
    MAIL_PASSWORD = 'joaquindaryl'
)
mail = Mail(app)
app.secret_key='replace_later'
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://acvkbvhdpkqdfx:cd1254236e14c2916acc8efcabe23abd59c3022f4fe52c3a2c0a12059f197ad4@ec2-54-163-47-62.compute-1.amazonaws.com:5432/de1bc8lmmb3b0s'
db= SQLAlchemy(app)
#TABLAS INTERMEDIARIAS DE LAS RELACIONES DE MUCHOS A MUCHOS
#Evento_Usuario
gestion_e =db.Table('gestion_e',
                    db.Column('id_usuario', db.Integer, db.ForeignKey('Usuarios.id'), primary_key=True),
                    db.Column('id_evento', db.Integer, db.ForeignKey('Evento.id_evento'),primary_key=True))
Evento_Material=db.Table('Evento_Material',
                db.Column('id_evento',db.Integer,db.ForeignKey('Evento.id_evento'),primary_key=True),
                db.Column('id_material',db.Integer,db.ForeignKey('Material.id_material'),primary_key=True))
Usuario_Comite=db.Table('Usuario_Comite',
                db.Column('id_usuario',db.Integer,db.ForeignKey('Usuarios.id'),primary_key=True),
                db.Column('id_comite',db.Integer,db.ForeignKey('Comite_org.id_comite'),primary_key=True))
Evento_Comite=db.Table('Evento_Comite',
                db.Column('id_evento',db.Integer,db.ForeignKey('Evento.id_evento'),primary_key=True),
                db.Column('id_comite',db.Integer,db.ForeignKey('Comite_org.id_comite'),primary_key=True))
Ambiente_Actividad=db.Table('Ambiente_Actividad',
                db.Column('id_actividad',db.Integer,db.ForeignKey('Actividad.id_actividad'),primary_key=True),
                db.Column('id_ambiente',db.Integer,db.ForeignKey('Ambiente.id_ambiente'),primary_key=True))
Ambiente_Evento=db.Table('Ambiente_Evento',
                db.Column('id_evento',db.Integer,db.ForeignKey('Evento.id_evento'),primary_key=True),
                db.Column('id_ambiente',db.Integer,db.ForeignKey('Ambiente.id_ambiente'),primary_key=True))
Ambiente_Material=db.Table('Ambiente_Material',
                db.Column('id_ambiente',db.Integer,db.ForeignKey('Ambiente.id_ambiente'),primary_key=True),
                db.Column('id_material',db.Integer,db.ForeignKey('Material.id_material'),primary_key=True))
Paquete_Participante=db.Table('Paquete_Participante',
                db.Column('id_participante',db.Integer,db.ForeignKey('Participante.id_participante'),primary_key=True),
                db.Column('id_paquete',db.Integer,db.ForeignKey('Paquete.id_paquete'),primary_key=True))
Paquete_Usuario=db.Table('Paquete_Usuario',
                db.Column('id_usuario',db.Integer,db.ForeignKey('Usuarios.id'),primary_key=True),
                db.Column('id_paquete',db.Integer,db.ForeignKey('Paquete.id_paquete'),primary_key=True))
Paquete_Actividad=db.Table('Paquete_Actividad',
                db.Column('id_paquete',db.Integer,db.ForeignKey('Paquete.id_paquete'),primary_key=True),
                db.Column('id_actividad',db.Integer,db.ForeignKey('Actividad.id_actividad'),primary_key=True))

#CREA LOS MODELOS EN LA BASE DE DATOS Y MANTIENE LAS INTERACCIONES DE:
#ML_01 Y ML_02
class User(UserMixin, db.Model):
    __tablename__= "Usuarios"
    id= db.Column(db.Integer, primary_key=True)
    usuario=db.Column(db.String(25),unique=True, nullable=False)
    contraseña=db.Column(db.String(),nullable=False)
    email=db.Column(db.String(120),unique=True)
    eventos=db.relationship('Evento',secondary=gestion_e, backref=db.backref('Usuarios_r'), lazy='dynamic')
    id_rol = db.Column(db.Integer, db.ForeignKey('Rol.id_rol'),nullable=True)
    comites=db.relationship('Comite',secondary=Usuario_Comite,backref=db.backref('Usuarios'),lazy='dynamic')
#CREA LOS MODELOS EN LA BASE DE DATOS Y MANTIENE LAS INTERACCIONES DE:
#MC_01, MC_02, MC_03.MC_04,MC_05
class Evento(db.Model):
    __tablename__= "Evento"
    id_evento= db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(100),nullable=False)
    fecha_inicial=db.Column(db.DateTime,nullable=False)
    fecha_final=db.Column(db.DateTime,nullable=False)
    ubicacion=db.Column(db.String(100),nullable=False)
    descripcion=db.Column(db.String(280),nullable=False)
    Materiales=db.relationship('Material',secondary=Evento_Material, backref=db.backref('Eventos'),lazy='dynamic')
    Comites=db.relationship('Comite',secondary=Evento_Comite,backref=db.backref('Eventos'),lazy='dynamic')
#CREA LOS MODELOS EN LA BASE DE DATOS Y MANTIENE LAS INTERACCIONES DE:
#MG_04,MG_05
class Rol(db.Model):
    __tablename__="Rol"
    id_rol=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(100),nullable=False)
    descripcion=db.Column(db.String(280),nullable=False)

class Permiso_Acceso(db.Model):
    __tablename__="Permiso_Acceso"
    id_permiso=db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('Rol.id_rol'), nullable=False)
# class Permiso_Acceso_Modulos(db.Model):
#     __tablename__="Permiso_Acceso_Modulos"
#     id_permiso=db.Column(db.Integer, db.ForeignKey('Permiso_Acceso.id_permiso'), nullable=False)
#     #????
# class Permiso_Acceso_Submodulos(db.Model):
#     __tablename__="Permiso_Acceso_Submodulos"
#     id_permiso = db.Column(db.Integer, db.ForeignKey('Permiso_Acceso.id_permiso'), nullable=False)
#     #???? que pedo con esa wea

#CREA LOS MODELOS EN LA BASE DE DATOS Y MANTIENE LAS INTERACCIONES DE:
#MC_14, MC_15, MC_16.MC_17
class Material(db.Model):
    __tablename__="Material"
    id_material=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(100),nullable=False)
    stock=db.Column(db.Integer)
    descripcion=db.Column(db.String(280),nullable=False)
class Actividad(db.Model):
    __tablename__="Actividad"
    descripcion=db.Column(db.String(300))
    hora_inicio=db.Column(db.Time,nullable=False)
    hora_fin=db.Column(db.Time,nullable=False)
    fecha_inicio=db.Column(db.DateTime,nullable=False)
    fecha_fin=db.Column(db.DateTime,nullable=False)
    id_actividad=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(150),nullable=False)
    id_evento=db.Column(db.Integer,db.ForeignKey('Evento.id_evento'), nullable=False)
class Ambiente(db.Model):
    __tablename__="Ambiente"
    id_ambiente=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(150),nullable=False)
    capacidad=db.Column(db.Integer,nullable=False)
    descripcion=db.Column(db.String(300),nullable=False)
    latitud=db.Column(db.Float,nullable=False)
    longitud=db.Column(db.Float,nullable=False)
    Actividades = db.relationship('Actividad', secondary=Ambiente_Actividad, backref=db.backref('Ambientes'),lazy='dynamic')
    Eventos = db.relationship('Evento', secondary=Ambiente_Evento, backref=db.backref('Ambientes'), lazy='dynamic')
    Materiales = db.relationship('Material', secondary=Ambiente_Material, backref=db.backref('Ambientes'), lazy='dynamic')
class Comite(db.Model):
    __tablename__="Comite_org"
    id_comite=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(150),nullable=False)
    representante=db.Column(db.String(150),nullable=False)
    descripcion=db.Column(db.String(300))
class Participante(db.Model):
    __tablename__="Participante"
    id_participante=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(150),nullable=False)
    correo=db.Column(db.String(150),nullable=False)
    tipo=db.Column(db.String(150),nullable=False)
class Reporte(db.Model):
    __tablename__="Reporte"
    tipo=db.Column(db.String(150),nullable=False)
    estado=db.Column(db.String(150),nullable=False)
    modulo=db.Column(db.String(150),nullable=False)
    fecha_inicio=db.Column(db.DateTime,nullable=False)
    fecha_fin=db.Column(db.DateTime,nullable=False)
    id_reporte=db.Column(db.Integer,primary_key=True)
class Factura(db.Model):
    __tablename__="Factura"
    id_factura=db.Column(db.Integer,primary_key=True)
    descuento=db.Column(db.Float,nullable=False)
    IVA = db.Column(db.Float, nullable=False)
    fecha=db.Column(db.DateTime,nullable=False)
    id_participante=db.Column(db.Integer,db.ForeignKey('Usuarios.id'), nullable=False)
class Asistencia(db.Model):
    __tablename__="Asistencia"
    id_asistencia=db.Column(db.Integer,primary_key=True)
    estado=db.Column(db.String(150),nullable=False)
    id_usuario=db.Column(db.Integer,db.ForeignKey('Usuarios.id'),nullable=False)
    id_participante=db.Column(db.Integer,db.ForeignKey('Participante.id_participante'),nullable=False)
    id_reporte=db.Column(db.Integer,db.ForeignKey('Reporte.id_reporte'),nullable=False)
class Gasto(db.Model):
    __tablename__="Gasto"
    id_gasto=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(150),nullable=False)
    estado=db.Column(db.String(150),nullable=False)
    presupuesto=db.Column(db.Float,nullable=False)
    id_reporte=db.Column(db.Integer,db.ForeignKey('Reporte.id_reporte'),nullable=False)
    id_factura=db.Column(db.Integer,db.ForeignKey('Factura.id_factura'),nullable=False)
class Ingreso(db.Model):
    __tablename__="Ingreso"
    id_ingreso=db.Column(db.Integer,primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(150), nullable=False)
    id_reporte = db.Column(db.Integer, db.ForeignKey('Reporte.id_reporte'), nullable=False)
    id_factura = db.Column(db.Integer, db.ForeignKey('Factura.id_factura'), nullable=False)
class Paquete(db.Model):
    __tablename__="Paquete"
    nombre=db.Column(db.String(150), nullable=False)
    id_paquete=db.Column(db.Integer,primary_key=True)
    id_evento=db.Column(db.Integer,db.ForeignKey('Evento.id_evento'),nullable=False)
    Participantes = db.relationship('Participante', secondary=Paquete_Participante, backref=db.backref('Paquetes'), lazy='dynamic')
    Usuarios = db.relationship('User', secondary=Paquete_Usuario, backref=db.backref('Paquetes'), lazy='dynamic')
    Actividades = db.relationship('Actividad', secondary=Paquete_Actividad, backref=db.backref('Paquetes'), lazy='dynamic')
#PALTASA CON ESTAS 4 ULTIMAS TABLAS Y SU PRIMARY KEY
class Paquete_Tipo_Participante(db.Model):
    __tablename__="Paquete_Tipo_Participante"
    tipo_participante=db.Column(db.String(150), nullable=False)
    id_paquete=db.Column(db.ForeignKey('Paquete.id_paquete'),nullable=False,primary_key=True)
class Paquete_Precio(db.Model):
    __tablename__="Paquete_Precio"
    precio=db.Column(db.Float,nullable=False)
    id_paquete=db.Column(db.ForeignKey('Paquete.id_paquete'),nullable=False,primary_key=True)
class Detalle(db.Model):
    __tablename__="Detalle"
    cantidad=db.Column(db.Integer,nullable=False)
    descripcion=db.Column(db.Integer)
    id_factura=db.Column(db.ForeignKey('Factura.id_factura'),nullable=False,primary_key=True)
    id_paquete=db.Column(db.ForeignKey('Paquete.id_paquete'),nullable=False)
class Detalle_subtotal(db.Model):
    subtotal=db.Column(db.Float,nullable=False)
    id_factura=db.Column(db.ForeignKey('Factura.id_factura'),nullable=False,primary_key=True)