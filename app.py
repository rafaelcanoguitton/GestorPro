from flask_login import LoginManager, login_user, current_user,login_required,logout_user
from wtform_fields import *
from models import *
from itsdangerous import URLSafeTimedSerializer
from datetime import date
import qrcode
import os
login = LoginManager(app)
login.init_app(app)
s= URLSafeTimedSerializer('Thisisasecret!')

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA
#ML_01 Y ML_02
@app.route('/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    reg_form=RegistrationForm()
    log_form=LoginForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password= reg_form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        email=reg_form.email.data
        #Añade usuario a la BD
        user=User(usuario=username, contraseña=hashed_pswd,email=email)
        db.session.add(user)
        db.session.commit()
        logout_user()
        return redirect(url_for('login'))
    if log_form.validate_on_submit():
        user_object = User.query.filter_by(usuario=log_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('dashboard'))
        
    return render_template("index_true.html",reg_form=reg_form,log_form=log_form)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_01,MC03,MC05
@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if not current_user.is_authenticated:
        return render_template("/Algo-salio-mal.html")
    eventitos=Evento.query.filter(Evento.Usuarios_r.any(id=current_user.id)).all()
    evento_form=EventoForm()
    upe_form=UE()
    if upe_form.validate_on_submit():
        idi=Evento.query.filter(Evento.id_evento==upe_form.id_e.data).first()
        if upe_form.delete.data:
            ev=Evento.query.filter(Evento.id_evento==idi.id_evento).first()
            db.session.delete(ev)
            db.session.commit()
            return redirect(url_for('dashboard'))
        idi.nombre=upe_form.nombre.data
        idi.fecha_inicial=upe_form.fecha_inicial.data
        idi.fecha_final=upe_form.fecha_final.data
        idi.ubicacion=upe_form.ubicacion.data
        idi.descripcion=upe_form.descripcion.data
        db.session.commit()
        return redirect(url_for('dashboard')) 
        
    if evento_form.validate_on_submit():
        nom=evento_form.nombre.data
        fi=evento_form.fecha_inicial.data
        ff=evento_form.fecha_final.data
        ub=evento_form.ubicacion.data
        desc=evento_form.descripcion.data
        
        id_temp=current_user.get_id()
        evento=Evento(nombre=nom, fecha_inicial=fi, fecha_final=ff, ubicacion=ub, descripcion=desc)
        db.session.add(evento)
        db.session.commit()
        current_user.eventos.append(evento)
        db.session.commit()
        return redirect(url_for('dashboard')) 
    return render_template("/dashboard_true.html",ev_form=evento_form,evs=eventitos,up_e=upe_form,nomb=current_user.usuario)
#CERRAR SESIÓN
@app.route('/actividad/<int:id>',methods=['GET','POST'])
def actividad(id):
    actividades = Actividad.query.filter_by(id_evento=id).all()
    idi = Evento.query.filter(Evento.id_evento == id).first()
    return render_template("/actividades.html",act=actividades,nom_pag="Actividades",id_e=id,nom_ev=idi.nombre)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_10
@app.route('/actividad/crear/<int:id_ev>',methods=['GET','POST'])
def actividad_c(id_ev):
    if request.method=='POST':
        id_eve=id_ev
        nom = request.form['name']
        desc = request.form['desc']
        fecha_i = request.form['date1']
        hora_i=request.form['hora1']
        fecha_f = request.form['date2']
        hora_f=request.form['hora2']
        actividad=Actividad(nombre=nom,descripcion=desc,fecha_inicio=fecha_i,fecha_fin=fecha_f,id_evento=id_eve,hora_inicio=hora_i,hora_fin=hora_f)
        db.session.add(actividad)
        db.session.commit()
    return redirect(url_for('actividad',id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_12
@app.route('/actividad/modificar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def actividad_m(id,id_eve):
    if request.method=='POST':
        actividad = Actividad.query.filter(Actividad.id_actividad == id).first()
        actividad.nombre = request.form['name']
        actividad.descripcion = request.form['desc']
        actividad.fecha_inicio = request.form['date1']
        actividad.hora_inicio=request.form['hora1']
        actividad.fecha_fin = request.form['date2']
        actividad.hora_fin=request.form['hora2']
        db.session.commit()
    return redirect(url_for('actividad',id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_**
@app.route('/actividad/eliminar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def actividad_e(id,id_eve):
    actividad = Actividad.query.filter(Actividad.id_actividad == id).first()
    db.session.delete(actividad)
    db.session.commit()
    return redirect(url_for('actividad', id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_-CU07
@app.route('/ambiente/<int:id>',methods=['GET','POST'])
def ambiente(id):
    ambientes=Ambiente.query.filter(Ambiente.Eventos.any(id_evento=id)).all()
    actividades = Actividad.query.filter_by(id_evento=id).all()
    idi = Evento.query.filter(Evento.id_evento == id).first()
    return render_template("/ambientes.html",amb=ambientes,nom_ev=idi.nombre,act=actividades,id_e=idi.id_evento)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_06
@app.route('/ambiente/crear/<int:id>',methods=['GET','POST'])
def ambiente_c(id):
    if request.method=='POST':
        nom = request.form['name']
        cap = request.form['capa']
        desc = request.form['desc']
        lat = request.form['lat']
        long = request.form['long']
        amb = Ambiente(nombre=nom,capacidad=cap,descripcion=desc,latitud=lat,longitud=long)
        db.session.add(amb)
        db.session.commit()
        evento=Evento.query.filter(Evento.id_evento==id).first()
        amb.Eventos.append(evento)
        db.session.commit()
    return redirect(url_for('ambiente',id=id))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_08
@app.route('/ambiente/modificar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def ambiente_m(id,id_eve):
    if request.method=='POST':
        ambi = Ambiente.query.filter(Ambiente.id_ambiente == id).first()
        ambi.nombre=request.form['name']
        ambi.cap=request.form['cap']
        ambi.desc=request.form['desc']
        ambi.lat=request.form['lati']
        ambi.long=request.form['longi']
        db.session.commit()
    return redirect(url_for('ambiente',id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_08
@app.route('/ambiente/asignar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def ambiente_a(id,id_eve):
    if request.method=='POST':
        ambi = Ambiente.query.filter(Ambiente.id_ambiente == id).first()
        acti_id = request.form['select']
        activ = Actividad.query.filter(Actividad.id_actividad == acti_id).first()
        ambi.Actividades.append(activ)
        db.session.commit()
    return redirect(url_for('ambiente', id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_09
@app.route('/ambiente/eliminar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def ambiente_e(id,id_eve):
    ambiente = Ambiente.query.filter(Ambiente.id_ambiente == id).first()
    db.session.delete(ambiente)
    db.session.commit()
    return redirect(url_for('actividad', id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_17
@app.route('/material/<int:id>',methods=['GET','POST'])
def material(id):
    materiales=Material.query.filter(Material.Eventos.any(id_evento=id)).all()
    ambientes = Ambiente.query.filter(Ambiente.Eventos.any(id_evento=id)).all()
    idi = Evento.query.filter(Evento.id_evento == id).first()
    return render_template("/materiales.html",mat=materiales,nom_ev=idi.nombre,ambi=ambientes,id_e=idi.id_evento)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_14
@app.route('/material/crear/<int:id>',methods=['GET','POST'])
def material_c(id):
    if request.method=='POST':
        nom = request.form['name']
        st = request.form['capa']
        desc = request.form['desc']
        amb = Material(nombre=nom,stock=st,descripcion=desc)
        db.session.add(amb)
        db.session.commit()
        evento=Evento.query.filter(Evento.id_evento==id).first()
        amb.Eventos.append(evento)
        db.session.commit()
    return redirect(url_for('material',id=id))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_15
@app.route('/material/modificar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def material_m(id,id_eve):
    if request.method=='POST':
        mati = Ambiente.query.filter(Ambiente.id_ambiente == id).first()
        mati.nombre=request.form['name']
        mati.stock=request.form['cap']
        mati.desc=request.form['desc']
        db.session.commit()
    return redirect(url_for('material',id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_15
@app.route('/material/asignar/<int:id>/<int:id_eve>',methods=['GET','POST'])
def material_a(id,id_eve):
    if request.method=='POST':
        acti = Actividad.query.filter(Actividad.id_actividad == id).first()
        mati_id = request.form['select']
        materi = Material.query.filter(Material.id_material == mati_id).first()
        materi.Ambientes.append(acti)
        db.session.commit()
    return redirect(url_for('material', id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_16
@app.route('/material/eliminar/<int:id>/<int:id_eve>',methods=['GET','POST'])

def material_e(id,id_eve):
    material = Material.query.filter(Material.id_material == id).first()
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('actividad', id=id_eve))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#LOGOUT
@app.route("/logout",methods=['GET'])
def logout():
    logout_user()
    flash('Sesion terminada', 'success')
    return redirect(url_for('login'))
@app.route('/roles', methods=['GET','POST'])
def send_mail():
    eventitos = Evento.query.filter(Evento.Usuarios_r.any(id=current_user.id)).all()
    if request.method== 'GET':
        return render_template("/Permisos_de_acceso_true.html",evs=eventitos,nom_pag="Permisos de acceso")
    email=request.form['email']
    evento=request.form['select']
    eventotk=s.dumps(evento,salt='evento-confirm')
    token=s.dumps(email,salt='email-confirm')
    msg = Message('Usted ha sido invitado para colaborar en un evento!', sender='rafael.cano@ucsp.edu.pe',recipients=[email])
    if(bool(User.query.filter_by(email=email).first())):
        link = url_for('confirm_mail', token=token, eventotk=eventotk, _external=True)
        msg.body = "Su enlace es {}".format(link)
        mail.send(msg)
    else:
        link = url_for('reg_ev', token=token, eventotk=eventotk, _external=True)
        msg.body = "Su enlace es {}".format(link)
        mail.send(msg)
    return render_template("/Permisos_de_acceso_true.html",evs=eventitos,nomb=current_user.usuario)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MG_04 Y #MG_05
@app.route('/confirm_email/<token>/<eventotk>')
def confirm_mail(token,eventotk):
    email=s.loads(token,salt='email-confirm',max_age=3600)
    idi=s.loads(eventotk,salt='evento-confirm',max_age=3600)
    ev=Evento.query.filter(Evento.id_evento==idi).one()
    us=User.query.filter_by(email=email).first()
    us.eventos.append(ev)
    db.session.commit()
    return render_template("/Felicidades.html",nom=ev.nombre)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_04 Y #MG_05
@app.route('/registro/<token>/<eventotk>',methods=['GET','POST'])
def reg_ev(token,eventotk):
    email = s.loads(token, salt='email-confirm', max_age=3600)
    idi = s.loads(eventotk, salt='evento-confirm', max_age=3600)
    if request.method=='GET':
        return render_template("/onlyregister.html",correo=email)
    ev = Evento.query.filter(Evento.id_evento == idi).one()
    username = request.form['username']
    password = request.form['password']
    hashed_pswd = pbkdf2_sha256.hash(password)
    # Añade usuario a la BD
    user = User(usuario=username, contraseña=hashed_pswd, email=email)
    user.eventos.append(ev)
    db.session.add(user)
    db.session.commit()
    return render_template("/Felicidades.html",nom=ev.nombre)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MG_06
@app.route('/crear_paquete')
def crear_p():
    eventitos=Evento.query.filter(Evento.Usuarios_r.any(id=current_user.id)).all()
    return render_template("/crear_paquete.html",evs=eventitos)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_06
@app.route('/crear_paquete/<int:id>')
def crear_p_e(id):
    evento=Evento.query.filter(Evento.id_evento==id).first()
    actividades = Actividad.query.filter_by(id_evento=id).all()
    return render_template("/crear_paqu_id.html",ev=evento,act=actividades)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MC_06
@app.route('/crear_paq/<int:id>',methods=['GET','POST'])
def crear_p_f(id):
    if request.method=='POST':
        nombre = request.form['name']
        tipo = request.form['tipo']
        precio = request.form['precio']
        actividades = request.form.getlist('mycheckbox')
        paq = Paquete(nombre=nombre, id_evento=id)
        db.session.add(paq)
        db.session.commit()
        for i in actividades:
            acti=Actividad.query.filter(Actividad.id_actividad == i).first()
            paq.Actividades.append(acti)
        db.session.add(paq)
        db.session.commit()
        paqui=Paquete_Tipo_Participante_Precio(tipo_participante=tipo,precio=precio,id_paquete=paq.id_paquete)
        db.session.add(paqui)
        db.session.commit()
        return redirect(url_for('crear_p'))
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_01
@app.route('/preinscripcion/<int:id_evento>')
def preinscri(id_evento):
    evento=Evento.query.filter(Evento.id_evento==id_evento).first()
    paquetes=Paquete.query.filter(Paquete.id_evento==id_evento).all()
    return render_template("/Pre-Inscripcion.html",ev=evento,paqs=paquetes)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_01
@app.route('/preins/<int:id_paquete>')
def preins(id_paquete):
    paquete=Paquete.query.filter(Paquete.id_paquete==id_paquete).first()
    paquis=Paquete_Tipo_Participante_Precio.query.filter(Paquete_Tipo_Participante_Precio.id_paquete==id_paquete).all()
    return render_template("/Pre-ins.html",tipos=paquis,nom=paquete.nombre)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_01
@app.route('/preinscribir/',methods=['GET','POST'])
def preinsc():
    if request.method=='POST':
        nombre=request.form['nombre']
        corre=request.form['correo']
        tipo=request.form['gridRadios']
        partici=Participante(nombre=nombre,correo=corre,tipo_participante=tipo)
        db.session.add(partici)
        db.session.commit()
        return render_template("/felicidadesins.html",dato="preinscrito")
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/inscripcion/<int:id_evento>',methods=['GET','POST'])
def inscri(id_evento):
    evento = Evento.query.filter(Evento.id_evento == id_evento).first()
    paquetes = Paquete.query.filter(Paquete.id_evento == id_evento).all()
    return render_template("/Inscripcion.html", ev=evento, paqs=paquetes)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/ins/<int:id_paquete>')
def ins(id_paquete):
    paquete=Paquete.query.filter(Paquete.id_paquete==id_paquete).first()
    paquis=Paquete_Tipo_Participante_Precio.query.filter(Paquete_Tipo_Participante_Precio.id_paquete==id_paquete).all()
    return render_template("/Ins.html",tipos=paquis,nom=paquete.nombre)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/inscribir/',methods=['GET','POST'])
def insc():
    if request.method=='POST':
        nombre=request.form['nombre']
        corre=request.form['correo']
        tipo=request.form['gridRadios']
        participante=Participante(nombre=nombre,correo=corre,tipo_participante=tipo)
        db.session.add(participante)
        db.session.commit()
        tipo = Paquete_Tipo_Participante_Precio.query.filter(
            Paquete_Tipo_Participante_Precio.id_paquete_tipo == participante.tipo_participante).first()
        paq = Paquete.query.filter(Paquete.id_paquete == tipo.id_paquete).first()
        factu = Factura(descuento=0, IVA=0, fecha=date.today(), id_participante=participante.id_participante)
        db.session.add(factu)
        db.session.commit()
        email = participante.correo
        msg = Message('Su factura', sender='rafael.cano@ucsp.edu.pe',
                      recipients=[email])
        msg.html = render_template("/factura_template.html", nombre=participante.nombre, email=participante.correo,
                                   id_factura=factu.id_factura, fecha=factu.fecha, precio=tipo.precio,
                                   tipo=tipo.tipo_participante, paquete=paq.nombre)
        qr = qrcode.make(url_for('asistencia', id_participante=participante.id_participante))
        qr.save('myQR.png')
        with app.open_resource("myQR.png") as fp:
            msg.attach("myQR.png", "image/png", fp.read())
        mail.send(msg)
        os.remove("myQR.png")
        return render_template("/felicidadesins.html",dato="inscrito")
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/yamepreinscribi',methods=['GET','POST'])
def yame():
    return render_template("yame.html")
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/buscar',methods=['GET','POST'])
def buscar():
    if request.method=='POST':
        corre=request.form['name']
        if(bool(Participante.query.filter(Participante.correo==corre).first())):
            parti=Participante.query.filter_by(correo=corre).first()
            return redirect(url_for('pagar',id=parti.id_participante))
        else:
            return render_template("No_hay.html")
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/realizar_pago/<int:id>',methods=['GET','POST'])
def pagar(id):
    return render_template("/pagar.html",id=id)
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MI_03, #MI_04 Y #MI_05
@app.route('/finalizar/<int:id>',methods=['GET','POST'])
def mandar_todo(id):
    participante = Participante.query.filter(Participante.id_participante == id).first()
    tipo = Paquete_Tipo_Participante_Precio.query.filter(
        Paquete_Tipo_Participante_Precio.id_paquete_tipo == participante.tipo_participante).first()
    paq = Paquete.query.filter(Paquete.id_paquete == tipo.id_paquete).first()
    factu = Factura(descuento=0, IVA=0, fecha=date.today(), id_participante=participante.id_participante)
    db.session.add(factu)
    db.session.commit()
    email = participante.correo
    msg = Message('Su factura', sender='rafael.cano@ucsp.edu.pe',
                  recipients=[email])
    msg.html = render_template("/factura_template.html", nombre=participante.nombre, email=participante.correo,
                             id_factura=factu.id_factura, fecha=factu.fecha, precio=tipo.precio,
                             tipo=tipo.tipo_participante, paquete=paq.nombre)
    qr = qrcode.make(url_for('asistencia', id_participante=participante.id_participante))
    qr.save('myQR.png')
    with app.open_resource("myQR.png") as fp:
        msg.attach("myQR.png", "image/png", fp.read())
    mail.send(msg)
    os.remove("myQR.png")
    return render_template("/felicidadesins.html",dato="inscrito")
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#MA_01, #MA_02 Y #MA_03
@app.route('/asistencia/<int:id_participante>')
def asistencia(id_participante):
    return "to-do"
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA:
#ENLACES__
@app.route('/enlaces/<int:id>')
def links(id):
    email=current_user.email
    msg = Message('Enlace inscripción!', sender='rafael.cano@ucsp.edu.pe',
                  recipients=[email])
    link = url_for('inscri',id_evento=id, _external=True)
    msg.body = "Su enlace es {}".format(link)
    mail.send(msg)
    msg2 = Message('Enlace preinscripción!', sender='rafael.cano@ucsp.edu.pe',
                  recipients=[email])
    link2 = url_for('preinscri', id_evento=id, _external=True)
    msg2.body = "Su enlace es {}".format(link)
    mail.send(msg2)
    return redirect(url_for('dashboard'))