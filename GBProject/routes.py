from flask import render_template, url_for, flash, redirect, request
from GBProject import app,db,engine
import pandas as pd
from GBProject.models import Fruit,Client,EuroToStrling,EuroToDollars,UsersFavs
from GBProject.forms import FruitSearchForm,FruitAddForm,UserSearchForm,ClientEditForm,AveragesForm,ClientAddForm,Translate
import matplotlib.pyplot as plt
import numpy as np
import secrets
import os
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import goslate



def save_file(form_file):
	random_hex = secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_file.filename)
	file_name = random_hex + f_ext
	file_path = os.path.join(app.root_path,'static/uploads',file_name)
	form_file.save(file_path)
	return file_name,file_path


@app.route("/",methods=['GET','POST'])
def hello():
	Avform = AveragesForm()
	if(Avform.validate_on_submit()):
		#check if the uer has submitted values correcty
		return "Clicked"
	return render_template('home.html',title="Home Page",Avform=Avform)


@app.route("/testBokeh",methods=['GET','POST'])
def testBokeh():
	fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
	counts = [5, 3, 4, 2, 4, 6]
	p = figure(x_range=fruits, plot_height=250, title="Fruit Counts")
	p.vbar(x=fruits, top=counts, width=0.9)
	
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()

    # render template
	script, div = components(p)
	return render_template('bokeh.html',plot_script=script,plot_div=div,js_resources=js_resources,css_resources=css_resources,)


@app.route("/clients",methods = ['GET','POST'])
def clients():
	empty = '0';
	form = UserSearchForm()
	if request.method == 'POST':
		clients = Client.query.filter_by(name=str(form.search_field.data).capitalize()).all()
		if len(clients) == 0:
			empty = '1'
		return render_template('clients.html',form=form,empty=empty,clients = clients)
	return render_template('clients.html',form=form)

@app.route("/clients_display/<client_id>",methods=['GET','POST'])
def clients_display(client_id):
	form = ClientEditForm()
	error = 0
	client = Client.query.filter_by(id=int(client_id)).first()
	if form.validate_on_submit():
		#we have to upload update data
		if client.name != str(form.name.data).capitalize():
			client2 = Client.query.filter_by(name=str(form.name.data).capitalize()).first()
			if client2:
				error = 1
				flash('Name already exists','danger')

		if str(form.currency_pref1.data) == str(form.currency_pref3.data) and str(form.currency_pref1.data) != str(form.currency_pref2.data):
			error = 1
			flash('Currency Prefrences are not logical','danger')

		elif form.size_pref1.data == form.size_pref3.data and form.size_pref1.data != form.size_pref2.data:
			error = 1
			flash('Size Prefrences are not logical','danger')

		if error == 0:
			client.name = str(form.name.data).capitalize()
			client.country = str(form.country.data).capitalize()
			client.city = str(form.city.data).capitalize()
			client.gender = str(form.gender.data)
			
			client.fruit_currency_preference_1 = str(form.currency_pref1.data).lower()
			client.fruit_currency_preference_2 = str(form.currency_pref2.data).lower()
			client.fruit_currency_preference_3 = str(form.currency_pref3.data).lower()
			
			client.fruit_size_preference_1 = str(form.size_pref1.data).lower()
			client.fruit_size_preference_2 = str(form.size_pref2.data).lower()
			client.fruit_size_preference_3 = str(form.size_pref3.data).lower()

			client.fruit_type_preference_1 = str(form.type_pref1.data).lower()
			client.fruit_type_preference_2 = str(form.type_pref2.data).lower()

			db.session.commit()
			flash('Data Updated','success')
	form.name.data = client.name 
	form.country.data = client.country
	form.city.data = client.city
	form.gender.data = client.gender

	form.currency_pref1.data = client.fruit_currency_preference_1
	form.currency_pref2.data = client.fruit_currency_preference_2
	form.currency_pref3.data = client.fruit_currency_preference_3
	
	form.size_pref1.data = client.fruit_size_preference_1;
	form.size_pref2.data = client.fruit_size_preference_2;
	form.size_pref3.data = client.fruit_size_preference_3;

	form.type_pref1.data = client.fruit_type_preference_1
	form.type_pref2.data = client.fruit_type_preference_2

	mfruits = client.fruits

	mp = [None,None,None]
	eprices = [None]*len(mfruits)
	dprices = [None]*len(mfruits)
	sprices = [None]*len(mfruits)
	i = 0
	for f in mfruits:
		if f.currency == 'euro':
			eprices[i] = float(f.price_month_12)
			ed = float(EuroToDollars.query.filter_by(id = 12).first().price)
			dprices[i] = eprices[i]/ed
			es = float(EuroToStrling.query.filter_by(id = 12).first().price)
			sprices[i] = eprices[i]/es
			

		elif f.currency == 'dollar':
			dprices[i] = float(f.price_month_12)
			ed = float(EuroToDollars.query.filter_by(id = 12).first().price)
			eprices[i] = dprices[i]*ed
			es = float(EuroToStrling.query.filter_by(id = 12).first().price)
			sprices[i] = eprices[i]/es
			

		elif f.currency == 'sterling':
			sprices[i] = float(f.price_month_12)
			es = float(EuroToStrling.query.filter_by(id = 12).first().price)
			eprices[i] = sprices[i]*es
			ed = float(EuroToDollars.query.filter_by(id = 12).first().price)
			dprices[i] = eprices[i]/ed


		i = i+1
	dat = zip(mfruits,eprices,dprices,sprices)
	#price Evolution of the basket:
	basketPriceEuro = [None]*12
	basketPriceDollar = [None]*12
	basketPriceSterling = [None]*12

	for i in range(12):
		for f in mfruits:
			monthPrices = [float(f.price_month_1),float(f.price_month_2),float(f.price_month_3),float(f.price_month_4),float(f.price_month_5),float(f.price_month_6),float(f.price_month_7),float(f.price_month_8),float(f.price_month_9),float(f.price_month_10),float(f.price_month_11),float(f.price_month_12)]

			monthVolume = [float(f.volume_month_1),float(f.volume_month_2),float(f.volume_month_3),float(f.volume_month_4),float(f.volume_month_5),float(f.volume_month_6),float(f.volume_month_7),float(f.volume_month_8),float(f.volume_month_9),float(f.volume_month_10),float(f.volume_month_11),float(f.volume_month_12)]
			if f.currency == 'euro':
				basketPriceEuro[i] = monthPrices[i]*int(f.price_unit)*monthVolume[i]
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceDollar[i] = basketPriceEuro[i]/ed
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceSterling[i] = basketPriceEuro[i]/es
				

			elif f.currency == 'dollar':
				basketPriceDollar[i] = monthPrices[i]*int(f.price_unit)*monthVolume[i]
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceEuro[i] = basketPriceDollar[i]*ed
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceSterling[i] = basketPriceEuro[i]/es
				

			elif f.currency == 'sterling':
				basketPriceSterling[i] = monthPrices[i]*int(f.price_unit)*monthVolume[i]
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceEuro[i] = basketPriceSterling[i]*es
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceDollar[i] = basketPriceSterling[i]/ed

	months = np.array(range(1,13))
	if(client.fruit_currency_preference_1 == 'euro'):
		plt.plot(months,basketPriceEuro,label='Basket Price In Euro')
	elif(client.fruit_currency_preference_1 == 'dollar'):
		plt.plot(months,basketPriceDollar,label='Basket Price In Dollar')
	elif(client.fruit_currency_preference_1 == 'sterling'):
		plt.plot(months,basketPriceSterling,label='Basket Price In Sterling')
	plt.xlabel('Month')
	plt.legend(loc='upper left', shadow=True, fontsize='x-small')
	figloc = "GBProject/static/price_images/"+client.name+"PriceMost.jpg"
	fignameMost = "price_images/"+client.name+"PriceMost.jpg"
	plt.savefig(figloc)
	plt.gcf().clear()

	if(client.fruit_currency_preference_3 == 'euro'):
		plt.plot(months,basketPriceEuro,label='Basket Price In Euro')
	elif(client.fruit_currency_preference_3 == 'dollar'):
		plt.plot(months,basketPriceDollar,label='Basket Price In Dollar')
	elif(client.fruit_currency_preference_3 == 'sterling'):
		plt.plot(months,basketPriceSterling,label='Basket Price In Sterling')
	plt.xlabel('Month')
	plt.legend(loc='upper left', shadow=True, fontsize='x-small')
	figloc = "GBProject/static/price_images/"+client.name+"PriceLeast.jpg"
	fignameLeast = "price_images/"+client.name+"PriceLeast.jpg"
	plt.savefig(figloc)
	plt.gcf().clear()



	return render_template("clients_display.html",client=client,form=form,dat = dat,fignameMost=fignameMost,fignameLeast=fignameLeast,title=str(client.name))


