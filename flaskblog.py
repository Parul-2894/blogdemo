from flask import Flask, render_template

app = Flask(__name__)

posts=[
    {
        'author': 'Parul Tiwari',
        'title': 'Blog Post',
        'content': 'First Post Content',
        'date_posted': 'April 20 2018'
    },
    {
        'author': 'Pablo ',
        'title': 'Blog Post2',
        'content': 'First Post2 Content',
        'date_posted': 'April 26 2018'
    }



]

@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html', posts= posts, title='Home page')

@app.route("/about")
def about():
    return render_template("about.html", title="About page")

if  __name__ == '__main__':
    app.run(port="8080", debug=True)