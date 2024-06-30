import secrets
import os
import json
import atexit
from PIL import Image
from flask import Flask, render_template, url_for,  flash, redirect, request,abort
from app.models import User, Notification ,Drug, DrugSchedule,Activities,Elderlyuser
from app import app, db, bcrypt ,socketio,scheduler
from app.forms import RegistrationForm, LoginForms ,UpdateAccountForm, AddNotificationForm ,AddDrugForm,AddActivityForm
from flask_login import login_user, current_user ,logout_user,login_required
from app.drugapi import DrugAPI
from datetime import timedelta,datetime,time
import pytz






#pages and website logic
@app.route("/")
@app.route("/home")
@login_required
def home():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date.asc()).order_by(Notification.time.asc())
    drugs = Drug.query.filter_by(user_id=current_user.id).order_by(Drug.startdate.asc())
    eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
    eldelys_dict = {i.id: i.username for i in eldelys}
    return render_template("home.html",notifications=notifications ,drugs=drugs,eldelys_dict=eldelys_dict)



@app.route("/drugs")
@login_required
def drugs():
    if current_user.is_authenticated:
        drugs = Drug.query.filter_by(user_id=current_user.id).order_by(Drug.startdate.asc())
        drug_schedule = DrugSchedule.query.filter_by(user_id=current_user.id)
        eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
        eldelys_dict = {i.id: i.username for i in eldelys}
        return render_template("drugs.html",drugs=drugs,drug_schedule=drug_schedule, title="Drugs",eldelys_dict=eldelys_dict)
    else:
        return render_template("home.html")
    


def calc_dates(drug):
    drug_id = drug.id
    startdate = drug.startdate
    gap = drug.gap
    taketime = drug.taketime
    packsize = drug.packsize
    timesaday = drug.timesaday
    dose = drug.dose
    daystotake = drug.daystotake

    datelist = []
    timelist =[]

    dummy_date = datetime(2000, 1, 1)  # Dummy date
    taketime_datetime = datetime.combine(dummy_date, taketime)

    timelist.append(taketime)
    while timesaday > 1:
        taketime_datetime = taketime_datetime + timedelta(hours=gap)
        timelist.append(taketime_datetime.time())
        timesaday -= 1

    datelist.append(startdate)
    while daystotake > 1:
        startdate = startdate + timedelta(days=1)
        datelist.append(startdate)
        daystotake -= 1

    return datelist,timelist





@app.route("/add_drug",methods=['GET','POST'])
@login_required
def add_drug():
    eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
    eldelys_list = [(i.id,i.username) for i in  eldelys ]
    form = AddDrugForm()
    form.eldrly.choices = eldelys_list
    if form.validate_on_submit():
        warnings = ""
        current_drug = DrugAPI(form.name.data)
        durg_info = current_drug.check_fda_approval(current_drug.drug_name)
        if durg_info == None:
            flash('Drug not found in FDA Data Base', 'warning')
        else:
            if 'warnings' in durg_info['results'][0].keys():
                warning = durg_info['results'][0]['warnings']
            else:
                warning = durg_info['results'][0]['warnings_and_cautions']
            warnings = '\n'.join(warning)



        drug = Drug(name=form.name.data,type=form.type.data,dose=form.dose.data,timesaday=form.timesaday.data,daystotake=form.daystotake.data,user_id=current_user.id,startdate=form.startdate.data,packsize=form.packsize.data,gap=form.gap.data,taketime=form.taketime.data,elderly_user_id=form.eldrly.data,warnings=warnings,finish=False)
        db.session.add(drug)
        db.session.commit()
        drug = Drug.query.filter_by(user_id=current_user.id).order_by(Drug.id.desc()).first()
        dateslist, timeslist = calc_dates(drug)
        for date in dateslist:
            for time in timeslist:
                drug_schedule = DrugSchedule(user_id=current_user.id,drug_id=drug.id,takedate=date,taketime=time,took=False,elderly_user_id=form.eldrly.data)
                db.session.add(drug_schedule)
                db.session.commit()

        flash('Your Drug has been added !','success')
        return redirect(url_for('drugs'))
        
    return render_template("add_drug.html", title="Add Drug", form=form,eldelys_list=eldelys_list)


