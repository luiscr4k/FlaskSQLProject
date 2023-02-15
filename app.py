# IMPORTACION DE LIBRERIAS
import pdfkit
from flask import Flask, render_template, request, url_for, flash, make_response
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from sqlalchemy import engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import redirect      
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from estructura import Lista, Pila
from models import Empleado, Departamento, CentroTrabajo, EmpleadoHijos, Usuario, HabilidadEmpleado, EmpHab
from forms import EmpleadoForm, DepartamentoForm, CentroTrabajoForm, EmpleadoHijosForm, LoginForm, RegistroForm, \
    HabilidadEmpleadoForm, AddSkillToEmpleadoForm

#INICIALIZACION DE LA APLICACION
app = Flask(__name__) 
Bootstrap(app) 

#CONFIGURACIONES DE LA BASE DE DATOS

USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'proyecto1'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#llamar al objeto db en sql alchemy
#db = SQLAlchemy
db.init_app(app)
Session = sessionmaker(bind=engine)
session = Session()

#configurar flask-migrate
migrate = Migrate()
migrate.init_app(app, db)

#configuracion de flask_wtf
app.config['SECRET_KEY'] = 'llave secreta'

#Inicializacion de las clases login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def home():
    return render_template('index.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

#funcion de login
@app.route('/login', methods =['GET', 'POST'])
def login():
    loginform = LoginForm()

    if loginform.validate_on_submit():
        usuario = Usuario.query.filter_by(usuario=loginform.usuario.data).first()
        if usuario:
            if check_password_hash(usuario.password, loginform.password.data):
                login_user(usuario, remember=loginform.recuerda.data)
                return redirect(url_for('dashboard'))
        return '<h1>Usuario o contraseña incorrectos</h1>'
    return render_template('login.html', loginform=loginform)


#funcion del registro 
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    registroform = RegistroForm()
    if registroform.validate_on_submit():
        try:
            pass_hasheada = generate_password_hash(registroform.password.data, method='sha256')
            nuevo_usuario=Usuario(usuario=registroform.usuario.data, email=registroform.email.data, password=pass_hasheada)
            app.logger.debug(f'El hash de contraseña es: {pass_hasheada}')
            db.session.add(nuevo_usuario)
            db.session.commit()
            login_user(nuevo_usuario)
            return redirect(url_for('dashboard')), flash('Usuario registrado exitosamente')
        except IntegrityError:
            db.session.rollback()
            return render_template('registro.html', regform=registroform, flash=True)

    return render_template('registro.html', regform=registroform)


#funcion dashboard o panel principal
@app.route('/dashboard')
@login_required
def dashboard():
    
    return render_template('dashboard.html', usuario=current_user.usuario, admin=current_user.admin)

#funcion de cerrar sesion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#funcion para agregar un nuevo empleado
@app.route('/agregar_empleado', methods=['GET', 'POST'])
@app.route('/agregar_empleado.html', methods=['GET', 'POST'])
@login_required
def agregar_empleado():
    Empleados = Empleado()
    db_empleado = Empleado.query.join(Departamento).add_columns(Empleado.rif, Empleado.nombre_empleado,
                                                            Empleado.apellidoP_empleado, Empleado.apellidoM_empleado, Empleado.tlf_movil_emp,
                                                            Empleado.codigo_dep_emp, Empleado.tlf_fijo_emp, Empleado.fecha_ingreso_emp, Empleado.salario, Empleado.num_hijos, Departamento.id,
                                                            Departamento.nombre_dep)
    empleadoForm= EmpleadoForm(obj=Empleados)
    #definicion de estructura de datos Lista
    empleadopila=Pila()
    for empleado in db_empleado:
        empleadopila.apilar(empleado)
    empleado = empleadopila.retornar_datos()
    if request.method == 'POST':
        if empleadoForm.validate_on_submit():
            empleadoForm.populate_obj(Empleados) #Rellena el objeto empleado con los datos del formulario
            #Insertamos el nuevo registro
            db.session.add(Empleados) #Rellena la base de  datos con los datos del objeto Empleado
            db.session.commit()
            db.session.refresh(Empleados)
            return redirect(url_for('agregar_empleado'))
    return render_template('agregar_empleado.html', empleado_form=empleadoForm, empleados=empleado, admin=current_user.admin)

#funcion para agregar un nuevo departamento
@app.route('/agregar_departamento', methods=['GET', 'POST'])
@app.route('/agregar_departamento.html', methods=['GET', 'POST'])
@login_required
def agregar_departamento():
    Departamentos = Departamento()
    db_departamento = Departamento.query.all()
    departamentoForm = DepartamentoForm(obj=Departamentos)
    depto_lista = Lista()
    for departamento in db_departamento:
        depto_lista.agregar_final(departamento)
    departamento = depto_lista.retornar_datos()
    if request.method == 'POST':
        if departamentoForm.validate_on_submit():
            departamentoForm.populate_obj(Departamentos)
            #Insertamos el nuevo registro
            db.session.add(Departamentos)
            db.session.commit()
            return redirect(url_for('agregar_departamento'))
    return render_template('agregar_departamento.html', departamento_form=departamentoForm, departamentos=departamento, admin=current_user.admin)

#funcion para agregar un nuevo centro de trabajo
@app.route('/agregar_centro', methods=['GET', 'POST'])
@app.route('/agregar_centro.html', methods=['GET','POST'])
@login_required
def agregar_centro():
    Centro = CentroTrabajo()
    centroForm = CentroTrabajoForm(obj=Centro)
    db_centrotabla= CentroTrabajo.query.all()
    centro_lista = Lista()
    for centro in db_centrotabla:
        centro_lista.agregar_final(centro)
    centro = centro_lista.retornar_datos()
    if request.method == 'POST':
        if centroForm.validate_on_submit():
            centroForm.populate_obj(Centro)
            db.session.add(Centro)
            db.session.commit()
            return redirect(url_for('agregar_centro'))
    return render_template('agregar_centro.html', centro_form=centroForm, centrotrabajo=centro, admin=current_user.admin)

#funcion para agregar un nuevo hijo
@app.route('/agregar_hijo', methods=['GET', 'POST'])
@app.route('/agregar_hijo.html', methods=['GET','POST'])
@login_required
def agregar_hijo():
    Hijo = EmpleadoHijos()
    hijoForm = EmpleadoHijosForm(obj=Hijo)
    db_hijotabla = Empleado.query.join(EmpleadoHijos).add_columns(EmpleadoHijos.codigohijo, Empleado.rif, Empleado.nombre_empleado, Empleado.apellidoP_empleado, Empleado.apellidoM_empleado, EmpleadoHijos.nombre_hijo,
                                                                EmpleadoHijos.apellidoP_hijo, EmpleadoHijos.apellidoM_hijo, EmpleadoHijos.fecha_nacimiento)
    hijo_lista = Pila()
    for hijo in db_hijotabla:
        hijo_lista.apilar(hijo)
    hijo = hijo_lista.retornar_datos()
    if request.method == 'POST':
        if hijoForm.validate_on_submit():
            hijoForm.populate_obj(Hijo)
            db.session.add(Hijo)
            db.session.commit()
            app.logger.debug(f'{Hijo} agregado')
            return redirect(url_for('agregar_hijo'))
    return render_template('agregar_hijo.html', hijo_form=hijoForm, hijotabla=hijo, admin=current_user.admin)

@app.route('/agregar_habilidad', methods=['GET','POST'])
@app.route('/agregar_habilidad.html', methods=['GET','POST'])
@login_required
def agregar_habilidad():
    Habilidad = HabilidadEmpleado()
    emphab = EmpHab()
    emphabForm = AddSkillToEmpleadoForm(obj=emphab)
    habilidadForm = HabilidadEmpleadoForm(obj=Habilidad)
    db_tabla_habilidad = HabilidadEmpleado.query
    tabla_emphab = EmpHab.query.join(Empleado,HabilidadEmpleado).add_columns(EmpHab.empleado_rif,
                                                                                Empleado.nombre_empleado, Empleado.apellidoP_empleado,
                                                                                Empleado.apellidoM_empleado, HabilidadEmpleado.codigohabilidad,
                                                                                HabilidadEmpleado.descripcion, EmpHab.id_emphab).filter(Empleado.rif == EmpHab.empleado_rif).filter(HabilidadEmpleado.codigohabilidad == EmpHab.habilidad_id)
    habilidad_lista= Lista()
    for habilidad in db_tabla_habilidad:
        habilidad_lista.agregar_final(habilidad)
    habilidad = habilidad_lista.retornar_datos()
    if request.method == 'POST':
        if habilidadForm.validate_on_submit():
            habilidadForm.populate_obj(Habilidad)
            db.session.add(Habilidad)
            db.session.commit()
            return redirect(url_for('agregar_habilidad'))
        if emphabForm.validate_on_submit():
            emphabForm.populate_obj(emphab)
            db.session.add(emphab)
            db.session.commit()
            return redirect(url_for('agregar_habilidad'))
    return render_template('agregar_habilidad.html', hab_form=habilidadForm, tabla_habilidades=db_tabla_habilidad,
                           emp_form=emphabForm, tabla_emphab=tabla_emphab, admin=current_user.admin)

#funcion para editar un empleado
@app.route('/editar_empleado/<rif>', methods=['GET', 'POST'])
@login_required
def editar(rif):
    #Recuperamos el objeto persona a editar
    empleado = Empleado.query.get_or_404(rif)
    empleadoforma = EmpleadoForm(obj=empleado)
    emptabla= Empleado.query.join(Departamento).add_columns(Empleado.rif, Empleado.nombre_empleado,
                                                            Empleado.apellidoP_empleado, Empleado.tlf_movil_emp,
                                                            Empleado.codigo_dep_emp, Departamento.id,
                                                            Departamento.nombre_dep).filter(Departamento.id == Empleado.codigo_dep_emp)
    if request.method == 'POST':
        if empleadoforma.validate_on_submit():
            empleadoforma.populate_obj(empleado)
            db.session.commit()
            return redirect(url_for('agregar_empleado'))
    return render_template('agregar_empleado.html', empleado_form=empleadoforma, empleados=emptabla, admin=current_user.admin)

#funcion para editar un departamento
@app.route('/editar_departamento/<int:id>', methods = ['GET', 'POST'])
@login_required
def editar_departamento(id):
    departamento = Departamento.query.get_or_404(id)
    departamentoforma = DepartamentoForm(obj=departamento)
    deptabla = Departamento.query.all()
    if request.method == 'POST':
        if departamentoforma.validate_on_submit():
            departamentoforma.populate_obj(departamento)
            db.session.commit()
            return redirect(url_for('agregar_departamento'))
    return render_template('agregar_departamento.html', departamento_form=departamentoforma, departamentos=deptabla, admin=current_user.admin)

#funcion para editar un centro de trabajo
@app.route('/editar_centro/<int:id_centro>', methods = ['GET', 'POST'])
@login_required
def editar_centrotrabajo(id_centro):
    centrotrabajo = CentroTrabajo.query.get_or_404(id_centro)
    centroforma = CentroTrabajoForm(obj=centrotrabajo)
    centrotabla = CentroTrabajo.query.all()
    if request.method == 'POST':
        if centroforma.validate_on_submit():
            centroforma.populate_obj(centrotrabajo)
            app.logger.debug(f'Editar centro de trabajo: ')
            db.session.commit()
            return redirect(url_for('agregar_centro'))
    return render_template('agregar_centro.html', centro_form=centroforma, centrotrabajo=centrotabla, admin=current_user.admin)

#funcion para editar un hijo
@app.route('/editar_hijo/<int:codigohijo>', methods = ['GET', 'POST'])
@login_required
def editar_hijo(codigohijo):
    hijo = EmpleadoHijos.query.get_or_404(codigohijo)
    hijoforma = EmpleadoHijosForm(obj=hijo)
    db_hijotabla = Empleado.query.join(EmpleadoHijos).add_columns(EmpleadoHijos.codigohijo, Empleado.rif,
                                                                  Empleado.nombre_empleado, Empleado.apellidoP_empleado,
                                                                  Empleado.apellidoM_empleado,
                                                                  EmpleadoHijos.nombre_hijo,
                                                                  EmpleadoHijos.apellidoP_hijo,
                                                                  EmpleadoHijos.apellidoM_hijo,
                                                                  EmpleadoHijos.fecha_nacimiento)
    hijo_lista = Pila()
    for hijo in db_hijotabla:
        hijo_lista.apilar(hijo)
    hijo = hijo_lista.retornar_datos()
    if request.method == 'POST':
        if hijoforma.validate_on_submit():
            hijoforma.populate_obj(hijo)
            app.logger.debug(f'Editar datos del hijo: ')
            db.session.commit()
            return redirect(url_for('agregar_hijo'))
    return render_template('agregar_hijo.html', hijo_form=hijoforma, hijotabla=hijo, admin=current_user.admin)


@app.route('/editar_habilidad/<int:codigohabilidad>', methods=['GET','POST'])
@login_required
def editar_habilidad(codigohabilidad):
    habilidad = HabilidadEmpleado.query.get_or_404(codigohabilidad)
    habilidadforma = HabilidadEmpleadoForm(obj=habilidad)
    tabla_habilidad = HabilidadEmpleado.query.all()
    emphab = EmpHab()
    emphabForm = AddSkillToEmpleadoForm(obj=emphab)
    tabla_emphab = EmpHab.query.join(Empleado,HabilidadEmpleado).add_columns(EmpHab.empleado_rif,
                                                                                Empleado.nombre_empleado, Empleado.apellidoP_empleado,
                                                                                Empleado.apellidoM_empleado, HabilidadEmpleado.codigohabilidad,
                                                                                HabilidadEmpleado.descripcion, EmpHab.id_emphab).filter(Empleado.rif == EmpHab.empleado_rif).filter(HabilidadEmpleado.codigohabilidad == EmpHab.habilidad_id)

    if request.method == 'POST':
        if habilidadforma.validate_on_submit():
            habilidadforma.populate_obj(habilidad)
            db.session.add(habilidad)
            db.session.commit()
            return redirect(url_for('agregar_habilidad'))
        if emphabForm.validate_on_submit():
            emphabForm.populate_obj(emphab)
            db.session.add(emphab)
            db.session.commit()
            return redirect(url_for('agregar_habilidad'))
    return render_template('agregar_habilidad.html', hab_form=habilidadforma, tabla_habilidades=tabla_habilidad,
                           tabla_emphab=tabla_emphab, emp_form=emphabForm, admin=current_user.admin)


@app.route('/editar_habilidad_emp/<int:id_emphab>', methods=['GET','POST'])
@login_required
def editar_habilidad_empleado(id_emphab):
    emphab = EmpHab.query.get_or_404(id_emphab)
    emphabForma = AddSkillToEmpleadoForm(obj=id_emphab)
    habilidad = HabilidadEmpleado()
    HabilidadForm = HabilidadEmpleadoForm(obj=habilidad)
    tabla_habilidad = HabilidadEmpleado.query.all()
    tabla_emphab = EmpHab.query.join(Empleado,HabilidadEmpleado).add_columns(EmpHab.empleado_rif,
                                                                                Empleado.nombre_empleado, Empleado.apellidoP_empleado,
                                                                                Empleado.apellidoM_empleado, HabilidadEmpleado.codigohabilidad,
                                                                                HabilidadEmpleado.descripcion, EmpHab.id_emphab).filter(Empleado.rif == EmpHab.empleado_rif).filter(HabilidadEmpleado.codigohabilidad == EmpHab.habilidad_id)
    if request.method == 'POST':
        if emphabForma.validate_on_submit():
            emphabForma.populate_obj(emphab)
            db.session.add(emphab)
            db.session.commit()
            return(redirect(url_for('agregar_habilidad')))
        if HabilidadForm.validate_on_submit():
            HabilidadForm.populate_obj(habilidad)
            db.session.add(habilidad)
            db.session.commit()
            return redirect(url_for('agregar_habilidad'))
    return render_template('agregar_habilidad.html', hab_form=HabilidadForm, tabla_habilidades=tabla_habilidad,
                           emp_form=emphabForma, tabla_emphab=tabla_emphab, admin=current_user.admin)

#funcion para eliminar un empleado
@app.route('/eliminar_empleado/<rif>')
@login_required
def eliminar_empleado(rif):
    empleado = Empleado.query.get_or_404(rif)
    db.session.delete(empleado)
    db.session.commit()
    return redirect(url_for('agregar_empleado'))

#funcion para elimninar un departamento
@app.route('/eliminar_departamento/<int:id>')
@login_required
def eliminar_departamento(id):
    departamento = Departamento.query.get_or_404(id)
    db.session.delete(departamento)
    db.session.commit()
    return redirect(url_for('agregar_departamento'))

#funcion para eliminar un centro de trabajo
@app.route('/eliminar_centrotrabajo/<int:id_centro>')
@login_required
def eliminar_centro(id_centro):
    centrotrabajo = CentroTrabajo.query.get_or_404(id_centro)
    db.session.delete(centrotrabajo)
    db.session.commit()
    return redirect(url_for('agregar_centro'))

#funcion para eliminar un hijo 
@app.route('/eliminar_hijo/<int:codigohijo>')
@login_required
def eliminar_hijo(codigohijo):
    hijo = EmpleadoHijos.query.get_or_404(codigohijo)
    db.session.delete(hijo)
    db.session.commit()
    return redirect(url_for('agregar_hijo'))

#funcion para eliminar una habilidad
@app.route('/eliminar_habilidad/<int:codigohabilidad>')
@login_required
def eliminar_habilidad(codigohabilidad):
    habilidad = HabilidadEmpleado.query.get_or_404(codigohabilidad)
    db.session.delete(habilidad)
    db.session.commit()
    return redirect(url_for('agregar_habilidad'))

@app.route('/eliminar_habilidad_emp/<int:id_emphab>')
@login_required
def eliminar_habilidad_emp(id_emphab):
    habilidad = EmpHab.query.get_or_404(id_emphab)
    db.session.delete(habilidad)
    db.session.commit()
    return redirect(url_for('agregar_habilidad'))

@app.route('/generar/reporte_empleados')
@login_required
def reporte_empleados():
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    emptabla = Empleado.query.join(Departamento).add_columns(Empleado.rif, Empleado.nombre_empleado,
                                                             Empleado.apellidoP_empleado, Empleado.tlf_movil_emp, Empleado.tlf_fijo_emp,
                                                             Empleado.codigo_dep_emp, Departamento.id,
                                                             Empleado.salario, Empleado.num_hijos, Empleado.fecha_ingreso_emp,
                                                             Departamento.nombre_dep).filter(Departamento.id == Empleado.codigo_dep_emp)
    res = render_template('empleadospdf.html', empleados=emptabla)
    respstring=pdfkit.from_string(res,configuration=config)
    respuesta=make_response(respstring)
    respuesta.headers['Content-Type']='application/pdf'
    respuesta.headers['Content-Disposition']='inline;filename=empleados.pdf'
    return respuesta

@app.route('/generar/reporte_departamentos/')
@login_required
def reporte_departamentos():
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    dep_tabla= Departamento.query.join(CentroTrabajo).add_columns(Departamento.id, Departamento.nombre_dep,
                                                                 Departamento.codigo_centro, Departamento.presupuesto_anual,
                                                                 CentroTrabajo.id_centro, CentroTrabajo.ciudad_centro,
                                                                 CentroTrabajo.poblacion_centro, CentroTrabajo.calle_av, CentroTrabajo.estado_centro).filter(Departamento.codigo_centro == CentroTrabajo.id_centro)
    res = render_template('departamentospdf.html', departamentos=dep_tabla)
    respstring=pdfkit.from_string(res,configuration=config)
    respuesta=make_response(respstring)
    respuesta.headers['Content-Type']='application/pdf'
    respuesta.headers['Content-Disposition']='inline;filename=departamentos.pdf'
    return respuesta

@app.route('/generar/reporte_habilidades/')
def reporte_habilidades():
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    hab_tabla= EmpHab.query.join(Empleado,HabilidadEmpleado).add_columns(EmpHab.empleado_rif,
                                                                                Empleado.nombre_empleado, Empleado.apellidoP_empleado,
                                                                                Empleado.apellidoM_empleado, HabilidadEmpleado.codigohabilidad,
                                                                                HabilidadEmpleado.descripcion, EmpHab.id_emphab).filter(Empleado.rif == EmpHab.empleado_rif).filter(HabilidadEmpleado.codigohabilidad == EmpHab.habilidad_id)
    res = render_template('habilidadespdf.html', habilidades=hab_tabla)
    respstring=pdfkit.from_string(res,configuration=config)
    respuesta=make_response(respstring)
    respuesta.headers['Content-Type']='application/pdf'
    respuesta.headers['Content-Disposition']='inline;filename=departamentos.pdf'
    return respuesta

@app.errorhandler(IntegrityError)
def special_exception_handler(error):
    string='Llave duplicada, inserta un codigo unico que no exista'
    return render_template('error.html', error=string), 500

@app.errorhandler(404)
def exception_handler_404(error):
    return render_template('error.html', error=error), 404