def ComputeBaskets(client,start_month,end_month):
	mfruits = client.fruits
	#here we have a list mfruits of all the fruits in the client's basket
	basketPriceEuro = [None]*((end_month - start_month) + 1)
	basketPriceDollar = [None]*((end_month - start_month) + 1)
	basketPriceSterling = [None]*((end_month - start_month) + 1)
	euroPrices = 0
	dollarPrices = euroPrices
	sterlingPrices = euroPrices

	for i in range(start_month-1,end_month):
		for f in mfruits:
			monthPrices = [float(f.price_month_1),float(f.price_month_2),float(f.price_month_3),float(f.price_month_4),float(f.price_month_5),float(f.price_month_6),float(f.price_month_7),float(f.price_month_8),float(f.price_month_9),float(f.price_month_10),float(f.price_month_11),float(f.price_month_12)]
			monthVolume = [float(f.volume_month_1),float(f.volume_month_2),float(f.volume_month_3),float(f.volume_month_4),float(f.volume_month_5),float(f.volume_month_6),float(f.volume_month_7),float(f.volume_month_8),float(f.volume_month_9),float(f.volume_month_10),float(f.volume_month_11),float(f.volume_month_12)]
			if f.currency == 'euro':
				euroPrices = euroPrices + monthPrices[i]*monthVolume[i]
				basketPriceEuro[i - start_month -1] = monthPrices[i]*monthVolume[i]
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceDollar[i - start_month -1] = basketPriceEuro[i - start_month -1]/ed
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceSterling[i - start_month -1] = basketPriceEuro[i - start_month -1]/es
				

			elif f.currency == 'dollar':
				basketPriceDollar[i - start_month -1] = monthPrices[i]*monthVolume[i]
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceEuro[i - start_month -1] = basketPriceDollar[i - start_month -1]*ed
				dollarPrices = dollarPrices + basketPriceEuro[i - start_month -1]
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceSterling[i - start_month -1] = basketPriceEuro[i - start_month -1]/es
				

			elif f.currency == 'sterling':
				basketPriceSterling[i - start_month -1] = monthPrices[i]*monthVolume[i]
				es = float(EuroToStrling.query.filter_by(id = i+1).first().price)
				basketPriceEuro[i - start_month -1] = basketPriceSterling[i - start_month -1]*es
				sterlingPrices = sterlingPrices + basketPriceEuro[i - start_month -1]
				ed = float(EuroToDollars.query.filter_by(id = i+1).first().price)
				basketPriceDollar[i - start_month -1] = basketPriceSterling[i - start_month -1]/ed


	euroPrices = euroPrices/(end_month - start_month + 1)
	dollarPrices = dollarPrices/(end_month - start_month + 1)
	sterlingPrices = sterlingPrices/(end_month - start_month + 1)
	return basketPriceEuro,mfruits,euroPrices,dollarPrices,sterlingPrices

