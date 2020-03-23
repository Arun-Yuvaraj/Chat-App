from time import localtime, strftime
from flask import Flask, render_template, redirect, url_for, flash
from wtform_fields import *
from models import *
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send, join_room, leave_room
from aylienapiclient import textapi
import os, json
from flask import g

client = textapi.Client("f0a364af", "f4d755bada030bd03821fd253780111a")


# Configure app
app = Flask(__name__)

app.secret_key = os.environ.get('SECRET')

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 30
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 100

db = SQLAlchemy(app)

#Initialize Flask-SocketIO
socketio = SocketIO(app, manage_session = False)

ROOMS = ["General", "Coding"]
users = []
test = {}

# Configure Flask Login
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/", methods = ["GET","POST"])

def index():

    reg_form = RegistrationForm()
    
    # update database with username and password
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        
        hashed_pswd = pbkdf2_sha256.hash(password)
        
        user = User(username = username, password = hashed_pswd)
        db.session.add(user)
        db.session.commit()
        flash('User successfully Registered', 'success')
        return redirect(url_for('login'))
        
    return render_template("index.html", form = reg_form)
    
@app.route("/login", methods = ["GET","POST"])
def login():
    login_form = LoginForm()
    
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username = login_form.username.data).first()
        login_user(user_object)
        if (user_object.username not in users):
            users.append(user_object.username)
        test['Username'] = users
        return redirect(url_for('chat'))
        
    return render_template("login.html", form = login_form)
    
@app.route("/chat", methods = ["GET","POST"])
def chat():
    if not current_user.is_authenticated:
        flash('Please Login', 'danger')
        return redirect(url_for('login'))
    return render_template('chat.html', username=current_user.username, rooms = ROOMS, users = test)
    
@app.route("/logout", methods = ["GET"])
def logout():
    logout_user()
    flash('You have successfully Logged Out', 'success')
    return redirect(url_for('login'))


@socketio.on('message')
def message(data):
    text = data.get("msg")
    sentiment = client.Sentiment({'text': text})
    text1 = sentiment.get("polarity")
    if (text1 == 'positive'):
        emotion = "\U0001F642"
    elif (text1 == 'negative'):
        emotion = "\U0001F641"
    else:
        emotion = "\U0001F610"
        
    text = text + emotion
    data["msg"] = text
    
    ### send function will broadcast the message from server side to socketio.js's message event
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])
    
@socketio.on('join')
def join(data):

    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room = data['room'])
    
@socketio.on('leave')
def leave(data):

    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room = data['room'])
    
@socketio.on('joinpersonal')
def joinpersonal(data):

    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room = data['room'])
    
@socketio.on('leavepersonal')
def leavepersonal(data):

    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room = data['room'])
    
@socketio.on('send_message')
def handle_source(data):
    socketio.emit('echo', {'username': data['username']}, broadcast = True)

@socketio.on('logout')
def logout(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + "chat"}, room = data['room'])
    


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run()

