
import pandas as pd 

df = pd.read_csv('clients.csv',dtype={'id':int,'name':str})
print df

