from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
# DATABASE SETTINGS
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@127.0.0.1:3306/ticketing_db'
app.config['SECRET_KEY'] = 'jollyhotdog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

_password = "mysqlapp"

# /DATABASE SETTINGS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(), Length(1, 16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm', message="Password must match")
    ])
    role = SelectField(u'Role', choices=[('admin', 'Admin'), ('user', 'User')])
    # role = StringField('Role', validators=[DataRequired(), Length(1, 16)])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    department_id = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.Date, nullable=False)
    priority  = db.Column(db.Integer, nullable=False)

    

# ------- Log & Reg Form Routes ------- #


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(name=name,username=username,
                        hashed_password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('auth/registration.html', form=form)

@app.route('/registration/post', methods=['POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(name=name,username=username,
                        hashed_password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
    return make_response({'success': 'Sent Successfully'}, 200)
        

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'GET':
        form = LoginForm()
        return render_template('auth/login.html', form=form)
    
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user:
        if bcrypt.check_password_hash(user.hashed_password, password):
            login_user(user)
            if user.role == 'admin':
                print(password)
                return render_template('/admin/tickets.html')
            else:
                return render_template('/user/user.html')
        else:
            return 'You are not authorized to access this page', 403
    else:
        return 'You are not authorized to access this page', 403



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
def initial():
    return redirect(url_for('login'))

@app.route('/getuser')
def userdata():
    results = User.query.all()
    json_res = {}
    for res in results:
        json_res[res.id] = {'id' : res.id, 'name' : res.name, 'username' : res.username, 
        'password' : res.password, 'role': res.role}
    return json_res

@app.route('/user/getdata')
def getdata():
    results = Tickets.query.all()
    json_res = {}
    for res in results:
        
        json_res[res.id] = {'id' : res.id, 'subject' : res.subject, 'content' : res.content,
         'department_id' : res.department_id, 'created_at' : res.created_at, 'priority': res.priority }
    return json_res
def exists(sql, value):
    exist = False
    try: 
        connect = db.connect()
        cursor =  connect.cursor()
        cursor.execute(sql, value)
        
        row = cursor.fetchone()
        if row:
            exist = True
        else:
            pass
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connect.close()
    return exist
    

@app.route('/viewed', methods=['POST'])
def viewed():
    try:
        id = request.form['id']
        connect = db.connect()
        cursor = connect.cursor() 

        if exists("SELECT * FROM ticket_status WHERE ticket_id = %s", id) == False:
            sql = ('INSERT INTO ticket_status (ticket_id, created_at) VALUES (%s, %s);')
            values = (id,datetime.now())
            cursor.execute(sql,values)
            connect.commit()
    except Exception as error:
        print (error)
    finally:
        cursor.close()
        connect.close()
    return ""

@app.route('/admin/update', methods=['POST'])
def update():
    try:
        id = request.form['id']
        archived = request.form['archive']

        connect = db.connect()
        cursor = connect.cursor()

        sql = 'UPDATE tickets SET archived = %s WHERE id = %s;'
        values = (archived, id)
        cursor.execute(sql, values)
        connect.commit()
        cursor.close()
        connect.close()

        return make_response({'success': 'update Successfully'}, 200)
    except Exception as error:
        print(error)

    return ""


@app.route('/user/ticket')
@login_required
def userIndex():
    if current_user.role != 'user':
        return 'You are not authorized to access this page', 403
    return render_template('/user/user.html')
    
@app.route('/user/arcive')
def archiveIndex():
    return render_template('/forms/user/user-archive.html')

@app.route('/user/ticketsend', methods=['POST'])
def sendticket():
    try:
        id = request.form['id']
        subject = request.form['subject']
        content = request.form['content']
        priority = request.form['priority']

        tikcet = Tickets(subject=subject,content=content,department_id= id,created_at= datetime.now(),priority=priority)
        db.session.add(tikcet)
        db.session.commit()

        return make_response({'success': 'Sent Successfully'}, 200)
    except Exception as err:
        print(err)
    return ""


# ------- Sidebar Routes ------- #

@app.route('/admin')
@login_required
def tickets():
    return render_template('admin/tickets.html')


@ app.route('/unassigned')
def unassigned():
    return render_template('admin/unassigned.html')


@ app.route('/pending')
def pending():
    return render_template('admin/pending.html')


@ app.route('/onhold')
def onhold():
    return render_template('admin/onhold.html')


@ app.route('/summary')
def summary():
    return render_template('admin/summary.html')


@ app.route('/archive')
def archive():
    return render_template('admin/archive.html')


@ app.route('/agents')
@login_required
def agents():
    return render_template('admin/agents.html')

@ app.route('/departments')
def departments():
    return render_template('admin/departments.html')

@ app.route('/inbox')
def inbox():
    return render_template('user/user.html')

if __name__ == '__main__':
    app.run(debug=True)
