from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#Configuracion de la base de datos
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='cliente')
    contrasena_hash = db.Column(db.String(256), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now())


    #MEtodo para establecer la contraseña del usuario, generando un hash seguro y almacenandolo en la base de datos
    def set_contrasena(self, contrasena):
        self.contrasena_hash = generate_password_hash(contrasena)

    def set_password(self, contrasena):
        self.set_contrasena(contrasena)

    #Metodo para verificar la contraseña del usuario comparando el hash almacenado
    def verificar_contrasena(self, contrasena):
        return check_password_hash(self.contrasena_hash, contrasena)

    #Metodo para verificar si el usuario es administrador
    def es_administrador(self):
        return self.rol == 'administrador'
    
    #Metodo para imprimir un objeto de la clase Usuario en formato legible
    def __repr__(self):
        return f'<Usuario {self.nombre}>'   

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    precio_base = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    #Columnas para ProductosFisico
    peso_kg = db.Column(db.Float, nullable=True)
    costo_envio = db.Column(db.Float, nullable=True)

    #Columnas para ProductosDigital
    licencia = db.Column(db.String(100), nullable=True)

    #Columnas para ProductosPerecibles
    dias_para_vencer = db.Column(db.Integer, nullable=True)

    #Columnas que le dice a la base de datos que tipo de producto es, para poder diferenciar entre los distintos tipos de productos
    tipo = db.Column(db.String(50), nullable=False)

    #__mapper permite a SQLAlchemy mapear la clase Producto a las subclases correspondientes según el valor de la columna tipo
    __mapper_args__ = {
        'polymorphic_identity': 'producto',
        'polymorphic_on': tipo
    }

    def precio_final(self):
        return self.precio_base

    def ficha(self):
        return f"Producto: {self.nombre}, Precio: {self.precio_final()}, Stock: {self.stock}, Activo: {self.activo}"

    
    #Metodo para imprimir un objeto de la clase Producto en formato legible
    def __repr__(self):
        return f'<Producto {self.nombre}>'
class ProductoFisico(Producto):
    __mapper_args__ = {"polymorphic_identity": "fisico"}

    def __init__(self, *args, **kwargs):
        costo_envio_por_kg = kwargs.pop('costo_envio_por_kg', None)
        if costo_envio_por_kg is not None:
            kwargs['costo_envio'] = costo_envio_por_kg
        super().__init__(*args, **kwargs)

    def precio_final(self):
        envio = (self.peso_kg or 0) * (self.costo_envio or 0)
        return self.precio_base + envio


class ProductoDigital(Producto):
    __mapper_args__ = {"polymorphic_identity": "digital"}

    MULTIPLICADORES = {
        "personal": 1.0,
        "comercial": 2.5,
        "educativa": 0.6,
    }

    def precio_final(self):
        multiplicador = self.MULTIPLICADORES.get(self.licencia, 1.0)
        return self.precio_base * multiplicador


class ProductoPerecible(Producto):
    __mapper_args__ = {"polymorphic_identity": "perecible"}

    def precio_final(self):
        dias = self.dias_para_vencer
        if dias is None:
            return self.precio_base
        if dias <= 3:
            return self.precio_base * 0.50
        elif dias <= 7:
            return self.precio_base * 0.80
        return self.precio_base