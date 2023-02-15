#importacion de librerias
from sqlalchemy.orm import backref
from app import db
from flask_login import UserMixin

#conexion con la bae de datos

#clase modelo usuario  
class Usuario(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(15), unique=True)
    email= db.Column(db.String(50), unique=True)
    admin = db.Column(db.Boolean, default=False)
    password= db.Column(db.String(88))


#clase modelo departamento
class Departamento(db.Model):
    __tablename__ = 'departamento'

    id = db.Column(db.Integer, primary_key=True)
    nombre_dep = db.Column(db.String(40))
    presupuesto_anual = db.Column(db.Integer)
    codigo_centro = db.Column(db.Integer, db.ForeignKey('centrotrabajo.id_centro'))

    #Relaciones de Departamento
    dptoempleado = db.relationship('Empleado', backref=backref("departamento"))

    def __str__(self):
        return(
            f'Id Departamento: {self.id}'
            f'Nombre de departamento: {self.nombre_dep}'
            f'Presupuesto anual: {self.presupuesto_anual}'
            f'Codigo de centro: {self.codigo_centro}'
        )

#clase modelo centro de trabajo
class CentroTrabajo(db.Model):
    __tablename__ = 'centrotrabajo'

    id_centro = db.Column(db.Integer, primary_key=True)
    calle_av = db.Column(db.String(60))
    ciudad_centro= db.Column(db.String(60))
    estado_centro = db.Column(db.String(60))
    poblacion_centro = db.Column(db.Integer)

#Llaves foraneas de codigo departamento y codigo jefe
    codigo_jefe = db.Column(db.String(20), db.ForeignKey('empleado.rif'))
    centroempleado = db.relationship('Empleado', backref=backref("centrotrabajo"))

    def __str__(self):
        return(
            f'Id del centro: {self.id_centro}'
            f'Calle y/o avenida:{self.calle_av}'
            f'Ciudad:{self.ciudad_centro}'
            f'Estado:{self.estado_centro}'
            f'Poblacion del centro: {self.poblacion_centro}'
            f'Codigo jefe: {self.codigo_jefe}'
        )

#clase modelo hijos de empleados
class EmpleadoHijos(db.Model):
    __tablename__ = 'empleadohijos'

    codigohijo = db.Column(db.Integer, primary_key=True)
    nombre_hijo = db.Column(db.String(60))
    apellidoP_hijo = db.Column(db.String(60))
    apellidoM_hijo = db.Column(db.String(60))
    fecha_nacimiento = db.Column(db.Date)
    empleado_padre = db.Column(db.String(20), db.ForeignKey('empleado.rif'))

    def __str__(self):
        return(
            f'ID: {self.codigohijo}'
            f'Nombre: {self.nombre_hijo}'
            f'Apellidos : {self.apellidoP_hijo+self.apellidoM_hijo}'
            f'Fecha nacimiento: {self.fecha_nacimiento}'
            f'Padre: {self.empleado_padre}'
        )

#clase modelo habilidades de  empleado
class HabilidadEmpleado(db.Model):
    __tablename__ = 'habilidadempleado'

    codigohabilidad = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(120))
    habilidades = db.relationship('EmpHab', backref=backref("habilidadempleado", cascade="all,delete"))

    def __str__(self):
        return(
            f'Codigo Habilidad: {self.codigohabilidad}'
            f'Descripcion: {self.descripcion}'
        )

#clase modelo  habilidad empleado 
class EmpHab(db.Model):
    __tablename__ = 'habilidades_empleados'

    id_emphab = db.Column(db.Integer, primary_key=True)
    empleado_rif = db.Column(db.String(20), db.ForeignKey('empleado.rif'))
    habilidad_id = db.Column(db.Integer, db.ForeignKey('habilidadempleado.codigohabilidad'))

#clase modelo empleado
class Empleado(db.Model):
    __tablename__ = 'empleado'

    rif = db.Column(db.String(20), primary_key=True)
    fecha_ingreso_emp = db.Column(db.Date)
    nombre_empleado = db.Column(db.String(60))
    apellidoP_empleado = db.Column(db.String(60))
    apellidoM_empleado = db.Column(db.String(60))
    tlf_movil_emp = db.Column(db.String(32))
    tlf_fijo_emp = db.Column(db.String(32))
    num_hijos = db.Column(db.Integer)
    salario = db.Column(db.Numeric)

#Creacion llaves foraneas para relaciones con otras tablas
    codigo_dep_emp = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    
    #Creacion relacion con centro trabajo
    codigo_hijos = db.relationship('EmpleadoHijos', backref=backref("empleado", cascade="all,delete"))
    codigo_jefe = db.relationship('CentroTrabajo', backref=backref("empleado"), overlaps="centroempleado,centrotrabajo" )
    habilidades = db.relationship('EmpHab', backref=backref("empleado"))

    def __str__(self):
        return(
            f'RIF: {self.rif}'
            f'Fecha Ingreso: {self.fecha_ingreso_emp}'
            f'Nombre: {self.nombre_empleado}'
            f'Apellidos: {self.apellidoP_empleado+self.apellidoM_empleado}'
            f'TLF Movil: {self.tlf_movil_emp}'
            f'TLF Fijo: {self.tlf_fijo_emp}'
            f'Num Hijos: {self.num_hijos}'
            f'Salario: {self.salario}'
            f'Codigo Departamento Emp: {self.codigo_dep_emp}'
            f'Codigo Hijos Emp: {self.codigo_hijos}'
        )