@app.route("/delete_drug/<int:drug_id>", methods=['GET','POST'])
@login_required
def delete_drug(drug_id):

    drug = Drug.query.get_or_404(drug_id)
    db.session.delete(drug)
    db.session.commit()

    flash('Your drug has been deleted!', 'success')
    return redirect(url_for('drugs'))


@app.route("/edit_notification/<int:notification_id>",methods=['GET','POST'])
@login_required
def edit_notification(notification_id):
    eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
    eldelys_list = [(i.id, i.username) for i in eldelys]
    form = AddNotificationForm()
    form.eldrly.choices = eldelys_list
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        abort(403)
    if form.validate_on_submit():
        notification.title = form.title.data
        notification.content = form.content.data
        notification.date = form.date.data
        notification.time = form.time.data
        notification.elderly_user_id = form.eldrly.data
        db.session.commit()
        flash('Your Notification has been Updated !','success')
        return redirect(url_for('notification'))

    elif request.method == 'GET':
        form.title.data = notification.title
        form.content.data = notification.content  
        form.date.data = notification.date 
        form.time.data = notification.time
        form.eldrly.data = notification.elderly_user_id
    return render_template("edit_notification.html", title="edit Notification", notification=notification, form=form,eldelys_list=eldelys_list)


@app.route("/delete_notification/<int:notification_id>", methods=['GET','POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    flash('Your notification has been deleted!', 'success')
    return redirect(url_for('notification'))


@app.route("/add_notification",methods=['GET','POST'])
@login_required
def add_notification():
    eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
    eldelys_list = [(i.id,i.username) for i in  eldelys ]
    form = AddNotificationForm()
    form.eldrly.choices = eldelys_list
    if form.validate_on_submit():
        notification = Notification(title=form.title.data,content=form.content.data,date=form.date.data,time=form.time.data,user_id=current_user.id,elderly_user_id=form.eldrly.data,took=False)
        db.session.add(notification)
        db.session.commit()
        flash('Your Notification has been added !','success')
        return redirect(url_for('notification'))
    return render_template("add_notification.html", title="Add Notification", form=form ,eldelys_list=eldelys_list)


@app.route("/notification")
@login_required
def notification():
    if current_user.is_authenticated:
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date.asc()).order_by(Notification.time.asc())
        eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
        eldelys_dict = {i.id: i.username for i in eldelys}
        return render_template("notification.html",notifications=notifications,eldelys_dict=eldelys_dict, title="Notification")
    else:
        return render_template("home.html")


@app.route("/api", methods=['GET','POST'])
def api():
    data = request.json
    if not data:
        return "no data sent"

    return [data,data]


# @app.route("/about")
# @login_required
# def about():
#     return render_template("about.html")


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hased_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        elderly_hased_pw = bcrypt.generate_password_hash(form.elderlypassword.data).decode('utf-8')
        #if form.elderlypassword.data:
        #    elderly2_hased_pw = bcrypt.generate_password_hash(form.elderlypassword2.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hased_pw)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        elderly_user = Elderlyuser(username=form.elderlyusername.data, password=elderly_hased_pw, user_id=user.id)
        db.session.add(elderly_user)
        db.session.commit()
        db.session.refresh(elderly_user)
        if form.elderlypassword2.data:
            elderly2_hased_pw = bcrypt.generate_password_hash(form.elderlypassword2.data).decode('utf-8')
            elderly_user2 = Elderlyuser(username=form.elderlyusername2.data, password=elderly2_hased_pw, user_id=user.id)
            db.session.add(elderly_user2)
            db.session.commit()
            db.session.refresh(elderly_user2)

        eldelys = Elderlyuser.query.filter_by(user_id=user.id)
        eldelys_list = [i.id for i in eldelys]
        for elderly_id in eldelys_list:
            for day in range(1,8,1):
                activity = Activities(day=day, activity1=False, activity2=False, activity3=False,
                                          user_id=user.id, elderly_user_id=elderly_id)
                db.session.add(activity)
            db.session.commit()
        flash('Your account has been Created !','success')
        return redirect(url_for('login'))
    return render_template("register.html",  title="Register", form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForms()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('email or pass are worng- try again', 'danger')
    return render_template("login.html",  title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    rnd_hex = secrets.token_hex(8)
    _, f_ext =os.path.splitext(form_picture.filename)
    picture_fn = rnd_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',picture_fn)

    #resize
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has bee updated','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file= url_for('static',filename = 'profile_pics/'+ current_user.image_file)
    return render_template("account.html",  title='Account', image_file=image_file , form=form)



@app.route('/send_message')
def send_message():
    message = "Hello from Flask!"
    socketio.emit('my_message', {'data': message})
    return "Message sent!"



@app.route("/activities")
@login_required
def activities():

    if current_user.is_authenticated:
        activities = Activities.query.filter_by(user_id=current_user.id).order_by(Activities.day.asc())
        eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
        eldelys_dict = {i.id: i.username for i in eldelys}
        eldely_activities = {}
        for el_id in eldelys_dict.keys():
            d1 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=1).first()
            d2 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=2).first()
            d3 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=3).first()
            d4 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=4).first()
            d5 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=5).first()
            d6 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=6).first()
            d7 = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=el_id, day=7).first()
            eldely_activities[el_id] = {'d1':d1,'d2':d2,'d3':d3,'d4':d4,'d5':d5,'d6':d6,'d7':d7}

        return render_template("activities.html", title="activities",eldely_activities=eldely_activities,eldelys_dict=eldelys_dict)
    else:
        return render_template("home.html")
    

