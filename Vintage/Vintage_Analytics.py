
# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import sys
import webbrowser
import random
import string
from IO_Util import IO_Util
import datetime
from Data_Parser import Data_Parser
import math

reload(sys)
sys.setdefaultencoding( "gb2312" )

class Vintage_Analytics(object):
	def __init__(self, the_repayment, the_loantape,the_dimensions_settings, the_measures_dict, the_rules_mapping = None, add_code_IN = ''):
		self.repayment = the_repayment
		self.loantape = the_loantape

		self.dimensions_settings = the_dimensions_settings
		self.measures_dict = the_measures_dict
		self.rules_mapping = the_rules_mapping

		self.datatype_dict = dict()
		self.add_code = add_code_IN
		self.data_parser = Data_Parser(self.loantape,self.add_code)

	def run_add_code(self):
		for add_code_item in (self.add_code_list):
			exec(add_code_item)


	def analytics_procedure(self):
		# Assign MOB column

		self.prepay_accum_rate = {}
		self.smm = {}
		self.cpr = {}


		self.repayment['MOB'] = self.repayment.sort_values([self.measures_dict['repayment_loan_identity'],self.measures_dict['time_schedule']], ascending=[True,True]) \
		.groupby([self.measures_dict['repayment_loan_identity']]) \
		.cumcount() + 1

		repayment_columns = list(self.repayment.columns.values)
		dimension_columns = list(self.dimensions_settings.loc[:,'column'])


		def run_exec(code_piece):
			exec(code_piece)

		# Loan Tape Condition Partition
		if self.add_code != '':
			self.add_code_list = self.add_code.split('\n')
			self.run_add_code()


		# Find Inner Join of Loan Tape and Repayment
		self.repayment = pd.merge(self.repayment,self.loantape, left_on=self.measures_dict['repayment_loan_identity'], right_on = self.measures_dict['loantape_loan_identity'], how = 'inner')
		self.repayment = self.repayment.loc[:,repayment_columns + dimension_columns]

		for dimension in dimension_columns:
			self.prepay_accum_rate[dimension] = []
			self.smm[dimension] = []
			self.cpr[dimension] = []

			# Prepayment Calculation
			orig_bal = self.repayment.groupby([dimension,'MOB'])[self.measures_dict['orig_bal']].sum().reset_index()

			orig_bal = pd.DataFrame(orig_bal.loc[orig_bal['MOB'] == 1,:].set_index(dimension)[self.measures_dict['orig_bal']])
			prepay_vector = self.repayment.groupby(by = [dimension,'MOB'])[self.measures_dict['prepay']].sum()
			prepay_accum = prepay_vector.groupby(level=[0]).cumsum().reset_index(level = 1)
			merged = prepay_accum.merge(orig_bal,left_index = True, right_index = True, how = 'inner')
			merged.loc[:,'prepay_accum_rate'] = merged.loc[:,self.measures_dict['prepay']]/merged.loc[:,self.measures_dict['orig_bal']]
			prepay_accum_rate = merged.loc[:,['MOB','prepay_accum_rate']]

			bop_bal_vector = self.repayment.groupby(by = [dimension,'MOB'])[self.measures_dict['bop_bal']].sum()
			sche_bal_vector = self.repayment.groupby(by = [dimension,'MOB'])[self.measures_dict['sche_bal']].sum()

			smm_vector = prepay_vector / (bop_bal_vector-sche_bal_vector)
			cpr_vector = 1 - smm_vector.apply(lambda x: math.pow(1 - x,12))

			print prepay_accum_rate

			# prepay_accum_rate.to_csv(os.path.join(Config.Orcas_dir, 'temp_output\prepay_accum_rate2.csv'))

def main():
	the_repayment = pd.read_csv(u"F:\Work\Bohai Huijin Asset Management\Investment\ABS Investment\Opportunities\优信二手车\尽调\资产数据\\uxin_repayment.csv",sep = ",",encoding='gb2312')
	the_loantape = pd.read_csv(u"F:\Work\Bohai Huijin Asset Management\Investment\ABS Investment\Opportunities\优信二手车\尽调\资产数据\\uxin_loantape.csv",sep = ",",encoding='gb2312')

	the_dimensions_settings = pd.DataFrame(columns = [u'column',u'group_rule',u'label'])
	the_dimensions_settings.loc[0] = [u'性别','',u'Gender']

	the_measures_dict = {
						'repayment_loan_identity':u'loan_number',
						'loantape_loan_identity':u'付一半订单编号',
						'time_schedule':u'sche_date',
						'orig_bal':u'original_balance',
						'bop_bal':u'bop_balance',
						'prepay':u'prepayment',
						'sche_bal':u'due_prin'
						}
	the_rules_mapping = None
	add_code_IN = ''

	Vintage_Analytics_instance = Vintage_Analytics(the_repayment, the_loantape,the_dimensions_settings, the_measures_dict, the_rules_mapping, add_code_IN)

	Vintage_Analytics_instance.analytics_procedure()


if __name__ == "__main__":
	main()