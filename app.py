from flask import Flask, render_template
from flaskext.mysql import MySQL

app = Flask(__name__, static_folder='static', template_folder='templates')

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'demo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def index():
    return render_template('forms/user.html')

if __name__ == '__main__':
    app.run(debug=True)