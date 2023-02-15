#importacion de librerias 

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, DecimalField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, DataRequired, Email, Optional


#creacion de clases

#clase formulario login 
class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[InputRequired(), Length(min=4, max=15)], render_kw={"placeholder":'Ingresa tu usuario'} )
    password = PasswordField('Contraseña', validators=[InputRequired(), Length(min=8, max=88)], render_kw={"placeholder":'Ingresa tu contraseña'})
    recuerda = BooleanField('Recuerdame')

#clase registro login 
class RegistroForm(FlaskForm):
    usuario = StringField('Usuario', validators=[InputRequired(), Length(min=4, max=15)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Correo invalido'), Length(max=50)])
    password = PasswordField('Contraseña', validators=[InputRequired(), Length(min=8, max=88)])

#clase formulario empleado 
class EmpleadoForm(FlaskForm):
    rif = StringField('RIF', validators=[DataRequired()], render_kw={"placeholder":'V- o J-'})
    fecha_ingreso_emp = DateField('Fecha Ingreso', validators=[DataRequired()])
    nombre_empleado = StringField('Nombre', validators=[DataRequired()])
    apellidoP_empleado = StringField('Apellido paterno', validators=[DataRequired()])
    apellidoM_empleado = StringField('Apellido materno', validators=[Optional()])
    tlf_movil_emp = IntegerField('Telefono Movil', validators=[DataRequired()])
    tlf_fijo_emp = IntegerField('Telefono Fijo', validators=[Optional()])
    num_hijos = IntegerField('Numero de hijos', validators=[Optional()])
    salario = DecimalField('Salario', validators=[DataRequired()])
    codigo_dep_emp = IntegerField('Codigo de Departamento', validators=[Optional()])
    enviar = SubmitField('Enviar datos')

#clase formulario departamento
class DepartamentoForm(FlaskForm):
    nombre_dep = StringField('Nombre: ', validators=[DataRequired()])
    presupuesto_anual = IntegerField('Presupuesto anual', validators=[DataRequired()])
    codigo_centro = IntegerField('Codigo de centro', validators=[Optional()])
    enviar= SubmitField('Enviar datos')

#clase formulario centro de trabajo
class CentroTrabajoForm(FlaskForm):

    calle_av = StringField('Calle y/o avenida', validators=[DataRequired()])
    ciudad_centro= StringField('Ciudad', validators=[DataRequired()])
    estado_centro = StringField('Estado', validators=[DataRequired()])
    poblacion_centro = IntegerField('Poblacion', validators=[Optional()])
    codigo_jefe = StringField('Jefe encargado', validators=[Optional()])
    enviar= SubmitField('Enviar datos')

#clase formulario hijos de empleados
class EmpleadoHijosForm(FlaskForm):
    nombre_hijo = StringField('Nombre',validators=[DataRequired()])
    apellidoP_hijo = StringField('Apellido Padre', validators=[DataRequired()])
    apellidoM_hijo = StringField('Apellido Madre', validators=[DataRequired()])
    fecha_nacimiento= DateField('Fecha de nacimiento ', validators=[DataRequired()])
    empleado_padre = StringField('RIF del padre ', validators=[Optional()])
    enviar= SubmitField('Enviar datos')

#clase formulario habilidad de empleados
class HabilidadEmpleadoForm(FlaskForm):
    descripcion = StringField('Nombre habilidad', validators=[DataRequired()])
    enviar = SubmitField('Enviar datos')

class AddSkillToEmpleadoForm(FlaskForm):
    empleado_rif = StringField('RIF del Empleado', validators=[DataRequired()])
    habilidad_id = IntegerField('Codigo habilidad', validators=[DataRequired()])
    enviar = SubmitField('Enviar datos')