from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

### MAMP server config ###

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

### SQL config with mamp ###

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(30))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, owner):
        self.username = username
        self.owner = owner






### home page ###

@app.route('/')
def index():
    return redirect('/blog')


### blog listing page ###

@app.route('/blog')

def blog():


    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('home.html', posts=posts, title='Build-a-blog')
    else:
        post = Blog.query.get(blog_id)
        return render_template('blog_history.html', post=post, title='Blog Entry')


  ### new blog post page ###    

@app.route('/signup', methods=['POST', 'GET'])

@app.route('/login', methods=['POST', 'GET'])

@app.route('/index', methods=['POST', 'GET'])




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':

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
            new_entry = Blog(blog_title, blog_entry)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) #add new post to database and website
        else:
            return render_template('new_blog.html', title='New Entry', title_error=title_error, blog_error=blog_error, 
                blog_title=blog_title, blog_entry=blog_entry) #errors alerts
    
    return render_template('new_blog.html', title='New Entry')

if  __name__ == "__main__":
    app.run()