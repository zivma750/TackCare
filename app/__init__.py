from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta,datetime,time
import pytz
import atexit


#Create Flask App

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

#Configure ranadom secret key and db location
app.config['SECRET_KEY'] = '47db71e739639f70b97f57093694bbec'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

#Add DB, Crypt lib, and andmin configuration to the application
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
admin = Admin(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category ='info'

#Configure SocketIO and Schedualer
socketio = SocketIO(app,message_queue='redis://localhost:6379',logger=True, engineio_logger=True)
scheduler = BackgroundScheduler()


from app import models
from app import drugapi


#Set and init Admin Views
class NotificationView(ModelView):
    column_display_pk = True 
    column_hide_backrefs = False
    column_list = ('id', 'title', 'content','date','time','user_id','elderly_user_id','took')

class UserView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id', 'username', 'email','image_file','password','ElderlyUser','Notifications','Drugs')


class ElderlyuserView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id', 'username', 'password','user_id')


class DrugView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id', 'name', 'type','dose','timesaday','taketime','gap','packsize','daystotake','startdate','user_id','elderly_user_id','drugschedules','drugschedules','finish')

class DrugScheduleView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id', 'takedate', 'taketime','took','user_id','drug_id','elderly_user_id')

class ActivitiesView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('id', 'day', 'activity1','activity2','activity3','elderly_user_id')

admin.add_view(UserView(models.User, db.session))
admin.add_view(NotificationView(models.Notification, db.session))
admin.add_view(ElderlyuserView(models.Elderlyuser, db.session))
admin.add_view(DrugView(models.Drug, db.session))
admin.add_view(DrugScheduleView(models.DrugSchedule, db.session))
admin.add_view(ActivitiesView(models.Activities, db.session))


## DB one time creation id not exist and create tables if missing
with app.app_context() as ctx:
    ctx.push()
    db.create_all()

from app import routes