@app.route("/add_activity",methods=['GET','POST'])
@login_required
def add_activity():

    eldelys = Elderlyuser.query.filter_by(user_id=current_user.id)
    eldelys_list = [(i.id, i.username) for i in eldelys]
    form = AddActivityForm()
    form.eldrly.choices = eldelys_list

    if form.validate_on_submit():
        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=1).first()
        activity.activity1 = form.a1d1.data
        activity.activity2 = form.a2d1.data
        activity.activity3 = form.a3d1.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=2).first()
        activity.activity1 = form.a1d2.data
        activity.activity2 = form.a2d2.data
        activity.activity3 = form.a3d2.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=3).first()
        activity.activity1 = form.a1d3.data
        activity.activity2 = form.a2d3.data
        activity.activity3 = form.a3d3.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=4).first()
        activity.activity1 = form.a1d4.data
        activity.activity2 = form.a2d4.data
        activity.activity3 = form.a3d4.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=5).first()
        activity.activity1 = form.a1d5.data
        activity.activity2 = form.a2d5.data
        activity.activity3 = form.a3d5.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=6).first()
        activity.activity1 = form.a1d6.data
        activity.activity2 = form.a2d6.data
        activity.activity3 = form.a3d6.data
        db.session.commit()

        activity = Activities.query.filter_by(user_id=current_user.id,elderly_user_id=form.eldrly.data,day=7).first()
        activity.activity1 = form.a1d7.data
        activity.activity2 = form.a2d7.data
        activity.activity3 = form.a3d7.data
        db.session.commit()
        flash('Your Activity has been added !', 'success')
        return redirect(url_for('activities'))
    return render_template("add_activity.html", title="Edit Activity", form=form)


# @socketio.on('message')
# def message(data):
#     print(data)
#     socketio.emit('message', data)
#     login_user(data)
#     #print('received message: ' + data)
#     #current_drug = DrugAPI(data)
#     #drug_info = current_drug.check_fda_approval(current_drug.drug_name)
#     #print(drug_info)
#
#     #socketio.emit('message', {'message': 'this is data from the flask '+str(drug_info)})
#     return "Message sent!"

@socketio.on('message')
def message(data):
    # test valid json
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:

        print("Received data is not in JSON format:", data)
        return "Invalid data format"
    type = data_dict['type']
    #if not current_user.is_authenticated:
    if type == "login":
        global android_username_id
        android_username_id = socket_login(data_dict['data'])
    if type == "notification_callback":
        notification = Notification.query.filter_by(id=data_dict['data']['notification_id']).first()
        notification.took = ('true' == data_dict['data']['took'].lower())
        db.session.commit()
        socketio.emit('messege', {'type':'info_notification','data':{'took':('true' == data_dict['data']['took'].lower())}})
    if type == "drugschedule_callback":
        drugschedule = DrugSchedule.query.filter_by(id=data_dict['data']['DrugSchedule_id']).first()
        drugschedule.took = ('true' == data_dict['data']['took'].lower())
        db.session.commit()
        socketio.emit('messege', {'type':'info_drug','data':{'took':('true' == data_dict['data']['took'].lower())}})

        drugschedules = DrugSchedule.query.filter_by(drug_id=data_dict['data']['drug_id']).all()
        drug = Drug.query.filter_by(id=data_dict['data']['drug_id']).first()

        #test Drug Status
        status = []
        for drugschedule1 in drugschedules:
            status.append(drugschedule1.took)
        if all(status):
            drug.finish = True
        db.session.commit()

    else:
        socketio.emit('message',data)