@app.route("/add_clients",methods=['GET','POST'])
def add_clients():
	form = ClientAddForm()
	list_of_sizeprefs = ['small','medium','large']
	list_of_currprefs = ['euro','dollar','sterling']
	list_of_typeprefs = ['size','currency']
	list_of_countries = ['France','Germany','Luxembourg']
	list_of_genders = ['male','female']
	if form.validate_on_submit():
		file,path = save_file(form.file_field.data)
		error = 0
		try:
			df = pd.read_csv(path,dtype={'id':int,'name':str,'country':str,'city':str,'gender':str,
					'fruit_currency_preference_1':str,'fruit_currency_preference_2':str,'fruit_currency_preference_3':str,
					'fruit_size_preference_1':str,'fruit_size_preference_2':str,'fruit_size_preference_3':str,
					'fruit_type_preference_1':str,'fruit_type_preference_1':str
					})
			count = len(Client.query.all())
			df['id'] = int(df['id']) + count
			for index, row in df.iterrows():
				df['name'][index] = df['name'][index].capitalize()
				df['country'][index] = df['country'][index].capitalize()
				df['gender'][index] = df['gender'][index].lower()
				if(df['gender'][index] not in list_of_genders):
					error = 6
					break
				if(df['country'][index] not in list_of_countries):
					error = 5
					break
				df['fruit_type_preference_1'][index] = df['fruit_type_preference_1'][index].lower()
				df['fruit_type_preference_2'][index] = df['fruit_type_preference_2'][index].lower()
				if (df['fruit_type_preference_1'][index] not in list_of_typeprefs or df['fruit_type_preference_2'][index] not in list_of_typeprefs):
					error = 2
					break

				df['fruit_size_preference_1'][index] = df['fruit_size_preference_1'][index].lower()
				df['fruit_size_preference_2'][index] = df['fruit_size_preference_2'][index].lower()
				df['fruit_size_preference_3'][index] = df['fruit_size_preference_3'][index].lower()

				if (df['fruit_size_preference_1'][index] not in list_of_sizeprefs or df['fruit_size_preference_2'][index] not in list_of_sizeprefs or df['fruit_size_preference_3'][index] not in list_of_sizeprefs):
					error = 3
					break

				df['fruit_currency_preference_1'][index] = df['fruit_currency_preference_1'][index].lower()
				df['fruit_currency_preference_2'][index] = df['fruit_currency_preference_2'][index].lower()
				df['fruit_currency_preference_3'][index] = df['fruit_currency_preference_3'][index].lower()

				if (df['fruit_currency_preference_1'][index] not in list_of_currprefs or df['fruit_currency_preference_2'][index] not in list_of_currprefs or df['fruit_currency_preference_3'][index] not in list_of_currprefs):
					error = 4
					break

				client = Client.query.filter_by(name=df['name'][index]).first()
				if (client is not None):
						error = 1
						break
			if error == 1:
				flash("Client Already Exists at row : "+str(index)+" Client Name : "+df['name'][index],'danger')
			elif error == 2:
				flash("Text entered in type pref at line "+ str(index) +" is not supported",'danger')
			elif error == 3:
				flash("Text entered in size pref at line "+ str(index) +" is not supported",'danger')
			elif error == 4:
				flash("Text entered in currency pref at line "+ str(index) +" is not supported",'danger')
			elif error == 5:
				flash("Text entered in country at line "+ str(index) +" is not supported",'danger')
			elif error == 6:
				flash("Text entered in gender at line "+ str(index) +" is not supported",'danger')
			else:	
				df.to_sql(name='client',con=engine,if_exists='append',index=False)
				#update the data in users_favs
				FillUsersFavs()
				flash('submitted','success')

		except Exception as e:
			flash(repr(e),'danger')
	else:
		for error in form.file_field.errors:
			flash(str(error),'danger')
	return render_template('add_clients.html',form = form,title="Add Clients")


