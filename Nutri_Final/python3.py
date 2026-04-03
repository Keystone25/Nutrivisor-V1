from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, update, Column, Integer, String
from fitness_tools.meals.meal_maker import MakeMeal
from flask import Blueprint
from flask_login import UserMixin, current_user, login_user
from flask_login import LoginManager, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, Response, request, flash, redirect, url_for
import cv2
import os
import glob
from PIL import Image
from keras.models import load_model
import pandas as pd
from keras.utils import img_to_array
import numpy as np
from datetime import datetime
from pytz import timezone
import re

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'newmenu1.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'C:/Users/mail4_zofe0iz/Desktop/Latest_Nutri2/static/upload/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



auth = Blueprint('auth', __name__)
app.register_blueprint(auth)
main = Blueprint('main', __name__)
app.register_blueprint(main)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(u_id):
    return User.query.get(int(u_id))





class User(UserMixin,db.Model):
     id = db.Column('u_id', db.Integer, primary_key=True)
     fname = db.Column(db.String(100))
     lname = db.Column(db.String(100))
     email = db.Column(db.String(50), nullable=False,unique=True)
     utype = db.Column(db.String(20), default='user')
     phone = db.Column(db.String(20))
     dob = db.Column(db.String(20))
     password = db.Column(db.String(50),nullable=False)
     weight = db.Column(db.Integer())
     height = db.Column(db.Integer())
     age = db.Column(db.String(10))
     gender = db.Column(db.String(10))
     bodytype = db.Column(db.String(10))
     activity = db.Column(db.String(20))
     goal = db.Column(db.String(20))
     health_issues1 = db.Column(db.String(10), default='')
     health_issues2 = db.Column(db.String(10), default='')
     allergy1 = db.Column(db.String(100), default='')
     allergy2 = db.Column(db.String(100), default='')
     cal = db.Column(db.Float())
     fat = db.Column(db.Float())
     protein = db.Column(db.Float())
     carbs = db.Column(db.Float())



class logsession(db.Model):
    id = db.Column('session_id', db.Integer, primary_key=True)
    log_date = db.Column(db.String(50))
    log_time = db.Column(db.String(50))

class menu(db.Model):  #this is a table named menu inside the menu1 database for user and admin but only viewing for user
    id = db.Column('menu_id', db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    cal = db.Column(db.String(50))
    stdwt = db.Column(db.String(50))
    cal100 = db.Column(db.String(50))
    meal = db.Column(db.String(50))
    allergen1 = db.Column(db.String(50), default='')
    allergen2 = db.Column(db.String(50), default='')
    risk1 = db.Column(db.String(50), default='')
    risk2 = db.Column(db.String(50), default='')
    imgpath = db.Column(db.String(100), default='')





class daily2(db.Model):#this is a table named daily2 inside the menu1 database for users
    id = db.Column('daily_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.u_id')) 
    usr_cal = db.Column(db.Float)
    br_item = db.Column(db.String(50), default='')
    br_cal = db.Column(db.Float, default=0.0)
    lu_item = db.Column(db.String(50), default='')
    lu_cal = db.Column(db.Float, default=0.0)
    di_item = db.Column(db.String(50), default='')
    di_cal = db.Column(db.Float, default=0.0)

