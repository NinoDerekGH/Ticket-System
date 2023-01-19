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

# /DATABASE SETTINGS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
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


# ------- Log & Reg Form Routes ------- #


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username,
                        hashed_password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('auth/registration.html', form=form)


@app.route('/', methods=['GET', 'POST'])
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
                return render_template('/admin/tickets.html')
            else:
                return render_template('/user/user.html')
        else:
            return 'Invalid email or password, please try again.'
    return render_template('admin/agents.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')




@app.route('/user/getdata')
def getdata():
    connect = db.connect()
    cursor = connect.cursor()

    sql = "SELECT * FROM tickets"
    cursor.execute(sql)

    results = cursor.fetchall()
    json_res = {}
    for res in results:
        json_res[res[0]] = dict(
            zip([col[0] for col in cursor.description], res))

    cursor.close()
    connect.close()
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
def userIndex():
    return render_template('/forms/user/user.html')
    
@app.route('/user/arcive')
def archiveIndex():
    return render_template('/forms/user/user-archive.html')

@app.route('/user/ticketsend', methods=['POST'])
def sendticket():
    try:
        id = "2"
        subject = request.form['subject']
        content = request.form['content']

        # Oppen Connection for ticketing_db
        connect = db.connect()
        cursor = connect.cursor()

        sql = 'INSERT INTO tickets (subject, content, department_id, created_at) VALUES (%s, %s,%s, %s);'
        var = (subject, content, id, datetime.now())

        cursor.execute(sql, var)

        connect.commit()
        # Close Current Connection
        cursor.close()
        connect.close()

        return make_response({'success': 'Sent Successfully'}, 200)
    except Exception as err:
        print(err)
    return ""


# ------- Sidebar Routes ------- #

@ app.route('/tickets')
def tickets():
    return render_template('admin/tickets.html')

@ app.route('/agents')
def agents():
    return render_template('admin/agents.html')

@ app.route('/inbox')
def inbox():
    return render_template('user/user.html')


if __name__ == '__main__':
    app.run(debug=True)