@app.route("/add_fruits",methods=['GET','POST'])
def add_fruits():
	form = FruitAddForm()
	list_of_size = ['small','medium','large']
	list_of_curr = ['euro','dollar','sterling']
	list_of_countries = ['France','Germany','Luxembourg']
	list_of_metric = ['number','weight']
	if form.validate_on_submit():
		if form.file_field.data:
		#flash('submitted','success')
			file,path = save_file(form.file_field.data)
			error = 0;
			try :
				df = pd.read_csv(path,dtype={'id':int,'name':str,'prohibited_country':str,'metric':str,'size':str,
					'currency':str,'price_unit':float,
					'price_month_1':float ,'price_month_2':float,'price_month_3':float,'price_month_4':float,
					'price_month_5':float,'price_month_6':float,'price_month_7':float,'price_month_8':float,
					'price_month_9':float,'price_month_10':float,'price_month_11':float,'price_month_12':float,
					'volume_month_1':int ,'volume_month_2':int,'volume_month_3':int,'volume_month_4':int,
					'volume_month_5':int ,'volume_month_6':int,'volume_month_7':int,'volume_month_8':int,
					'volume_month_9':int ,'volume_month_10':int,'volume_month_11':int,'volume_month_12':int,
					})
				con = engine.connect()
				res = con.execute("select max(id) from fruit")
				max_id = 0
				for raw in res:
					max_id = int(raw[0])
				con.close()
				df['id'] = int(df['id']) + max_id
				for index, row in df.iterrows():
					df['name'][index] = df['name'][index].capitalize()
					
					df['prohibited_country'][index] = df['prohibited_country'][index].capitalize()
					if(df['prohibited_country'][index] not in list_of_countries):
						error = 5
					
					df['metric'][index] = df['metric'][index].lower()
					if(df['metric'][index] not in list_of_metric):
						error = 4
					
					df['size'][index] = df['size'][index].lower()
					if(df['size'][index] not in list_of_size):
						error = 3
					
					df['currency'][index] = df['currency'][index].lower()
					if(df['currency'][index] not in list_of_curr):
						error = 2

					fruit = Fruit.query.filter_by(name=row['name']).first()
					
					if (fruit is not None):
						error = 1
						break

				if error == 1:
					flash("Fruit Already Exists at row : "+str(index)+" Fruit Name : "+row['name'],'danger')
				elif error == 2:
					flash("Text you've entered in currency at line "+str(index)+" is not supported",'danger')
				elif error == 3:
					flash("Text you've entered in size at line "+str(index)+" is not supported",'danger')
				elif error == 4:
					flash("Text you've entered in metric at line "+str(index)+" is not supported",'danger')
				elif error == 5:
					flash("Text you've entered in prohibited_country at line "+str(index)+" is not supported",'danger')
				else:	
					df.to_sql(name='fruit',con=engine,if_exists='append',index=False)
					flash('submitted','success')
			except Exception as e:
				flash(repr(e),'danger')
	else :
		for error in form.file_field.errors:
			flash(str(error),'danger')
	return render_template('add_fruits.html',title="Add Fruits",form=form)


@app.route("/fruits",methods=['GET','POST'])
def fruits():
	form = FruitSearchForm()
	if(request.method == 'POST'):
		#we need to get the data
		#connection = engine.connect()
		if(form.search_filter.data == "id"):
			fruits = Fruit.query.filter_by(id=form.search_field.data).all()
		elif(form.search_filter.data == "name"):
			fruits = Fruit.query.filter_by(name=form.search_field.data).all()
		elif(form.search_filter.data == "proh_count"):
			fruits = Fruit.query.filter_by(prohibited_country=form.search_field.data).all()
		elif(form.search_filter.data == "curr"):
			fruits = Fruit.query.filter_by(currency=form.search_field.data).all()
		elif(form.search_filter.data == "size"):
			fruits = Fruit.query.filter_by(size=form.search_field.data).all()
		elif(form.search_filter.data == "metric"):
			fruits = Fruit.query.filter_by(size=form.search_field.data).all()
		if(len(fruits) == 0):
			return render_template('fruits.html',form=form,empty='1')	
		return render_template('fruits.html',form=form,fruits=fruits)
		#return fruits[0].name
	return render_template('fruits.html',form=form)

@app.route("/fruit_display/<fruit_id>",methods=['GET','POST'])
def fruit_display(fruit_id):
	fruit = Fruit.query.filter_by(id=fruit_id).first()
	clients = Client.query.filter(Client.country != fruit.prohibited_country).all()
	if(fruit.currency == "euro"):
		prices = np.array([fruit.price_month_1, fruit.price_month_2,fruit.price_month_3,fruit.price_month_4,fruit.price_month_5,fruit.price_month_6,fruit.price_month_7,fruit.price_month_8,fruit.price_month_9,fruit.price_month_10,fruit.price_month_11,fruit.price_month_12])
		prices = prices.astype(float)
		months = np.array(range(1,13))
		plt.plot(months,prices,label='Price In Euro')
		eds = EuroToDollars.query.all()
		etd = np.array(range(1,13),dtype=float)
		i = 0
		for ed in eds:
			etd[i] = prices[i]/float(ed.price)
			i = i+1
		plt.plot(months,etd,label='Price In Dollars')
		ess = EuroToStrling.query.all()
		ets = np.array(range(1,13),dtype=float)
		i = 0
		for es in ess:
			ets[i] = prices[i]/float(es.price)
			i = i+1
		plt.plot(months,ets,label='Price In Sterling')
		plt.xlabel('Month')
		plt.legend(loc='upper left', shadow=True, fontsize='x-small')
		figloc = "GBProject/static/price_images/"+fruit.name+"Price.jpg"
		figname = "price_images/"+fruit.name+"Price.jpg"
		plt.savefig(figloc)
		plt.gcf().clear()
	if(fruit.currency == "dollar"):
		prices = np.array([fruit.price_month_1, fruit.price_month_2,fruit.price_month_3,fruit.price_month_4,fruit.price_month_5,fruit.price_month_6,fruit.price_month_7,fruit.price_month_8,fruit.price_month_9,fruit.price_month_10,fruit.price_month_11,fruit.price_month_12])
		prices = prices.astype(float)
		months = np.array(range(1,13))
		plt.plot(months,prices,label='Price In Dollars')
		eds = EuroToDollars.query.all()
		etd = np.array(range(1,13),dtype=float)
		i = 0
		for ed in eds:
			prices[i] = prices[i]*float(ed.price)
			i = i+1
		plt.plot(months,prices,label='Price In Euro')
		ess = EuroToStrling.query.all()
		ets = np.array(range(1,13),dtype=float)
		i = 0
		for es in ess:
			ets[i] = prices[i]/float(es.price)
			i = i+1
		plt.plot(months,ets,label='Price In Sterling')
		plt.xlabel('Month')
		plt.legend(loc='upper left', shadow=True, fontsize='x-small')
		figloc = "GBProject/static/price_images/"+fruit.name+"Price.jpg"
		figname = "price_images/"+fruit.name+"Price.jpg"
		plt.savefig(figloc)
		plt.gcf().clear()
	if(fruit.currency == "sterling"):
		prices = np.array([fruit.price_month_1, fruit.price_month_2,fruit.price_month_3,fruit.price_month_4,fruit.price_month_5,fruit.price_month_6,fruit.price_month_7,fruit.price_month_8,fruit.price_month_9,fruit.price_month_10,fruit.price_month_11,fruit.price_month_12])
		prices = prices.astype(float)
		months = np.array(range(1,13))
		plt.plot(months,prices,label='Price In Sterling')
		ess = EuroToStrling.query.all()
		ets = np.array(range(1,13),dtype=float)
		i = 0
		for es in ess:
			prices[i] = prices[i]*float(es.price)
			i = i+1
		plt.plot(months,prices,label='Price In Euro')
		eds = EuroToDollars.query.all()
		etd = np.array(range(1,13),dtype=float)
		i = 0
		for ed in eds:
			prices[i] = prices[i]/float(ed.price)
			i = i+1
		plt.plot(months,prices,label='Price In Dollars')
		
		plt.xlabel('Month')
		plt.legend(loc='upper left', shadow=True, fontsize='x-small')
		figloc = "GBProject/static/price_images/"+fruit.name+"Price.jpg"
		figname = "price_images/"+fruit.name+"Price.jpg"
		plt.savefig(figloc)
		plt.gcf().clear()

	return render_template('fruits_display.html',fruit=fruit,title=fruit.name,clients=clients,figname=figname)