class Feed(db.Model):
    id = db.Column('feed_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.String(600))
    timestamp = db.Column(db.String(50))

@app.route('/')
def main_all():
    return redirect(url_for('login'))

@app.route('/U_Home_page')
@login_required
def U_Home_page():
    user_data = daily2.query.filter_by(user_id=current_user.id).first()
    return render_template('U_Home_page_1.html',menu=menu.query.all(),user=current_user,daily=user_data)

@app.route('/U_Diet_Recommender')
@login_required
def U_Diet_recommender():
    quota = daily2.query.filter_by(user_id=current_user.id).first()

    return render_template('select_food1.html',menu=menu.query.all(),quota=quota)

@app.route('/U_Discover')
@login_required
def U_Discover():
    return render_template('U_Discover.html',menu=menu.query.all(), users=User.query.all(), daily2=daily2.query.all())

@app.route('/U_Select_food', methods=['GET', 'POST'])
@login_required
def U_Select_food():

    if request.method == 'POST':
     feed = Feed(name=request.form['name'], message=request.form['message'], timestamp=str(datetime.now()))
     db.session.add(feed)
     db.session.commit()
    
    return render_template('U_Select_food.html',menu=menu.query.all(), users=User.query.all(), daily2=daily2.query.all())

@app.route('/U_Settings', methods=['GET', 'POST'])
@login_required
def U_Settings():
    
    if request.method == 'POST':
     feed = Feed(name=request.form['name'], message=request.form['message'], timestamp=str(datetime.now()))
     db.session.add(feed)
     db.session.commit()

    return render_template('U_Settings.html',fname=current_user.fname,email=current_user.email, lname=current_user.lname)


@app.route('/UpdateUser', methods=['POST'])
@login_required
def UpdateUser():
    if request.method == 'POST':
        curr_user = User.query.get(current_user.id)
        curr_user.fname = request.form['fname']
        curr_user.lname = request.form['lname']
        curr_user.email = request.form['email']
        curr_user.phone = request.form['phone']
        db.session.commit()
    return redirect(url_for('U_Settings'))

@app.route('/UpdateMeasure', methods=['POST'])
@login_required
def UpdateMeasure():
    if request.method == 'POST':
        curr_user = User.query.get(current_user.id)
        curr_user.height = request.form['height']
        curr_user.weight = request.form['weight']
        curr_user.gender = request.form['gender']
        curr_user.age = request.form['age']
        curr_user.bodytype = request.form['bodytype']
        db.session.commit()
    return redirect(url_for('U_Settings'))

@app.route('/UpdatePassword', methods=['POST'])
@login_required
def UpdatePassword():
    if request.method=='POST':
        usr=User.query.get(current_user.id)
        old_pass = request.form['old-pass']
        new_pass = request.form['new-pass']
        print(old_pass, new_pass)
        print(usr.password, generate_password_hash(new_pass, method='pbkdf2:sha256'))
        new_pass_hash = generate_password_hash(new_pass, method='pbkdf2:sha256')
        if check_password_hash(usr.password, old_pass):
            usr.password=generate_password_hash(new_pass, method='pbkdf2:sha256')
            db.session.commit()
            flash("Password Changed")
        else:
            flash("Old Password does not match")
    return redirect(url_for('U_Settings'))



@app.route('/User_database')
@login_required
def User_database():
    return render_template('Admin_User_Viewer.html', users=User.query.all())


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('User_database'))

@app.route('/Admin_Panel')
@login_required
def Admin_Panel():
    return render_template('Admin_Panel.html', menu=menu.query.all())



@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_menu_item(id):
    menu_item = menu.query.get_or_404(id)
    db.session.delete(menu_item)
    db.session.commit()

    return redirect(url_for('Admin_Panel'))


@app.route('/Feedback_Admin_Side')
@login_required
def Feedback_Admin_Side(): 
    feed_data = Feed.query.all()
    return render_template('Feedback_Admin_Side.html', feed=feed_data)




@app.route('/allmenu')
@login_required
def allmenu():
    return render_template('menu_all.html', menu=menu.query.all())


@app.route('/allusers')
@login_required
def allusers():
    return render_template('users_all.html', users=User.query.all())


@app.route('/new2', methods=['GET', 'POST'])
@login_required
def new2():
    if request.method == 'POST':
        cal100_ = round((int(request.form['cal'])*100)/int(request.form['stdwt']),2)

        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        length = len(path)
        print(path)
        path1 = path[13:]
        print(path1)
        file1.save(path)

        food = menu(item=request.form['item'], cal=request.form['cal'], stdwt=request.form['stdwt'],
                cal100=cal100_, meal=request.form['meal'], allergen1=request.form['allergen1'],
                    allergen2=request.form['allergen2'], risk1=request.form['risk1'], risk2=request.form['risk2'],
                    imgpath=str(path1))

        db.session.add(food)
        db.session.commit()

        return redirect(url_for('Admin_Panel'))
    return render_template('new2.html')


