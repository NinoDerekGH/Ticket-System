from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/ticketing_db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/user', methods=['POST'])
def create_user():
   
    user = User(username='junzel gwapo', email='juzn@example.com')
    db.session.add(user)
    db.session.commit()

with app.app_context():
    db.create_all()
    create_user()

    user = User.query.all()
    print(user)