@app.route("/Top5s",methods=['GET','POST'])
def top5():
	clients = Client.query.all()
	
	countFrance = [0]*(len(Fruit.query.all()))
	countFrance = np.asarray(countFrance)
	countGermany = np.asarray([0]*(len(Fruit.query.all())))
	countLux = np.asarray([0]*(len(Fruit.query.all())))
	countMale = np.asarray([0]*(len(Fruit.query.all())))
	countFemale = np.asarray([0]*(len(Fruit.query.all())))
	countEuro = np.asarray([0]*(len(Fruit.query.all())))
	countDollar = np.asarray([0]*(len(Fruit.query.all())))
	countSterling = np.asarray([0]*(len(Fruit.query.all())))
	
	for client in clients:
		mfruits = client.fruits
		for f in mfruits:
			if f.currency == 'euro':
				countEuro[int(f.id) - 1] = countEuro[int(f.id) - 1] + 1
			if f.currency == 'dollar':
				countDollar[int(f.id) - 1] = countDollar[int(f.id) - 1] + 1
			if f.currency == 'sterling':
				countSterling[int(f.id) - 1] = countSterling[int(f.id) - 1] + 1

		if(client.country == 'France'):
			for f in mfruits:
				countFrance[int(f.id) - 1] = countFrance[int(f.id) - 1] + 1
		elif(client.country == 'Germany'):
			for f in mfruits:
				countGermany[int(f.id) - 1] = countGermany[int(f.id) - 1] + 1
		elif(client.country == 'Luxembourg'):
			for f in mfruits:
				countLux[int(f.id) - 1] = countLux[int(f.id) - 1] + 1

		if(client.gender == 'male'):
			for f in mfruits:
				countMale[int(f.id) - 1] = countMale[int(f.id) - 1] + 1

		elif(client.gender == 'female'):
			for f in mfruits:
				countFemale[int(f.id) - 1] = countFemale[int(f.id) - 1] + 1

	coutEuroId = countEuro.argsort()
	coutEuroId = np.flip(coutEuroId,0)[0:5]

	coutDollarId = countDollar.argsort()
	coutDollarId = np.flip(coutDollarId,0)[0:5]

	coutSterlingId = countSterling.argsort()
	coutSterlingId = np.flip(coutSterlingId,0)[0:5]

	coutFranceId = countFrance.argsort()
	coutFranceId = np.flip(coutFranceId,0)[0:5]

	coutGermanyId = countGermany.argsort()
	coutGermanyId = np.flip(coutGermanyId,0)[0:5]


	coutLuxId = countLux.argsort()
	coutLuxId = np.flip(coutLuxId,0)[0:5]

	coutMaleId = countMale.argsort()
	coutMaleId = np.flip(coutMaleId,0)[0:5]

	coutFemaleId = countFemale.argsort()
	coutFemaleId = np.flip(coutFemaleId,0)[0:5]

	franceTopFruits = [Fruit]*5
	GermanyTopFruits = [Fruit]*5
	LuxTopFruits = [Fruit]*5

	MaleTopFruits = [Fruit]*5
	FemaleTopFruits = [Fruit]*5

	EuroTopFruits = [Fruit]*5
	DollarTopFruits = [Fruit]*5
	SterlingTopFruits = [Fruit]*5


	for i in range(5):
		franceTopFruits[i] 	= Fruit.query.filter_by(id=str(coutFranceId[i] + 1)).first()
		GermanyTopFruits[i] = Fruit.query.filter_by(id=str(coutGermanyId[i] + 1)).first()
		LuxTopFruits[i] 	= Fruit.query.filter_by(id=str(coutLuxId[i] + 1)).first()
		MaleTopFruits[i]	= Fruit.query.filter_by(id=str(coutMaleId[i] + 1)).first()
		FemaleTopFruits[i]	= Fruit.query.filter_by(id=str(coutFemaleId[i] + 1)).first()
		EuroTopFruits[i] 	= Fruit.query.filter_by(id=str(coutEuroId[i] + 1)).first()
		DollarTopFruits[i] 	= Fruit.query.filter_by(id=str(coutDollarId[i] + 1)).first()
		SterlingTopFruits[i] 	= Fruit.query.filter_by(id=str(coutSterlingId[i] + 1)).first()



	namesTopFrance 	= [franceTopFruits[0].name,franceTopFruits[1].name,franceTopFruits[2].name,franceTopFruits[3].name,franceTopFruits[4].name]
	namesTopGermany = [GermanyTopFruits[0].name,GermanyTopFruits[1].name,GermanyTopFruits[2].name,GermanyTopFruits[3].name,GermanyTopFruits[4].name]
	namesTopLux 	= [LuxTopFruits[0].name,LuxTopFruits[1].name,LuxTopFruits[2].name,LuxTopFruits[3].name,LuxTopFruits[4].name]
	namesTopMale	= [MaleTopFruits[0].name,MaleTopFruits[1].name,MaleTopFruits[2].name,MaleTopFruits[3].name,MaleTopFruits[4].name]
	namesTopFemale	= [FemaleTopFruits[0].name,FemaleTopFruits[1].name,FemaleTopFruits[2].name,FemaleTopFruits[3].name,FemaleTopFruits[4].name]
	namesTopEuro 	= [EuroTopFruits[0].name,EuroTopFruits[1].name,EuroTopFruits[2].name,EuroTopFruits[3].name,EuroTopFruits[4].name]
	namesTopDollar	= [DollarTopFruits[0].name,DollarTopFruits[1].name,DollarTopFruits[2].name,DollarTopFruits[3].name,DollarTopFruits[4].name]
	namesTopSterling= [SterlingTopFruits[0].name,SterlingTopFruits[1].name,SterlingTopFruits[2].name,SterlingTopFruits[3].name,SterlingTopFruits[4].name]

	valTopFrance 	= [countFrance[coutFranceId[0]],countFrance[coutFranceId[1]],countFrance[coutFranceId[2]],countFrance[coutFranceId[3]],countFrance[coutFranceId[4]]]
	valTopGermany 	= [countGermany[coutGermanyId[0]],countGermany[coutGermanyId[1]],countGermany[coutGermanyId[2]],countGermany[coutGermanyId[3]],countGermany[coutGermanyId[4]]]
	valTopLux		= [countLux[coutLuxId[0]],countLux[coutLuxId[1]],countLux[coutLuxId[2]],countLux[coutLuxId[3]],countLux[coutLuxId[4]]]
	valTopMale		= [countMale[coutMaleId[0]],countMale[coutMaleId[1]],countMale[coutMaleId[2]],countMale[coutMaleId[3]],countMale[coutMaleId[4]]]
	valTopFemale 	= [countFemale[coutFemaleId[0]],countFemale[coutFemaleId[1]],countFemale[coutFemaleId[2]],countFemale[coutFemaleId[3]],countFemale[coutFemaleId[4]]]
	valTopEuro		= [countEuro[coutEuroId[0]],countEuro[coutEuroId[1]],countEuro[coutEuroId[2]],countEuro[coutEuroId[3]],countEuro[coutEuroId[4]]]
	valTopDollar 	= [countDollar[coutDollarId[0]],countDollar[coutDollarId[1]],countDollar[coutDollarId[2]],countDollar[coutDollarId[3]],countDollar[coutDollarId[4]]]
	valTopSterling  = [countSterling[coutSterlingId[0]],countSterling[coutSterlingId[1]],countSterling[coutSterlingId[2]],countSterling[coutSterlingId[3]],countSterling[coutSterlingId[4]]]


	p = figure(x_range=namesTopFrance, plot_height=250, title="Top 5 Fruits in France")
	p.vbar(x=namesTopFrance, top=valTopFrance, width=0.4)
		
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()

	    # render template
	scriptFrance, divFrance = components(p)

	p2 = figure(x_range=namesTopGermany, plot_height=250, title="Top 5 Fruits in Germany")
	p2.vbar(x=namesTopGermany, top=valTopGermany, width=0.4)
		
	js_resources2 = INLINE.render_js()
	css_resources2 = INLINE.render_css()

	    # render template
	scriptGermany, divGermany = components(p2)

	p3 = figure(x_range=namesTopLux, plot_height=250, title="Top 5 Fruits in Luxembourg")
	p3.vbar(x=namesTopLux, top=valTopLux, width=0.4)
		
	js_resources3 = INLINE.render_js()
	css_resources3 = INLINE.render_css()

	    # render template
	scriptLux, divLux = components(p3)

	p4 = figure(x_range=namesTopMale, plot_height=250, title="Top 5 Fruits for Males")
	p4.vbar(x=namesTopMale, top=valTopMale, width=0.4)
		
	js_resources4 = INLINE.render_js()
	css_resources4 = INLINE.render_css()

	    # render template
	scriptMale, divMale = components(p4)
	
	p5 = figure(x_range=namesTopFemale, plot_height=250, title="Top 5 Fruits for Females")
	p5.vbar(x=namesTopFemale, top=valTopFemale, width=0.4)
		
	js_resources5 = INLINE.render_js()
	css_resources5 = INLINE.render_css()

	    # render template
	scriptFemale, divFemale = components(p5)

	p6 = figure(x_range=namesTopEuro, plot_height=250, title="Top 5 Fruits in Euro")
	p6.vbar(x=namesTopEuro, top=valTopEuro, width=0.4)

	js_resources6 = INLINE.render_js()
	css_resources6 = INLINE.render_css()

	scriptEuro, divEuro = components(p6)


	p7 = figure(x_range=namesTopDollar, plot_height=250, title="Top 5 Fruits in Dollar")
	p7.vbar(x=namesTopDollar, top=valTopDollar, width=0.4)

	scriptDollar, divDollar = components(p7)

	p8 = figure(x_range=namesTopSterling, plot_height=250, title="Top 5 Fruits in Sterling")
	p8.vbar(x=namesTopSterling, top=valTopSterling, width=0.4)

	scriptSterling, divSterling = components(p8)

	return render_template('top5.html',title="Top 5",ready='1',divEuro=divEuro,scriptEuro=scriptEuro,divDollar=divDollar,scriptDollar=scriptDollar,divSterling=divSterling,scriptSterling=scriptSterling,css_resources4=css_resources4,js_resources4=js_resources4,css_resources5=css_resources5,js_resources5=js_resources5,divMale=divMale,scriptMale=scriptMale,divFemale=divFemale,scriptFemale=scriptFemale,divFrance = divFrance,divGermany=divGermany,divLux=divLux,scriptGermany=scriptGermany,scriptFrance=scriptFrance,scriptLux = scriptLux,js_resources=js_resources,css_resources=css_resources,js_resources2=js_resources2,css_resources2=css_resources2,js_resources3=js_resources3,css_resources3=css_resources3)


