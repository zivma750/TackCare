from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    email = db.Column(db.String(100), unique=True,nullable=False)
    image_file = db.Column(db.String(100),nullable=False,default='default.jpg')
    password= db.Column(db.String(60),nullable=False)
    ElderlyUser = db.relationship('Elderlyuser',backref='creator',lazy=True )
    Notifications = db.relationship('Notification',backref='creator',lazy=True )
    Drugs = db.relationship('Drug',backref='creator',lazy=True )

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"

class Elderlyuser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    password= db.Column(db.String(60),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"ElderlyUser('{self.id}','{self.username}')"

  
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    content = db.Column(db.Text,nullable=False)
    date = db.Column(db.Date,nullable=False)
    time = db.Column(db.Time,nullable=False)
    took = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    elderly_user_id = db.Column(db.Integer, db.ForeignKey('elderlyuser.id'), nullable=False)

    def __repr__(self):
        return f"Notification('{self.title}','{self.content}','{self.date}','{self.user_id}','{self.id},'{self.elderly_user_id}')"

class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150),nullable=False)
    type = db.Column(db.Text,nullable=False)
    dose = db.Column(db.Integer,nullable=False)
    timesaday = db.Column(db.Integer,nullable=False)
    taketime= db.Column(db.Time, nullable=False)
    gap = db.Column(db.Integer, nullable=False)
    packsize = db.Column(db.Integer,nullable=False)
    daystotake = db.Column(db.Integer,nullable=False)
    startdate = db.Column(db.Date,nullable=False)
    finish = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    elderly_user_id = db.Column(db.Integer, db.ForeignKey('elderlyuser.id'), nullable=False)
    drugschedules = db.relationship("DrugSchedule", cascade="all, delete")
    warnings = db.Column(db.String)

    def __repr__(self):
        return f"Drug('{self.name}','{self.type}','{self.dose}','{self.daystotake}','{self.packsize}')"

class DrugSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    takedate = db.Column(db.Date,nullable=False)
    taketime = db.Column(db.Time,nullable=False)
    took = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'), nullable=False)
    elderly_user_id = db.Column(db.Integer, db.ForeignKey('elderlyuser.id'), nullable=False)

    def __repr__(self):
        return f"Drug('{self.id}','{self.takedate}','{self.user_id}','{self.drug_id}')"

class Activities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day= db.Column(db.Integer, nullable=False)
    activity1= db.Column(db.Boolean, nullable=False)
    activity2= db.Column(db.Boolean, nullable=False)
    activity3= db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    elderly_user_id = db.Column(db.Integer, db.ForeignKey('elderlyuser.id'), nullable=False)
    def __repr__(self):
        return f"Activities('{self.id}','{self.day}','{self.activity1}','{self.activity2}','{self.activity3}' ,'{self.user_id}')"