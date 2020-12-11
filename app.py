from flask_login import LoginManager, login_user, current_user,login_required,logout_user
from wtform_fields import *
from models import *
from itsdangerous import URLSafeTimedSerializer


login = LoginManager(app)
login.init_app(app)
s= URLSafeTimedSerializer('Thisisasecret!')
#REQUISITOS IMPLEMENTADOS EN ESTA RUTA
#ML_01 Y ML_02
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/', methods=['GET','POST'])
def login():
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
        #flash('Registrado con éxito! Por favor inicie sesion.','success')
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
        flash('Primero inicia sesión :D', 'danger')
    eventitos=Evento.query.filter(Evento.Usuarios_r.any(id=current_user.id)).all()

    evento_form=EventoForm()
    upe_form=UE()
    if upe_form.validate_on_submit():
        idi=Evento.query.filter(Evento.id_evento==upe_form.id_e.data).first()
        if upe_form.delete.data:
            ev=Evento.query.filter(Evento.id_evento==idi.id_evento).first()
            db.session.delete(ev)
            db.session.commit()
            print("Dont preocupeis")
            return redirect(url_for('dashboard'))
        #Evento.query.filter_by(id_evento=idi.id_evento).update({"id_evento":upe_form.id_e.data,"nombre":upe_form.nombre.data,"fecha_inicial":idi.fecha_inicial,"fecha_final":idi.fecha_final,"ubicacion":upe_form.ubicacion.data,"descripcion":upe_form.descripcion.data})
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
    return render_template("/dashboard_true.html",ev_form=evento_form,evs=eventitos,up_e=upe_form)
#CERRAR SESIÓN
@app.route('/actividad/<int:id>',methods=['GET','POST'])
def actividad(id):
    actividades = Actividad.query.filter_by(id_actividad=id).all()
    return "actividades de su evento: "+str(id)
@app.route('/ambiente/<int:id>',methods=['GET','POST'])
def ambiente(id):
    return "ambientes de su evento: " +str(id)
@app.route('/material/<int:id>',methods=['GET','POST'])
def material(id):
    return "materiales de su evento: "+str(id)
@app.route("/logout",methods=['GET'])
def logout():
    logout_user()
    flash('Sesion terminada', 'success')
    return redirect(url_for('login'))
@app.route('/roles', methods=['GET','POST'])
def send_mail():
    eventitos = Evento.query.filter(Evento.Usuarios_r.any(id=current_user.id)).all()
    if request.method== 'GET':
        return render_template("/Permisos_de_acceso_true.html",evs=eventitos)
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
    return render_template("/Permisos_de_acceso_true.html",evs=eventitos)
@app.route('/confirm_email/<token>/<eventotk>')
def confirm_mail(token,eventotk):
    email=s.loads(token,salt='email-confirm',max_age=3600)
    idi=s.loads(eventotk,salt='evento-confirm',max_age=3600)
    ev=Evento.query.filter(Evento.id_evento==idi).one()
    us=User.query.filter_by(email=email).first()
    us.eventos.append(ev)
    db.session.commit()
    return render_template("/Felicidades.html",nom=ev.nombre)
@app.route('/registro/<token>/<eventotk>',methods=['GET','POST'])
def reg_ev(token,eventotk):
    if request.method=='GET':
        return render_template("/onlyregister.html")
    email = s.loads(token, salt='email-confirm', max_age=3600)
    idi = s.loads(eventotk, salt='evento-confirm', max_age=3600)
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