@app.route("/Averages",methods=['GET','POST'])
def averages():
	form = AveragesForm()

	if(form.validate_on_submit()):
		if(int(form.end_month.data) < int(form.start_month.data)):
			flash('End month can not be before the start month','danger')
			return render_template('averages.html',title="Avergaes Page",form=form,ready='0')
		
		

		pFrance = [0]*(int(form.end_month.data) -  int(form.start_month.data) + 1)
		pFrance = np.asarray(pFrance)
		pGermany = np.asarray([0]*(int(form.end_month.data) -  int(form.start_month.data) + 1))
		pLux = np.asarray([0]*(int(form.end_month.data) -  int(form.start_month.data) + 1))
		
		pMale = np.asarray([0]*(int(form.end_month.data) -  int(form.start_month.data) + 1))
		pFemale = np.asarray([0]*(int(form.end_month.data) -  int(form.start_month.data) + 1))
		
		clients = Client.query.all()
		for client in clients:
			#countries
			temp,mfruits,euroPrices,dollarPrices,sterlingPrices =  ComputeBaskets(client,int(form.start_month.data),int(form.end_month.data))
			if(client.country == 'France'):
				pFrance = pFrance + np.asarray(temp)
			elif(client.country == 'Germany'):
				pGermany = pGermany + np.asarray(temp)
			elif(client.country == 'Luxembourg'):
				pLux = pLux + np.asarray(temp)
			if(client.gender == 'male'):
				pMale = pMale + np.asarray(temp)
			elif(client.gender == 'female'):
				pFemale = pFemale + np.asarray(temp)
		countries = ['France', 'Germany', 'Luxembourg']
		genders = ['Female','Male']
		pricesGen = [np.average(pFemale),np.average(pMale)]
		prices = [np.average(pFrance),np.average(pGermany),np.average(pLux)]
		currencies = ['Euro','Dollar','Sterling']
		pricesCurr = [euroPrices,dollarPrices,sterlingPrices]

		p = figure(x_range=countries, plot_height=250, title="Average By Country")
		p.vbar(x=countries, top=prices, width=0.4)
		
		js_resources = INLINE.render_js()
		css_resources = INLINE.render_css()

	    # render template
		scriptCountries, divCountries = components(p)

		p2 = figure(x_range=genders, plot_height=250, title="Average By Gender")
		p2.vbar(x=genders, top=pricesGen, width=0.4)
		
		js_resources2 = INLINE.render_js()
		css_resources2 = INLINE.render_css()

	    # render template
		scriptGenders, divGenders = components(p2)

		p3 = figure(x_range=currencies, plot_height=250, title="Average By Gender")
		p3.vbar(x=currencies, top=pricesCurr, width=0.4)
		
		js_resources3 = INLINE.render_js()
		css_resources3 = INLINE.render_css()

	    # render template
		scriptCurr, divCurr = components(p3)
		
		return render_template('averages.html',title="Avergaes Page",form=form,ready='1',divCountries=divCountries,scriptCountries=scriptCountries,js_resources=js_resources,css_resources=css_resources,js_resources2=js_resources2,css_resources2=css_resources2,divGenders=divGenders,scriptGenders=scriptGenders,js_resources3=js_resources3,css_resources3=css_resources3,divCurr=divCurr,scriptCurr=scriptCurr)

	return render_template('averages.html',title="Avergaes Page",form=form,ready='0')



