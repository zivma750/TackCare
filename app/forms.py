from datetime import datetime
import pytz
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import SelectField , StringField,PasswordField,SubmitField, BooleanField, IntegerField, DateTimeField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Optional
from app.models import User, Elderlyuser
from app.drugapi import DrugAPI

#this files contains the starchcure of the forms in the project

# *********** Login \ Register **************

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20) ])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    elderlyusername = StringField('Username',validators=[DataRequired(),Length(min=2,max=20) ])
    elderlypassword = PasswordField('Password', validators=[DataRequired()])
    elderlyconfirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('elderlypassword')])
    elderlyusername2 = StringField('Username #2', validators=[Length(min=2, max=20),Optional()])
    elderlypassword2 = PasswordField('Password ',validators=[Optional()])
    elderlyconfirm_password2 = PasswordField('Confirm Password', validators=[EqualTo('elderlypassword2'),Optional()])
    submit = SubmitField('Sign Up')

    def validate_username (self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken. Choose a diffrent one.')
        
    def validate_email (self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Choose a diffrent one.')

    def validate_elderlyusername(self, elderlyusername):
        user = Elderlyuser.query.filter_by(username=elderlyusername.data).first()
        if user:
            raise ValidationError('That Username is taken. Choose a diffrent one.')

    def validate_elderlyusername2(self, elderlyusername2):
        user = User.query.filter_by(username=elderlyusername2.data).first()
        if user:
            raise ValidationError('That Username is taken. Choose a diffrent one.')



class LoginForms(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember =BooleanField('Remember Me')
    submit = SubmitField('login')

# *********** Notifications **************

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20) ])
    email = StringField('Email',validators=[DataRequired(),Email()])
    picture = FileField("Update Profile Picture",validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

    def validate_username (self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That Username is taken. Choose a diffrent one.')
        else:
            raise ValidationError('That Username must be diffrent than your current one.') 
            
    def validate_email (self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Choose a diffrent one.')
        else:
            raise ValidationError('That Username must be diffrent than your current one.')
        
        
class AddNotificationForm(FlaskForm):
    eldrly = SelectField('Eldrly user',coerce=str, validators=[DataRequired()])
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    date = DateField('Date',validators=[DataRequired()])
    time = TimeField('Time',validators=[DataRequired()])
    submit = SubmitField('Add Notification')

    def validate_date(self, field):
        local_tz = pytz.timezone('Asia/Jerusalem')
        current_datetime = datetime.now(local_tz)
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        # Combine the date and time fields into a datetime object
        input_datetime_local = datetime.combine(field.data, self.time.data, tzinfo=local_tz)

        # Check if the selected date is in the past
        if field.data < current_date:
            raise ValidationError('The date must be in the future.')

        # Check if the date is today and the selected time is in the past
        if field.data == current_date and self.time.data < current_time:
            raise ValidationError('The time must be in the future.')

    def validate_time(self, field):
        # This method is left empty because the validation is handled in validate_date
        pass
# *********** Drugs **************


class AddDrugForm(FlaskForm):
    eldrly = SelectField('Eldrly user', coerce=str, validators=[DataRequired()])
    name = StringField('Drug Name',validators=[DataRequired()])
    fdawarnning = BooleanField('Run FDA Aprroval Test',default=False)
    type = SelectField('Drug Type',validators=[DataRequired()],choices=[('pill', 'Pills'), ('drop', 'Drops'), ('liquid', 'Liquid (ml)')])
    dose = IntegerField('Dose (for Drops or Liquid - ml)',validators=[DataRequired()])
    timesaday = IntegerField('How many times a day?',validators=[DataRequired()])
    daystotake = IntegerField('How many days to take?',validators=[DataRequired()])
    startdate = DateField('Starting date',validators=[DataRequired()])
    taketime= TimeField('Take Time ',validators=[DataRequired()])
    gap = IntegerField('Gap between each take (hours)',validators=[DataRequired()])
    packsize = IntegerField('Pack Size?',validators=[DataRequired()])
    submit = SubmitField('Add Drug')


    def validate(self,extra_validators=None):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        current_drug = DrugAPI(self.name.data)
        durg_info = current_drug.check_fda_approval(current_drug.drug_name)
        if durg_info == None and self.fdawarnning.data:
            self.name.errors.append(ValidationError('Drug not found in FDA Data Base'),)
            return False
        return True

# *********** Activites **************

class AddActivityForm(FlaskForm):
    eldrly = SelectField('Eldrly user', coerce=str)
    a1d1 = BooleanField('a1d1',default=False)
    a1d2 = BooleanField('a1d2',default=False)
    a1d3 = BooleanField('a1d3',default=False)
    a1d4 = BooleanField('a1d4',default=False)
    a1d5 = BooleanField('a1d5',default=False)
    a1d6 = BooleanField('a1d6',default=False)
    a1d7 = BooleanField('a1d7',default=False)
    a2d1 = BooleanField('a2d1',default=False)
    a2d2 = BooleanField('a2d2',default=False)
    a2d5 = BooleanField('a2d5',default=False)
    a2d6 = BooleanField('a2d6',default=False)
    a2d3 = BooleanField('a2d3',default=False)
    a2d4 = BooleanField('a2d4',default=False)
    a2d7 = BooleanField('a2d7',default=False)
    a3d1 = BooleanField('a3d1',default=False)
    a3d2 = BooleanField('a3d2',default=False)
    a3d3 = BooleanField('a3d3',default=False)
    a3d4 = BooleanField('a3d4',default=False)
    a3d5 = BooleanField('a3d5',default=False)
    a3d6 = BooleanField('a3d6',default=False)
    a3d7 = BooleanField('a3d7',default=False)
    submit = SubmitField('Add Activities')

