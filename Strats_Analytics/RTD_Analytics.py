
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import webbrowser
import random
import string
from IO_Util import IO_Util
from Data_Parser import Data_Parser

reload(sys)
sys.setdefaultencoding( "gb2312" )

class RTD_Analytics(object):
	def __init__(self, the_rawtape,add_code_IN):
		self.rawtape = the_rawtape
		self.add_code = add_code_IN
		self.datatype_dict = dict()
		self.rtd_res = pd.DataFrame(columns = ['name','datatype','count','unique','mode','mean','std', 'min', '25%','50%','75%','max','sum'])
		self.data_parser = Data_Parser(self.rawtape,self.add_code)

	def analytics_procedure(self):
		self.data_parser.parser_procedure()
		self.rawtape = self.data_parser.df
		self.datatype_dict = self.data_parser.datatype_dict

		for key,value in self.datatype_dict.items():
			idx = len(self.rtd_res)
			self.rtd_res.loc[idx] = np.nan
			self.rtd_res.loc[idx]['name'] = key
			self.rtd_res.loc[idx]['datatype'] = value

			desc = self.rawtape[key].describe(include = 'all')

			if value == "string":			
				min_val,max_value = self.rawtape[key].min(),self.rawtape[key].max()
				self.rtd_res.loc[idx]['count','unique','mode','min','max'] = list(desc[['count','unique','top']].values) + [min_val,max_value]

			if value == "float":
				sum_val, mode_val, unique_val = self.rawtape[key].sum(), self.rawtape[key].mode()[0], len(self.rawtape[key].unique())
				self.rtd_res.loc[idx]['count','mean','std','min', '25%','50%','75%','max'] = desc[['count','mean','std','min', '25%','50%','75%','max']].values
				self.rtd_res.loc[idx]['sum','unique','mode'] = [sum_val, unique_val,mode_val]

			if value == "int":
				sum_val, mode_val, unique_val = self.rawtape[key].sum(), self.rawtape[key].mode()[0], len(self.rawtape[key].unique())
				self.rtd_res.loc[idx]['count','mean','std','min', '25%','50%','75%','max'] = desc[['count','mean','std','min', '25%','50%','75%','max']].values
				self.rtd_res.loc[idx]['sum','unique','mode'] = [sum_val, unique_val,mode_val]

			if value == "datetime":
				self.rtd_res.loc[idx]['count','unique','mode','min','max'] = desc[['count','unique','top','first', 'last']].values 
		return self.rtd_res