@app.route("/showAllFruits")
def showAllFruits():
	fruits = Fruit.query.all()
	return render_template('show_all_fruits.html',fruits=fruits,title="All Fruits")

@app.route("/showAllClients")
def showAllClients():
	clients = Client.query.all()
	return render_template('show_all_clients.html',clients=clients,title="All Clients")

@app.route("/about",methods=['GET','POST'])
def about():
	form = Translate()
	texts = ['This project is form GoldBaum','This project is done by Jad OBEID']
	if(form.validate_on_submit() and form.french.data):
		gs = goslate.Goslate()
		for i in range(len(texts)):
			texts[i] = gs.translate(texts[i],'fr')
	return render_template('about.html',texts=texts,form=form)

@app.route("/reset")
def reset_db():
	db.drop_all()
	db.create_all()
	#loc = url_for('static',filename='fruits.csv')
	loc = os.getcwd()+"/GBProject/static/fruits.csv"
	dfFr = pd.read_csv(loc)
	dfFr.to_sql(name='fruit',con=engine,if_exists='append',index=False)

	loc = os.getcwd()+"/GBProject/static/clients.csv"
	dfCli = pd.read_csv(loc)
	dfCli.to_sql(name='client',con=engine,if_exists='append',index=False)

	loc = os.getcwd()+"/GBProject/static/currencies.csv"
	dfCur = pd.read_csv(loc)

	ed1 = EuroToDollars(price=dfCur['euro_month_1'][2])
	ed2 = EuroToDollars(price=dfCur['euro_month_2'][2])
	ed3 = EuroToDollars(price=dfCur['euro_month_3'][2])
	ed4 = EuroToDollars(price=dfCur['euro_month_4'][2])
	ed5 = EuroToDollars(price=dfCur['euro_month_5'][2])
	ed6 = EuroToDollars(price=dfCur['euro_month_6'][2])
	ed7 = EuroToDollars(price=dfCur['euro_month_7'][2])
	ed8 = EuroToDollars(price=dfCur['euro_month_8'][2])
	ed9 = EuroToDollars(price=dfCur['euro_month_9'][2])
	ed10 = EuroToDollars(price=dfCur['euro_month_10'][2])
	ed11 = EuroToDollars(price=dfCur['euro_month_11'][2])
	ed12 = EuroToDollars(price=dfCur['euro_month_12'][2])
	
	db.session.add(ed1)
	db.session.add(ed2)
	db.session.add(ed3)
	db.session.add(ed4)
	db.session.add(ed5)
	db.session.add(ed6)
	db.session.add(ed7)
	db.session.add(ed8)
	db.session.add(ed9)
	db.session.add(ed10)
	db.session.add(ed11)
	db.session.add(ed12)


	es1 = EuroToStrling(price=dfCur['euro_month_1'][1])
	es2 = EuroToStrling(price=dfCur['euro_month_2'][1])
	es3 = EuroToStrling(price=dfCur['euro_month_3'][1])
	es4 = EuroToStrling(price=dfCur['euro_month_4'][1])
	es5 = EuroToStrling(price=dfCur['euro_month_5'][1])
	es6 = EuroToStrling(price=dfCur['euro_month_6'][1])
	es7 = EuroToStrling(price=dfCur['euro_month_7'][1])
	es8 = EuroToStrling(price=dfCur['euro_month_8'][1])
	es9 = EuroToStrling(price=dfCur['euro_month_9'][1])
	es10 = EuroToStrling(price=dfCur['euro_month_10'][1])
	es11 = EuroToStrling(price=dfCur['euro_month_11'][1])
	es12 = EuroToStrling(price=dfCur['euro_month_12'][1])
	
	db.session.add(es1)
	db.session.add(es2)
	db.session.add(es3)
	db.session.add(es4)
	db.session.add(es5)
	db.session.add(es6)
	db.session.add(es7)
	db.session.add(es8)
	db.session.add(es9)
	db.session.add(es10)
	db.session.add(es11)
	db.session.add(es12)
	FillUsersFavs()
	db.session.commit()
	flash('Done !','success')
	return redirect(url_for('hello'))
	
