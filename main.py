from flask import Flask, escape, request, render_template, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'ShhhhhItsasecret'

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    posts = Blog.query.all()
    users = User.query.distinct(User.username).all()
    return render_template('index.html', posts=posts, page_title="Home", ids=id, users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    posts = Blog.query.all()
    # idnumber = request.args.get()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<string:id>', methods=['POST', 'GET'])
def individ(id):
    posts = Blog.query.all()
    new_id = Blog.id
    blog_id = Blog.query.filter_by(id=id).first()
    return render_template('entry.html', posts=posts, blog_id=blog_id)

@app.route('/newpost', methods=['POST', 'GET'])
def add():
    posts = Blog.query.all()
    form_value = request.args.get('id')
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        new_post = Blog(new_title, new_body, owner)

        if new_title == "":
            new_body = request.form['body']
            flash("Please enter a title")
            return render_template('newpost.html', page_title="Add a New Entry", post=new_body)

        if new_body == "":
            new_title = request.form['title']
            flash("Please enter a body for the message")
            return render_template('newpost.html', page_title="Add a New Entry", title=new_title)   
        if new_title != "" and new_body != "":
            db.session.add(new_post)
            db.session.commit()
        
        new_id = new_post
        id=new_id.id
        redirection = "/blog/"+str(id)
        return redirect(redirection)
        # paramater = "/blog?id=" + str(new_id.id)
        # # return render_template('individ_entry.html', new_id=new_id)
        # return redirect (paramater)

        if new_id != "Null":
            return render_template('entry.html', posts=posts, id=new_id)
    else:
        return render_template('newpost.html', page_title="Add a New Entry")

@app.route('/singleuser')
def singleuser():
    return render_template("singleuser.html")

@app.route('/singleuser/<string:username>', methods=['POST', 'GET'])
def username(username):
    posts = Blog.query.all()
    users = User.query.all()
    user_id = User.query.filter_by(username=username).first()
    return render_template("singleuser.html", posts=posts, users=users, user_id=user_id)


class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if len(username)<3:
            flash("Username address is too short", 'error')
            return redirect('/signup')
        else:
            if (len(username)>= 3 and len(username) <= 20) and not (" " in username):
                pass
            else:
                flash("Please select a valid username", 'error')
                return redirect('/signup')
        if len(password)>= 3 and len(password) <= 20 and not (" " in password):
            pass
        else:
            flash("Password does not meet requirements", 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if password and confirm_password == password:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                flash("Sorry, passwords don't match", 'error')
                return redirect('/signup')
        else:
            flash("User Name has been used already", 'error')
            return redirect('/signup')

    return render_template('signup.html', page_title = "Sign Up")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in", 'error')
            return redirect('/newpost')
        elif not user:
            flash("Username does not exist", 'error')
            return redirect('/signup')
        elif not check_pw_hash(password, user.pw_hash):
            flash("Password is incorrect")
            return redirect('/login')
        

    return render_template('login.html')

@app.route('/index', methods=['POST', 'GET'])
def home():
    pass

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if session['username']!="":
        del session['username']
        return redirect ("/blog")
    else:
        return redirect('/blog')
    # return redirect ("/blog")

    pass

if __name__ == '__main__':
    app.run()