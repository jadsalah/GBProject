from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,SelectField,BooleanField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired, Length, Email,EqualTo,ValidationError, NumberRange
from GBProject.models import Fruit,Client,EuroToStrling,EuroToDollars


class FruitSearchForm(FlaskForm):
	search_field = StringField('Search Field', validators=[DataRequired()])
	search_filter = SelectField('Search Filter',choices=[('id','ID'),('name','Name'),('proh_count','Prohibited Country'),('curr','Currency'),('size','Size'),('metric','Metric')])
	#language = SelectField('Programming Language',choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
	search_btn = SubmitField('Search')


class FruitAddForm(FlaskForm):
	file_field =  FileField('Upload File', validators=[FileAllowed(['csv',]),])
	add_btn = SubmitField('Add Fruit')

class ClientAddForm(FlaskForm):
	file_field =  FileField('Upload File', validators=[FileAllowed(['csv',]),])
	add_btn = SubmitField('Add Client')


class UserSearchForm(FlaskForm):
	search_field = StringField('Search Field', validators=[DataRequired()])
	search_btn = SubmitField('Search')


class ClientEditForm(FlaskForm):
	name 	= StringField('Name', validators=[DataRequired(),])
	country = SelectField('Country', choices=[('France','France'),('Germany','Germany'),('Luxembourg','Luxembourg')])
	city 	= StringField('City', validators=[DataRequired(),])
	gender 	= SelectField('Gender',choices=[('male','Male'),('female','Female')])

	currency_pref1 = SelectField('Currency Prefrence',choices=[('euro','Euro'),('dollar','Dollar'),('sterling','Sterling')])
	currency_pref2 = SelectField('Currency Prefrence',choices=[('euro','Euro'),('dollar','Dollar'),('sterling','Sterling')])
	currency_pref3 = SelectField('Currency Prefrence',choices=[('euro','Euro'),('dollar','Dollar'),('sterling','Sterling')])

	size_pref1 = SelectField('Size Prefrence',choices=[('small','Small'),('medium','Medium'),('large','Large')])
	size_pref2 = SelectField('Size Prefrence',choices=[('small','Small'),('medium','Medium'),('large','Large')])
	size_pref3 = SelectField('Size Prefrence',choices=[('small','Small'),('medium','Medium'),('large','Large')])

	type_pref1 = SelectField('Type Prefrence',choices=[('currency','Currency'),('size','Size')])
	type_pref2 = SelectField('Type Prefrence',choices=[('currency','Currency'),('size','Size')])

	update_btn = SubmitField('Update')

class AveragesForm(FlaskForm):
	start_month 	= SelectField('Start Month',choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')])
	end_month 		= SelectField('End Month',choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')])
	compute_btn 	= SubmitField('Compute')

class Translate(FlaskForm):
	french 			= BooleanField('French')
	translate_btn 	= SubmitField('Translate')