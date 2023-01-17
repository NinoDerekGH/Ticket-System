from flask import Flask, render_template, request, make_response
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_login import login_required


from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from datetime import datetime
import os


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
# DATABASE SETTINGS

login_manager = LoginManager()
login_manager.init_app(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'ticketing_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

# DATABASE CONFIG


class User:
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = {}".format(user_id))
    user = cur.fetchone()
    if user:
        return user
    return None


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
@login_required
def index():
    return render_template('forms/user/user.html')


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
    return json_res


@app.route('/user', methods=['POST'])
def send():
    try:
        id = "2"
        subject = request.form['subject']
        content = request.form['content']

        # Oppen Connection for ticketing_db
        connect = mysql.connect()
        cursor = connect.cursor()

        sql = 'INSERT INTO tickets (subject, content, user_id, priority, created_at) VALUES (%s, %s,%s, %s, %s);'
        var = (subject, content, id, "normal", datetime.now())

        cursor.execute(sql, var)
        ticket_id = cursor.lastrowid
        connect.commit()
        # Close Current Connection
        cursor.close()
        connect.close()
        # # print ()
        # filepath  = os.path.join(app.root_path, 'uploads')
        # file = request.files['file']
        # if file:
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join('uploads', filename))
        #     return make_response({'success' : 'Sent Successfully'},200)
        # else:
        #     return "No file found."

        return make_response({'success': 'Sent Successfully'}, 200)
    except Exception as err:
        print(err)
    return ""


@app.route('/unassigned')
def unassigned():
    return render_template('vendor/unassigned.html')


@app.route('/pending')
def pending():
    return render_template('vendor/pending.html')


@app.route('/onhold')
def onhold():
    return render_template('vendor/onhold.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
