from flask import Flask, render_template, request, make_response, redirect, url_for
from flaskext.mysql import MySQL
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import bcrypt

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from datetime import datetime
import os


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
# DATABASE SETTINGS

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'ticketing_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = 'jollyhotdog'

mysql.init_app(app)
# /DATABASE SETTINGS


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.name = username
        self.password = password
        self.email = email

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password, self.email)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm', message="Password must match")
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = {}".format(user_id))
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

# ------- Log & Reg Form Routes ------- #


@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s",
                       (form.emai.data,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user[3], form.password.data):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('login'))
    return render_template('forms/user.html', form=form)


@app.route('/register')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = mysql.connect()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(form.password.data)
        cursor.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
                       (form.username.data, form.email.data, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        user = User(id=cursor.lastrowid,
                    username=form.username.data, email=form.email.data)
        login_user(user)
        return redirect(url_for('login'))

    return render_template('forms/register.html', form=form)


@app.route('/user/getdata')
def getdata():
    connect = mysql.connect()
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


@app.route('/user/update', methods=['POST'])
def update():
    try:
        id = request.form['id']
        archived = request.form['archive']

        connect = mysql.connect()
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


@app.route('/user/ticketsend', methods=['POST'])
def sendticket():
    try:
        id = "2"
        subject = request.form['subject']
        content = request.form['content']

        # Oppen Connection for ticketing_db
        connect = mysql.connect()
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


# ------- Admin Routes ------- #
@app.route('/admin')
def admin():
    return render_template('/admin/tickets.html')

@app.route('/agents')
def agents():
    return render_template('/admin/agents.html')


if __name__ == '__main__':
    app.run(debug=True)