"""
	clients = Client.query.all()
	for client in clients:
		if client.fruit_type_preference_1 == 'size':
			fruits1 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits2 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits3 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits1 = fruits1 + fruits2 + fruits3

			fruits4 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits5 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits6 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.prohibited_country != client.country).all()
			ffruits2 = fruits4 + fruits5 + fruits6

			fruits7 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits8 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits9 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits3 = fruits7 + fruits8 + fruits9
			
			mfruits = ffruits1 + ffruits2 + ffruits3

		else:

			fruits1 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits2 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits3 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits1 = fruits1 + fruits2 + fruits3

			fruits4 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits5 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits6 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_1),Fruit.size != str(client.fruit_size_preference_2),Fruit.prohibited_country != client.country).all()
			ffruits2 = fruits4 + fruits5 + fruits6

			fruits7 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits8 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits9 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits3 = fruits7 + fruits8 + fruits9
		
			mfruits = ffruits1 + ffruits2 + ffruits3
		i = 1
		for fruit in mfruits:
			add = UsersFavs(client_id=int(client.id),fruit_id=int(fruit.id),pref_order=i)
			i = i + 1
			db.session.add(add)
"""
def FillUsersFavs():
	clients = Client.query.all()
	for client in clients:
		if client.fruit_type_preference_1 == 'size':
			fruits1 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits2 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits3 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits1 = fruits1 + fruits2 + fruits3

			fruits4 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits5 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits6 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.prohibited_country != client.country).all()
			ffruits2 = fruits4 + fruits5 + fruits6

			fruits7 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits8 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			fruits9 = Fruit.query.filter(Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits3 = fruits7 + fruits8 + fruits9
			
			mfruits = ffruits1 + ffruits2 + ffruits3

		else:

			fruits1 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits2 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits3 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits1 = fruits1 + fruits2 + fruits3

			fruits4 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits5 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits6 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_1),Fruit.size != str(client.fruit_size_preference_2),Fruit.prohibited_country != client.country).all()
			ffruits2 = fruits4 + fruits5 + fruits6

			fruits7 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits8 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			fruits9 = Fruit.query.filter(Fruit.currency == str(client.fruit_currency_preference_3),Fruit.currency != str(client.fruit_currency_preference_2),Fruit.currency != str(client.fruit_currency_preference_1),Fruit.size == str(client.fruit_size_preference_3),Fruit.size != str(client.fruit_size_preference_2),Fruit.size != str(client.fruit_size_preference_1),Fruit.prohibited_country != client.country).all()
			ffruits3 = fruits7 + fruits8 + fruits9
		
			mfruits = ffruits1 + ffruits2 + ffruits3
		i = 1
		for fruit in mfruits:
			add = UsersFavs(client_id=int(client.id),fruit_id=int(fruit.id),pref_order=i)
			i = i + 1
			db.session.add(add)
