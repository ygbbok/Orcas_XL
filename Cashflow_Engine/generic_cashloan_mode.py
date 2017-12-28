import pandas as pd
import numpy as np
import os
import sys
import math
import pickle
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from Config import Config
from IO_Utilities import IO_Utilities
# IO_Utilities.IO_Util.open_in_html(static_betas_5m_prepay)

class generic_cashloan_mode(object):
	def __init__(self, static_pool_IN,smm_df_IN,mdr_df_IN,severity_rate_IN,recovery_lag_IN):
		self.static_pool = static_pool_IN
		self.smm_df = smm_df_IN
		self.mdr_df = mdr_df_IN
		self.severity_rate = severity_rate_IN
		self.recovery_lag = recovery_lag_IN

	def run_cashflow(self):
		self.cashflow = {}
		for idx,row in self.static_pool.iterrows():
			BHHJ_Loan_Number = row['BHHJ_Loan_Number']
			original_balance = row['original_balance']
			term = row['term']
			int_rate = row['int_rate']
			smm_vector = self.smm_df[self.smm_df['BHHJ_Loan_Number'] == BHHJ_Loan_Number]
			mdr_vector = self.mdr_df[self.mdr_df['BHHJ_Loan_Number'] == BHHJ_Loan_Number]


			total_term = int(term + self.recovery_lag)
			cf_df = pd.DataFrame(index = range(0,total_term+1),columns = [
																		'period',
																		'bop_bal',
																		'schedule_pmt',
																		'schedule_prin',
																		'schedule_int',
																		'default',
																		'prepay',
																		'expected_recovery',
																		'loss',
																		'recovery',
																		'recovery_bal_new',
																		'recovery_bal',
																		'prin_cf',
																		'int_cf',
																		'total_cf',
																		'eop_bal'
																		]).fillna(0)
			cf_df.loc[0,'period'] = 0
			cf_df.loc[0,'eop_bal'] = original_balance
			
			for period_i in range(1,total_term+1):

				remaining_term = term - period_i + 1
				mob_header = 'mob' + "_" + str(period_i)
				try:
					smm = smm_vector[mob_header]
				except:
					smm = 0
				try:
					mdr = mdr_vector[mob_header]
				except:
					mdr = 0

				bop_bal = cf_df.loc[period_i - 1,'eop_bal']
				schedule_pmt = 0 if remaining_term <= 0 else bop_bal/remaining_term * 1.0 + bop_bal * int_rate/12.0
				schedule_prin = 0 if remaining_term <= 0 else bop_bal/remaining_term * 1.0
				schedule_int = bop_bal * int_rate/12.0
				# default = bop_bal * mdr
				default = (bop_bal - schedule_prin) * mdr
				prepay = (bop_bal - schedule_prin) * smm
				expected_recovery = default * (1-self.severity_rate)
				loss = default - expected_recovery
				recovery = cf_df.loc[max(0,period_i - self.recovery_lag), 'expected_recovery']
				if self.recovery_lag == 0:
					recovery = expected_recovery
				recovery_bal_new = expected_recovery - recovery
				recovery_bal = cf_df.loc[max(0,period_i - 1), 'recovery_bal'] + recovery_bal_new
				# prin_cf = (schedule_prin - default) + prepay
				prin_cf = schedule_prin + recovery + prepay
				# int_cf = (bop_bal - default) * int_rate/12.0
				int_cf = bop_bal * int_rate/12.0
				# total_cf = prin_cf + int_cf + recovery
				total_cf = prin_cf + int_cf
				eop_bal = bop_bal - prin_cf - default + recovery

				cf_df.loc[period_i] = [ period_i,
										bop_bal,
										schedule_pmt,
										schedule_prin,
										schedule_int,
										default,
										prepay,
										expected_recovery,
										loss,
										recovery,
										recovery_bal_new,
										recovery_bal,
										prin_cf,
										int_cf,
										total_cf,
										eop_bal
										]

			self.cashflow[BHHJ_Loan_Number] = cf_df


class aggregator(object):
	def __init__(self, ll_cashflow_IN):
		self.ll_cashflow = ll_cashflow_IN
	
	def aggregate_cf(self):	
		self.concat_cashflow = pd.concat([value for key,value in self.ll_cashflow.items()])
		df_col = list(self.concat_cashflow.columns.values)
		df_col.remove('Period')

		self.aggregate_cashflow = self.concat_cashflow.groupby('Period')[df_col].sum()
		self.aggregate_cashflow = self.aggregate_cashflow.reset_index(drop = False)

def main():
	to_be_loaded_pkl = "F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Unlevered_Economics_Run\\3.ll.pkl"
	ll_pkl_file = open(to_be_loaded_pkl, 'rb')
	ll_cashflow_pkl = pickle.load(ll_pkl_file)
	ll_pkl_file.close()

	aggregator_instance = aggregator(ll_cashflow_pkl)
	aggregator_instance.aggregate_cf()

if __name__ == "__main__":
	main()