from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

### MAMP server config ###

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "msdadsfsf2345sf"

### SQL config with mamp ###

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date= datetime.utcnow()
        self.pub_date = pub_date
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(30))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


### does the user need to log in ###

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


### home page ###

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users')


### blog listing page ###

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('singleuser.html', posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('blog_history.html', post=post)

    return render_template('home.html', posts=posts, header='All Blog Posts')

### sign up page ###

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        verify_password = request.form['verify_password']


        registered_usernames = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""


        if password != verify_password or verify_password == "":
            verify_error = "Passwords do not match."

        if len(username) < 3 or len(username) > 20:
            username_error = "Username must be between 3 and 20 characters."
        if len(password) < 3 or len(password) > 20:
            password_error = "Password must be between 3 and 20 characters."

        if registered_usernames:
            username_error = "Username already exists."

        if len(username) >= 3 and len(password) >= 3 and len(username) <=20 and len(password) <= 20 and password == verify_password and not registered_usernames:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            return redirect("/newpost")

        else:
            return render_template('signup.html',username=username,username_error=username_error,password_error=password_error,verify_error=verify_error)

    return render_template('signup.html', header="Signup")



### login page ###


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_error = ""


    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        ### link user to sql ###

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')


        else:

            login_error = "Login Unsuccessful."

    return render_template("login.html", login_error=login_error, header="Login" )



### make a new post ###

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':

        ### link owner to posts in sql ###

        owner = User.query.filter_by(username=session['username']).first()

        ### link html forms to python ###

        blog_title = request.form['blog-title']
        blog_entry = request.form['blog-entry']

        ### errors ###
        
        title_error = ''
        blog_error = ''

        ### title error ###

        if not blog_title:
            title_error = "Please fill out your blog title"

            ### entry error ###
        if not blog_entry:
            blog_error = "Please fill out your blog entry"

            ### no errors ###

        if not blog_error and not title_error:
            new_entry = Blog(blog_title, blog_entry, owner)
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) #add new post to database and website
        else:
            return render_template('new_blog.html', title='New Entry', title_error=title_error, blog_error=blog_error, 
                blog_title=blog_title, blog_entry=blog_entry) #errors alerts
    
    return render_template('new_blog.html', title='New Entry')


### log out ###
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if  __name__ == "__main__":
    app.run()