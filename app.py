from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'blog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '46294a56a94800907b4ca86a07aa20c8fbe51a8b'

db.init_app(app)

login_manager = LoginManager(app)

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(25), nullable=False)
    confirm_password = db.Column(db.String(25), nullable=False)

    def __repr__(self):

        return f"User {self.username}"



class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

  

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


@app.route('/add_post', methods = ['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
       
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_post.html')

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('home.html')  


@app.route('/about')
def about():
    return render_template('about.html')  



@app.route('/posts', methods = ['POST', 'GET'])
def posts():
    posts = Post.query.all()

    return render_template('posts.html', posts = posts)     


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # confirm_password  = request.form.get('confirm_password')

        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('register'))

        first = User.query.filter_by(first_name=first_name).first()
        if first:
            return redirect(url_for('register'))

        last = User.query.filter_by(last_name=last_name).first()
        if last:
            return redirect(url_for('register'))

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
        
            return redirect(url_for('register'))    

        password_hash = generate_password_hash(password)

        
        
        new_user = User(username=username, email=email, password_hash=password_hash, first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html')  


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

    


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/edit/<int:id>/', methods = ['POST', 'GET'] )
def edit(id):
    update_post = Post.query.get_or_404(id)

    if request.method == 'POST':

        update_post.title = request.form.get('title')
        update_post.content = request.form.get('content')

        db.session.commit()

        return redirect(url_for('home'))   

    return render_template('edit.html', post = update_post)



if __name__ == '__main__':
    app.run(debug=True)
