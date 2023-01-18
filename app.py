from flask import Flask, render_template, request, make_response
from flaskext.mysql import MySQL

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from datetime import datetime
import os


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
# DATABASE SETTINGS



app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'ticketing_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

# /DATABASE SETTINGS





@app.route('/user/getdata')
def getdata():
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = "SELECT * FROM tickets"
    cursor.execute(sql)

    results = cursor.fetchall()
    json_res = {}
    for res in results:
        json_res[res[0]] = dict(zip([col[0] for col in cursor.description], res))

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
        
        cursor.execute(sql,values)
        connect.commit()

        cursor.close()
        connect.close()
        
        return make_response({'success' : 'update Successfully'},200)
    except Exception as error:
        print (error)

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

        cursor.execute(sql,var)
        
        connect.commit()
        # Close Current Connection
        cursor.close()
        connect.close()
        
        return make_response({'success' : 'Sent Successfully'},200)
    except Exception as err:
        print(err)
    return ""


# ------- Log & Reg Form Routes ------- #
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


# ------- Admin Routes ------- #
@app.route('/admin')
def admin():
    return render_template('admin/index.html')

@app.route('/unassigned')
def unassigned():
    return render_template('admin/unassigned.html')


@app.route('/pending')
def pending():
    return render_template('admin/pending.html')

@app.route('/onhold')
def onhold():
    return render_template('admin/onhold.html')

@app.route('/summary')
def summary():
    return render_template('admin/summary.html')

@app.route('/archive')
def archive():
    return render_template('admin/archive.html')

@app.route('/agents')
def agents():
    return render_template('admin/agents.html')


if __name__ == '__main__':
    app.run(debug=True)
