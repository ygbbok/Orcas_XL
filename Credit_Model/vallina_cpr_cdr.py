import pandas as pd
import numpy as np
import os
import sys
import math
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from Config import Config
from IO_Utilities import IO_Utilities
# IO_Utilities.IO_Util.open_in_html(static_betas_5m_prepay)

class vallina_cpr_cdr(object):
	def __init__(self, static_pool_IN, cpr_IN, cdr_IN):
		self.static_pool = static_pool_IN
		self.cpr = cpr_IN
		self.cdr = cdr_IN

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
			the_term = row['term']
			self.smm_matrix.ix[idx,1:the_term+1] = 1- pow(1-self.cpr,1/12.0)
			self.mdr_matrix.ix[idx,1:the_term+1] = 1- pow(1-self.cdr,1/12.0)

