import logging
from flaskblog.models import User, Post
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import Registration, Login, ResetForm, UpdateAccountForm, PostForm, RequestResetForm, ResetForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

import os
import secrets
from PIL import Image


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page = page)
    return render_template('home.html', posts= posts, title='Home page')

@app.route("/about")
def about():
    return render_template("about.html", title="About page")

@app.route("/register", methods=['GET', 'POST'])
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Registration()
    if form.validate_on_submit():
        
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_pw )
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! you are now able to login', 'success')
        return redirect(url_for('login'))
    else:
        print(form.errors)

    return render_template("register.html", form = form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password , form.password.data):
           login_user(user, remember=form.remember.data)
           next_page = request.args.get('next') 
           if next_page != None:
                return redirect(next_page)
           else:
                return redirect(url_for('home'))
        else:
            flash(f'Not able to login, please check your email and password!', 'danger')
    else:
        print(form.errors)
    return render_template("login.html", form = form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="noreply@demo.com", recipients=[user.email])

    msg.body = f''' To reset your password, please visit the following link
{url_for('reset_password', token=token, _external=True)} 

If you do not make this request, then please ignore
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            flash("The email id is not persent, pleas register?", "error")
            return redirect(url_for('register'))
        else:
            send_reset_email(user)
            flash('An email has been sent to you with the instructions', 'info')
            return redirect(url_for('login'))

    return render_template("requestreset.html", form=form)



@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid  or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetForm()

    if form.validate_on_submit():
        
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()

        flash('Your Password has been updated! you are now able to login', 'success')
        return redirect(url_for('login'))


    return render_template("reset.html", form=form, title= 'Reset Password')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pic', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
     






@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            current_user.image_file = picture_name
            



        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account is updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_url = url_for('static', filename='profile_pic/' + current_user.image_file)
    return render_template("account.html", title="Account", image = image_url, form = form)



@app.route("/post/new" , methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content = form.content.data, author = current_user )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template("create_post.html", title="New Post", form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", title = post.title , post=post, legend='Create Post')


@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been successfully updated", "success")
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    
    return render_template("create_post.html", title = post.title , post=post, form = form, legend = 'Update Post')


@app.route("/post/<int:post_id>/delete", methods = [ 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been delete', 'success')
    return redirect(url_for('home'))
    
