
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import webbrowser
import random
import string
reload(sys)
sys.setdefaultencoding( "gb2312" )

class Data_Parser(object):
	def __init__(self, the_df,add_code_IN = ''):
		self.df = the_df
		self.add_code = add_code_IN
		self.add_code_list = self.add_code.split('\n')

		self.datatype_dict = dict()

	def run_add_code(self):
		for add_code_item in (self.add_code_list):
			exec(add_code_item)

	def parser_procedure(self):
		self.df = self.df.dropna(axis = 1, how = 'all')
		self.run_add_code()

		for col in self.df.columns.values:
			switched = False
			datatype = self.df[col].dtype

			if datatype == np.dtype(np.int64):
				finaldatatype = "int"
			
			elif datatype == np.dtype(np.float64):
				finaldatatype = "float"
			
			elif datatype == np.dtype(np.object): #can be datetime, float64, object
				if not switched:
					try: # convert to datetime
						self.df[col] = pd.to_datetime(self.df[col])
						finaldatatype = 'datetime' #numpy does not contain any datetime data type in settings
						switched = True
					except:
						pass

				if not switched:
					try: # convert to float
						self.df[col] = self.df[col].astype(float)
						finaldatatype = "float"
						switched = True
					except:
						pass

				if not switched:
					try: # convert ##% to float
						self.df[col] = self.df[col].apply(lambda x: np.nan if x in ['-'] else x.strip('%')).astype(float)/100
						finaldatatype = "float"
						switched = True
					except:
						pass

				if not switched:
					finaldatatype = "string"
			
			self.datatype_dict[col] = finaldatatype
		
