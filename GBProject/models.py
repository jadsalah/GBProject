from GBProject import db

class UsersFavs(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'),nullable=False)
	fruit_id = db.Column(db.Integer, db.ForeignKey('fruit.id'),nullable=False)
	pref_order = db.Column(db.Integer,nullable=False,default=0)

class Fruit(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(20),unique=True,nullable=False)
	prohibited_country = db.Column(db.String(20),unique=False,nullable=False)
	currency = db.Column(db.String(20),unique=False,nullable=False)
	size = db.Column(db.String(20),unique=False,nullable=False)
	metric = db.Column(db.String(20),unique=False,nullable=False)
	price_unit = db.Column(db.String(20),unique=False,nullable=False)

	price_month_1 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_2 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_3 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_4 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_5 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_6 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_7 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_8 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_9 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_10 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_11 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	price_month_12 = db.Column(db.String(5),unique=False,nullable=False,default='0')

	volume_month_1 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_2 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_3 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_4 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_5 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_6 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_7 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_8 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_9 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_10 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_11 = db.Column(db.String(5),unique=False,nullable=False,default='0')
	volume_month_12 = db.Column(db.String(5),unique=False,nullable=False,default='0')

	clients = db.relationship("Client",secondary='users_favs',back_populates="fruits")

class Client(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(20),unique=True,nullable=False)
	country = db.Column(db.String(20),unique=False,nullable=False)
	city = db.Column(db.String(20),unique=False,nullable=False)
	gender = db.Column(db.String(20),unique=False,nullable=False)
	
	fruit_currency_preference_1 = db.Column(db.String(10),unique=False,nullable=False)
	fruit_currency_preference_2 = db.Column(db.String(10),unique=False,nullable=False)
	fruit_currency_preference_3 = db.Column(db.String(10),unique=False,nullable=False)

	fruit_size_preference_1 = db.Column(db.String(10),unique=False,nullable=False)
	fruit_size_preference_2 = db.Column(db.String(10),unique=False,nullable=False)
	fruit_size_preference_3 = db.Column(db.String(10),unique=False,nullable=False)
	
	fruit_type_preference_1 = db.Column(db.String(10),unique=False,nullable=False)
	fruit_type_preference_2 = db.Column(db.String(10),unique=False,nullable=False)

	fruits = db.relationship("Fruit",secondary='users_favs',back_populates="clients")
	

class EuroToStrling(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	price = db.Column(db.String(5),nullable=False)

class EuroToDollars(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	price = db.Column(db.String(5),nullable=False)
	

