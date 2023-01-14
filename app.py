from flask import Flask, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template('forms/user.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/unassigned')
def unassigned():
    return render_template('vendor/unassigned.html')


@app.route('/register')
def register():
    return render_template('register.html')

# @app.route('/user/create', methods=['POST'])
# def create():


if __name__ == '__main__':
    app.run(debug=True)