@app.route('/new1', methods=['GET', 'POST'])
@login_required
def new1():
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname']  or not request.form['email'] or not \
                request.form['phn'] or not request.form['dob'] or not request.form['pass'] or not request.form['pass1'] or not request.form['weight'] or not \
                request.form['height'] or not request.form['age'] or not request.form['gender'] or not request.form['bdy'] or not \
                request.form['act'] or not request.form['goal'] :
                
            flash('Please enter all the required* fields')
            return redirect(url_for('signup'))
        else:
            obj = MakeMeal(int(int(request.form['weight']) * 2.204), goal=request.form['goal'],
                           activity_level=request.form['act'], body_type=request.form['bdy'])
            cal_ = (obj.daily_min_calories() + obj.daily_max_calories()) / 2
            fat_ = (obj.daily_min_fat() + obj.daily_max_fat()) / 2
            protein_ = (obj.daily_min_protein() + obj.daily_max_protein()) / 2
            carbs_ = (obj.daily_min_carbs() + obj.daily_max_carbs()) / 2        
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phn')
            dob= request.form.get('dob')
            password = request.form.get('pass')
            weight = request.form.get('weight')
            height = request.form.get('height')
            age = request.form.get('age')
            gender = request.form.get('gender')
            bodytype = request.form.get('bdy')
            activity = request.form.get('act')
            goal = request.form.get('goal')
            health_issues1=request.form.get('health_issues1')
            health_issues2=request.form.get('health_issues2')
            allergy1=request.form.get('allergy1')
            allergy2=request.form.get('allergy2') 
        new_user1 = User(fname=fname, lname=lname, email=email, phone=phone,dob=dob,password=generate_password_hash(password, method='pbkdf2:sha256'),weight=weight,height=height,age=age,gender=gender,bodytype=bodytype,activity=activity,goal=goal,health_issues1=health_issues1,health_issues2=health_issues2,allergy1=allergy1,allergy2=allergy2,cal=cal_, fat=fat_, protein=protein_, carbs=carbs_)
        if new_user1:
                db.session.add(new_user1)
                db.session.commit()
                return redirect(url_for('User_database'))
    return render_template('new1.html')


