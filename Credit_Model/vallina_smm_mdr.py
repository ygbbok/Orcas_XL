import pandas as pd
import numpy as np
import os
import sys
import math
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from Config import Config
from IO_Utilities import IO_Utilities
from Calc_Utilities import Calc_Utilities
# IO_Utilities.IO_Util.open_in_html(static_betas_5m_prepay)

class vallina_smm_mdr(object):
	def __init__(self, static_pool_IN, smm_IN, mdr_IN):
		self.static_pool = static_pool_IN
		self.smm = smm_IN.split(" ")
		self.mdr = mdr_IN.split(" ")

		self.max_term = int(self.static_pool['term'].max())

		mob_list = []
		for i in range(1,self.max_term + 1):
			mob_list.append("mob_" + str(i))


		self.smm_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number'] + mob_list).fillna(0)
		self.mdr_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number'] + mob_list).fillna(0)


		self.smm_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']
		self.mdr_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']


	def run_prepay_default(self):
		for idx, row in self.static_pool.iterrows():
			the_term = int(row['term'])
			smm_parsed = Calc_Utilities.Parser_Util.intex_parser(self.smm, the_term-1)
			mdr_parsed = Calc_Utilities.Parser_Util.intex_parser(self.mdr, the_term-1)
			self.smm_matrix.ix[idx,1:(the_term+1)] = [float(item)/100.0 for item in smm_parsed]
			self.mdr_matrix.ix[idx,1:(the_term+1)] = [float(item)/100.0 for item in mdr_parsed]
	
	def intex_parser(self, intex_list_IN, term_IN):
		if term_IN == len(intex_list_IN):
			res = intex_list_IN

		if term_IN < len(intex_list_IN):
			res = intex_list_IN[0:term_IN]

		if term_IN > len(intex_list_IN):
			res = intex_list_IN + [intex_list_IN[-1]] * (term_IN - len(intex_list_IN))

		return res 