def socket_login(data_dict):
    user_username = data_dict["username"]
    user_password = data_dict["password"]
    user = Elderlyuser.query.filter_by(username=user_username).first()

    if user:
        if bcrypt.check_password_hash(user.password, user_password):
            login_user(user)
            socketio.emit('message', {'type': 'login_callback','data':{'user_id':str(user.id),'validpass':True,'validuser':True}})
        else:
            socketio.emit('message', {'type': 'login_callback','data':{'user_id':None,'validpass':False,'validuser':True}})
    else:
        socketio.emit('message', {'type': 'login_callback','data':{'user_id':None,'validpass':True,'validuser':False}})

    check_activity()
    #socketio.emit('message',login_response)
    return user.id


##listener##

def check_notifications():
    with app.app_context():
        local_tz = pytz.timezone('Asia/Jerusalem')
        current_datetime = datetime.now(local_tz)
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        notifications = Notification.query.filter(Notification.date <= current_date).all()


        for notification in notifications:
            if notification.date == current_date and notification.time <= current_time and not notification.took:
                json = {
                          "type": "notification",
                          "data": { "notification_id": str(notification.id),
                                    "title": str(notification.title),
                                    "content" :str(notification.content),
                                    "date":str(notification.date),
                                    "time":str(notification.time),
                                    "user_id":str(notification.user_id),
                                    "elderly_user_id":str(notification.elderly_user_id),
                                    "took":str(notification.took)
                                    }
                        }
                socketio.emit('message',json)


def check_drugs():
    with app.app_context():
        local_tz = pytz.timezone('Asia/Jerusalem')
        current_datetime = datetime.now(local_tz)
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        drugschedules = DrugSchedule.query.filter(DrugSchedule.takedate == current_date).all()


        for drugschedule in drugschedules:
            drugsinfo = Drug.query.filter_by(id=drugschedule.drug_id).first()
            if drugschedule.takedate == current_date and drugschedule.taketime <= current_time and not drugschedule.took:
                json ={
                          "type": "drugschedule",
                          "data": { "DrugSchedule_id": str(drugschedule.id),
                                    "takedate":str(drugschedule.takedate),
                                    "taketime":str(drugschedule.taketime),
                                    "drug_id":str(drugschedule.drug_id),
                                    "user_id":str(drugschedule.user_id),
                                    "elderly_user_id":str(drugschedule.elderly_user_id),
                                    "took":str(drugschedule.took),
                                    "drug_name":str(drugsinfo.name),
                                    "dose":str(drugsinfo.dose),
                                    "type":str(drugsinfo.type)
                                    }
                        }
                socketio.emit('message',json)

def check_activity():
    local_weekday_dic = {6:1,0:2,1:3,2:4,3:5,4:6,5:7}
    with app.app_context():
        local_tz = pytz.timezone('Asia/Jerusalem')
        current_datetime = datetime.now(local_tz)
        current_week_day = current_datetime.date().weekday()
        #current_time = current_datetime.time()
        activities = Activities.query.filter(Activities.day == local_weekday_dic[current_week_day]).all()


        for activitie in activities:
            if activitie.day == local_weekday_dic[current_week_day]:
                json ={
                        "type": "activitiy",
                        "data": {"activitiy_id": str(activitie.id),
                                 "day": str(activitie.day),
                                 "activity1": str(activitie.activity1),
                                 "activity2": str(activitie.activity2),
                                 "activity3": str(activitie.activity3),
                                 "user_id": str(activitie.user_id),
                                 "elderly_user_id": str(activitie.elderly_user_id)
                                 }
                    }
                socketio.emit('message',json)

scheduler.add_job(func=check_notifications, trigger="interval", seconds=11)
scheduler.add_job(func=check_drugs, trigger="interval", seconds=9)
scheduler.add_job(func=check_activity, trigger="interval", seconds=5)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