@app.route('/edit_food/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_food(id):
    item = menu.query.get_or_404(id)

    if request.method == 'POST':
        item.item = request.form['item']
        item.cal = request.form['cal']
        item.stdwt = request.form['stdwt']
        item.cal100 = request.form['cal100']
        item.meal = request.form['meal']
        item.allergen1 = request.form['allergen1']
        item.allergen2 = request.form['allergen2']
        item.risk1 = request.form['risk1']
        item.risk2 = request.form['risk2']
        item.imgpath = request.form['img']
        
        db.session.commit()
        return redirect('/Admin_Panel')
        

    return render_template('edit_food.html', item=item)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        user.age = request.form['age']
        user.email = request.form['email']
        user.phone = request.form['phn']
        user.dob = request.form['dob']
        user.password = request.form['pass']
        user.weight = request.form['weight']
        user.height = request.form['height']
        user.gender = request.form['gender']
        user.goal = request.form['goal']
        user.bodytype = request.form['bodytype']
        user.activity = request.form['act']
        user.allergy1 = request.form['allergy1']
        user.allergy2 = request.form['allergy2']
        user.health_issues1 = request.form['health_issues1']
        user.health_issues2 = request.form['health_issues2']
        user.cal = request.form['cal']
        user.fat = request.form['fat']
        user.protien = request.form['protein']
        user.carbs = request.form['carbs']
        
        
        db.session.commit()
        return redirect('/User_database')
        

    return render_template('edit_user.html', user=user)






@app.route('/live_capture')
@login_required
def live_capture():
    return render_template('index1.html',menu=menu.query.all())


@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    if request.method == 'POST':

        quota = daily2.query.filter_by(user_id=current_user.id).first()

        if request.form['type'] == 'breakfast':
            quota.br_cal = request.form['cal']
            quota.br_item = request.form['item']
        elif request.form['type'] == 'lunch':
            quota.lu_cal = request.form['cal']
            quota.lu_item = request.form['item']
        else:
            quota.di_cal = request.form['cal']
            quota.di_item = request.form['item']

        db.session.commit()

        return redirect(url_for('U_Home_page'))
 

@app.route('/signup', methods=['GET','POST'])
def signup():
    
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname']  or not request.form['email'] or not \
                request.form['phn'] or not request.form['dob'] or not request.form['pass'] or not request.form['pass1'] or not request.form['weight'] or not \
                request.form['height'] or not request.form['age'] or not request.form['gender'] or not request.form['bdy'] or not \
                request.form['act'] or not request.form['goal'] :
                
            flash('Please enter all the required* fields')
            return redirect(url_for('signup'))
        
        else:
            
            obj = MakeMeal(int(int(request.form['weight']) * 2.204), goal=request.form['goal'],
                           activity_level=request.form['act'], body_type=request.form['bdy'])
            cal_ = (obj.daily_min_calories() + obj.daily_max_calories()) / 2
            fat_ = (obj.daily_min_fat() + obj.daily_max_fat()) / 2
            protein_ = (obj.daily_min_protein() + obj.daily_max_protein()) / 2
            carbs_ = (obj.daily_min_carbs() + obj.daily_max_carbs()) / 2        
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phn')
            dob= request.form.get('dob')
            password = request.form.get('pass')
            weight = request.form.get('weight')
            height = request.form.get('height')
            age = request.form.get('age')
            gender = request.form.get('gender')
            bodytype = request.form.get('bdy')
            activity = request.form.get('act')
            goal = request.form.get('goal')
            health_issues1=request.form.get('health_issues1')
            health_issues2=request.form.get('health_issues2')
            allergy1=request.form.get('allergy1')
            allergy2=request.form.get('allergy2') 

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
            if not (re.fullmatch(regex, email)):
                flash("Enter a valid email")
                return redirect(url_for('signup'))   

            if not (Pattern.match(phone)):
                flash("Enter a valid phone no")
                return redirect(url_for('signup'))

        

            user = User.query.filter_by(email=email).first()  # if this returns a user, then the email already exists in database

            if user:  # if a user is found, we want to redirect back to signup page so user can try again
                flash('Email address already exists!')
                return redirect(url_for('signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User(fname=fname, lname=lname, email=email, phone=phone,dob=dob,password=generate_password_hash(password, method='pbkdf2:sha256'),weight=weight,height=height,age=age,gender=gender,bodytype=bodytype,activity=activity,goal=goal,health_issues1=health_issues1,health_issues2=health_issues2,allergy1=allergy1,allergy2=allergy2,cal=cal_, fat=fat_, protein=protein_, carbs=carbs_)
            if new_user:
                    db.session.add(new_user)
                    db.session.commit()
                    flash('New account created!')
                    return redirect(url_for('login'))

        
        
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():

    log_obj = logsession.query.all()
    previous = log_obj[-1].log_date
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('pass')

        user = User.query.filter_by(email=email).first()
    
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S')
        ind_date = datetime.today().strftime('%d-%m-%Y')

        

        quota = daily2.query.filter_by(user_id=current_user.id).all()

        # if no record exists, create one
        if not quota:
            quota = daily2(
                user_id=current_user.id,
                br_item='', br_cal=0.0,
                lu_item='', lu_cal=0.0,
                di_item='', di_cal=0.0
            )
            db.session.add(quota)
            db.session.commit()

        log = logsession(log_date=ind_date, log_time=ind_time)
        db.session.add(log)
        db.session.commit()

        if current_user.utype == "user":
            return redirect(url_for('U_Home_page'))
        elif current_user.utype == "admin":
            return redirect(url_for('User_database'))

    return render_template('login.html')







@app.route('/logout')
@login_required
def logout():

   
    logout_user()
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M:%S')
    ind_date = datetime.today().strftime('%d-%m-%Y')
    log = logsession(log_date=ind_date, log_time=ind_time)
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run(debug=True,port=5100)


