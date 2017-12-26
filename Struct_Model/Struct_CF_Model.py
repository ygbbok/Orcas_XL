# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
import pickle
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from IO_Utilities import IO_Utilities
from Calc_Utilities import Calc_Utilities
from Other_Utilities import Other_Utilities




class Whole_Loan_Purchase(object):
	def __init__(self, poolCashflow_IN, struct_specifics_IN,ramping_vector_IN, px_IN):
		self.poolCashflow = poolCashflow_IN
		self.struct_specifics = struct_specifics_IN
		self.ramping_vector = ramping_vector_IN.split(" ")
		self.px = px_IN


	def build_cashflow(self):
		self.ramping_vector_parsed = [float(item) * 1e8 for item in self.ramping_vector[0]]

		self.ramped_poolCashflow = Calc_Utilities.CashFlow_Util.ramping_cf(self.poolCashflow,self.ramping_vector_parsed)

		self.upfrontfee = self.struct_specifics['upfrontfee']
		self.mgmt_fee = self.struct_specifics['mgmt_fee']
		self.mgmt_fee_freq = self.struct_specifics['mgmt_fee_freq']

		self.asset_res_df = pd.DataFrame(columns = ['period','ASSET_bop_bal','ASSET_prin_cf','ASSET_int_cf','ASSET_total_cf','ASSET_new_purchase','ASSET_eop_bal'])
		self.liability_res_df = pd.DataFrame(columns = [
														'period',
														'FEE_paid_fee',
														'RESID_bop_bal',
														'RESID_eop_bal',
														'RESID_int_cf',
														'RESID_prin_cf',
														'RESID_extra_leakage_cf',
														'RESID_total_cf',
														'RESID_new_funding'
														])
		period_i = 0
		
		ASSET_bop_bal = 0
		ASSET_prin_cf = 0
		ASSET_int_cf = 0
		ASSET_total_cf = 0
		ASSET_new_purchase = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == 0,'eop_bal'].values[0]
		ASSET_eop_bal = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == 0,'eop_bal'].values[0]
		
		FEE_paid_fee = 0
		RESID_bop_bal = 0
		RESID_eop_bal = ASSET_eop_bal
		RESID_int_cf = 0
		RESID_prin_cf = 0
		RESID_extra_leakage_cf = 0
		RESID_total_cf = 0
		RESID_new_funding = ASSET_new_purchase

		self.asset_res_df.loc[len(self.asset_res_df)] = [
														period_i,
														ASSET_bop_bal,
														ASSET_prin_cf,
														ASSET_int_cf,
														ASSET_total_cf,
														ASSET_new_purchase,
														ASSET_eop_bal
														]

		self.liability_res_df.loc[len(self.liability_res_df)] = [
																period_i,
																FEE_paid_fee,
																RESID_bop_bal,
																RESID_eop_bal,
																RESID_int_cf,
																RESID_prin_cf,
																RESID_extra_leakage_cf,
																RESID_total_cf,
																RESID_new_funding
																]

		matched_asset_record = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == 0]

		while (ASSET_eop_bal > 0.01) and (len(matched_asset_record)>0):
			period_i += 1
			matched_asset_record = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == period_i]
			RESID_bop_bal = RESID_eop_bal

			# ASSET *******************************************
			ASSET_bop_bal = matched_asset_record['bop_bal'].values[0]
			ASSET_prin_cf = matched_asset_record['prin_cf'].values[0]
			ASSET_int_cf = matched_asset_record['int_cf'].values[0]
			ASSET_total_cf = matched_asset_record['total_cf'].values[0]
			ASSET_new_purchase = matched_asset_record['eop_bal'].values[0]
			ASSET_eop_bal = matched_asset_record['eop_bal'].values[0]

			self.asset_res_df.loc[len(self.asset_res_df)] = [
															period_i,
															ASSET_bop_bal,
															ASSET_prin_cf,
															ASSET_int_cf,
															ASSET_total_cf,
															ASSET_new_purchase,
															ASSET_eop_bal
															]

			# LIABILITY *******************************************
			avail_cf = matched_asset_record['total_cf'].values[0]

			upfront_fee = 0 if period_i>1 else matched_asset_record['bop_bal'].values[0] * (self.upfrontfee * 1.00)
			mgmt_fee = matched_asset_record['bop_bal'].values[0] * self.mgmt_fee /  (self.mgmt_fee_freq * 1.00)

			FEE_paid_fee = min(avail_cf, mgmt_fee + upfront_fee)

			avail_cf = avail_cf - FEE_paid_fee
			
			RESID_int_cf = 0
			RESID_prin_cf = min(avail_cf - RESID_int_cf,RESID_bop_bal)

			avail_cf = avail_cf - (RESID_int_cf + RESID_prin_cf)

			RESID_extra_leakage_cf = avail_cf

			RESID_total_cf = RESID_int_cf + RESID_prin_cf + RESID_extra_leakage_cf

			avail_cf = avail_cf - RESID_total_cf

			RESID_new_funding = matched_asset_record['fundings'].values[0]
			RESID_eop_bal = RESID_bop_bal - RESID_prin_cf + RESID_new_funding

			self.liability_res_df.loc[len(self.liability_res_df)] = [
																	period_i,
																	FEE_paid_fee,
																	RESID_bop_bal,
																	RESID_eop_bal,
																	RESID_int_cf,
																	RESID_prin_cf,
																	RESID_extra_leakage_cf,
																	RESID_total_cf,
																	RESID_new_funding
																	]

		self.asset_liability_res_df = pd.merge(self.asset_res_df, self.liability_res_df, left_on='period', right_on='period')
		# IO_Utilities.IO_Util.open_in_html(self.asset_liability_res_df)

class Securitization(object):
	def __init__(self, poolCashflow_IN, struct_specifics_IN, ramping_vector_IN, transition_period_IN = 9999, px_IN = 100.0):
		self.poolCashflow = poolCashflow_IN
		self.struct_specifics = struct_specifics_IN
		self.ramping_vector = ramping_vector_IN.split(" ")
		self.transition_period = transition_period_IN
		self.px = px_IN

		# General Terms
		self.upfrontfee = self.struct_specifics['upfront_fee']
		self.mgmt_fee = self.struct_specifics['mgmt_fee']
		self.mgmt_fee_freq = self.struct_specifics['mgmt_fee_freq']
		self.prin_cf_split = self.struct_specifics['prin_cf_split']
		self.term = len(poolCashflow_IN) - 1
		
		# DEBT - SNR
		self.snr_intrate = self.struct_specifics['snr_intrate']
		self.snr_intfreq = self.struct_specifics['snr_freq']
		self.snr_adv = self.struct_specifics['snr_advrate']

		# DEBT - MEZZ
		self.mezz_intrate = self.struct_specifics['mezz_intrate']
		self.mezz_intfreq = self.struct_specifics['mezz_freq']
		self.mezz_adv = self.struct_specifics['mezz_advrate']

		# EQUITY
		self.resid_advrate = 1 - self.struct_specifics['mezz_advrate']

		self.standard_cf_col = list(self.poolCashflow.columns.values)
		self.standard_cf_col.remove('period')



	def build_cashflow(self):
		self.ramping_vector_parsed = [float(item) * 1e8 for item in Calc_Utilities.Parser_Util.intex_parser(self.ramping_vector, self.term)]
		self.ramped_poolCashflow = Calc_Utilities.CashFlow_Util.ramping_cf(self.poolCashflow,self.ramping_vector_parsed)
		self.ramped_poolCashflow.loc[:,'fundings'] = self.ramped_poolCashflow.loc[:,'fundings'] * self.px/100.0


		# ASSET
		period_i = 0
		self.asset_cf = self.ramped_poolCashflow
		bop_bal = 0
		prin_cf = self.asset_cf[self.asset_cf['period'] == period_i]['prin_cf'].values[0]
		int_cf = self.asset_cf[self.asset_cf['period'] == period_i]['int_cf'].values[0]
		total_cf = self.asset_cf[self.asset_cf['period'] == period_i]['total_cf'].values[0]
		new_purchase = self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]
		new_funding = self.asset_cf[self.asset_cf['period'] == period_i]['fundings'].values[0]
		eop_bal = self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]

		self.asset_res_df = pd.DataFrame(columns = ['period','ASSET_bop_bal','ASSET_prin_cf','ASSET_int_cf','ASSET_total_cf','ASSET_new_purchase','ASSET_new_funding','ASSET_eop_bal'])
		self.asset_res_df.loc[0] = [period_i,bop_bal,prin_cf,int_cf,total_cf,new_purchase,new_funding,eop_bal]

		# FEE
		paid_fee = 0

		# LIABILITY - SNR
		snr_bop_bal = 0
		snr_eop_bal = eop_bal * self.snr_adv

		snr_schedule_int = 0
		snr_schedule_prin = 0
		snr_int_cf = 0
		snr_prin_cf = 0
		snr_total_cf = snr_int_cf + snr_prin_cf
		snr_int_shortfall = 0
		snr_new_funding = snr_eop_bal
		snr_new_purchase = snr_eop_bal
		snr_effective_adv_rate = snr_eop_bal / eop_bal

		# LIABILITY - MEZZ
		mezz_bop_bal = 0
		mezz_eop_bal = eop_bal * (self.mezz_adv - self.snr_adv)

		mezz_schedule_int = 0
		mezz_schedule_prin = 0
		mezz_int_cf = 0
		mezz_prin_cf = 0
		mezz_total_cf = mezz_int_cf + mezz_prin_cf
		mezz_int_shortfall = 0
		mezz_new_funding = mezz_eop_bal
		mezz_new_purchase = mezz_eop_bal
		mezz_effective_adv_rate = (snr_eop_bal + mezz_eop_bal) / eop_bal

		# EQUITY
		resid_bop_bal = 0
		resid_eop_bal = eop_bal - snr_eop_bal - mezz_eop_bal
		resid_new_purchase = resid_eop_bal
		resid_new_funding = new_funding - snr_new_funding - mezz_new_funding
		resid_cf = 0
		resid_extra_cf = 0
		resid_total_cf = resid_cf + resid_extra_cf


		self.liability_res_df = pd.DataFrame(columns = [
														'period',
														'FEE_paid_fee',
														'SNR_bop_bal',
														'SNR_eop_bal',
														'SNR_new_purchase',
														'SNR_new_funding',
														'SNR_schedule_int',
														'SNR_schedule_prin',
														'SNR_int_cf',
														'SNR_prin_cf',
														'SNR_total_cf',
														'SNR_int_shortfall',
														'SNR_effective_adv_rate',
														'MEZZ_bop_bal',
														'MEZZ_eop_bal',
														'MEZZ_new_purchase',
														'MEZZ_new_funding',
														'MEZZ_schedule_int',
														'MEZZ_schedule_prin',
														'MEZZ_int_cf',
														'MEZZ_prin_cf',
														'MEZZ_total_cf',
														'MEZZ_int_shortfall',
														'MEZZ_effective_adv_rate',
														'RESID_bop_bal',
														'RESID_eop_bal',
														'RESID_new_purchase',
														'RESID_new_funding',
														'RESID_cf',
														'RESID_extra_cf',
														'RESID_total_cf'
														])
		self.liability_res_df.loc[0] = [
										period_i,
										paid_fee,
										snr_bop_bal,
										snr_eop_bal,
										snr_new_purchase,
										snr_new_funding,
										snr_schedule_int,
										snr_schedule_prin,
										snr_int_cf,
										snr_prin_cf,
										snr_total_cf,
										snr_int_shortfall,
										snr_effective_adv_rate,
										mezz_bop_bal,
										mezz_eop_bal,
										mezz_new_purchase,
										mezz_new_funding,
										mezz_schedule_int,
										mezz_schedule_prin,
										mezz_int_cf,
										mezz_prin_cf,
										mezz_total_cf,
										mezz_int_shortfall,
										mezz_effective_adv_rate,
										resid_bop_bal,
										resid_eop_bal,
										resid_new_purchase,
										resid_new_funding,
										resid_cf,
										resid_extra_cf,
										resid_total_cf
										]



		next_matched_asset_record = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == 1]


		while len(next_matched_asset_record)>0 and self.transition_period>=(period_i+1):
			period_i += 1
			matched_asset_record = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == period_i]
			snr_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['SNR_eop_bal'].values[0]
			mezz_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['MEZZ_eop_bal'].values[0]
			resid_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['RESID_eop_bal'].values[0]

			# ASSET *******************************************


			bop_bal = matched_asset_record['bop_bal'].values[0]
			prin_cf = matched_asset_record['prin_cf'].values[0]
			int_cf = matched_asset_record['int_cf'].values[0]
			total_cf = matched_asset_record['total_cf'].values[0]
			new_funding = matched_asset_record['fundings'].values[0]
			new_purchase = new_funding/self.px * 100.0
			eop_bal = matched_asset_record['eop_bal'].values[0]

			if period_i == self.transition_period:
				total_cf = total_cf + matched_asset_record['eop_bal'].values[0]
				eop_bal = 0
			
			avail_cf = total_cf

			self.asset_res_df.loc[len(self.asset_res_df)] = [
															period_i
															,bop_bal
															,prin_cf
															,int_cf
															,total_cf
															,new_purchase
															,new_funding
															,eop_bal
															]


			# FEES and LIABILITY *******************************************

			# FEES
			upfront_fee = 0 if period_i>1 else matched_asset_record['bop_bal'].values[0] * (self.upfrontfee * 1.00)
			mgmt_fee = matched_asset_record['bop_bal'].values[0] * self.mgmt_fee /  (self.mgmt_fee_freq * 1.00)
			paid_fee = min(avail_cf, upfront_fee + mgmt_fee)

			avail_cf = avail_cf - paid_fee

			# DEBT - SNR - INT
			snr_schedule_int = snr_bop_bal * self.snr_intrate / 12.0			
			snr_int_cf = min(avail_cf, snr_schedule_int)
			snr_int_shortfall = snr_schedule_int - snr_int_cf

			avail_cf = avail_cf - snr_int_cf

			# DEBT - MEZZ - INT
			mezz_schedule_int = mezz_bop_bal * self.mezz_intrate / 12.0
			mezz_schedule_prin = mezz_bop_bal
			mezz_int_cf = min(avail_cf, mezz_schedule_int)
			mezz_int_shortfall = mezz_schedule_int - mezz_int_cf

			avail_cf = avail_cf - mezz_int_cf

			# DEBT - SNR - PRIN
			snr_schedule_prin = snr_bop_bal
			snr_prin_cf = min(avail_cf, snr_schedule_prin)
			avail_cf = avail_cf - snr_prin_cf

			# DEBT - MEZZ - PRIN
			mezz_schedule_prin = mezz_bop_bal
			mezz_prin_cf = min(avail_cf, mezz_schedule_prin)
			avail_cf = avail_cf - mezz_prin_cf

			# SNR and MEZZ CF
			snr_total_cf = snr_int_cf + snr_prin_cf
			mezz_total_cf = mezz_int_cf + mezz_prin_cf

			# RESID
			resid_cf = min(avail_cf, resid_bop_bal)
			avail_cf = avail_cf - resid_cf
			resid_extra_cf = avail_cf
			resid_total_cf = resid_cf + resid_extra_cf

			# NEW PURCHASE
			snr_new_funding = new_purchase * self.snr_adv
			snr_new_purchase = new_purchase * self.snr_adv
			mezz_new_funding = new_purchase * (self.mezz_adv - self.snr_adv)
			mezz_new_purchase = new_purchase * (self.mezz_adv - self.snr_adv)
			resid_new_funding = new_funding - snr_new_funding - mezz_new_funding
			resid_new_purchase = new_purchase - snr_new_purchase - mezz_new_purchase

			# EOP BALANCE
			eop_bal = matched_asset_record['eop_bal'].values[0]
			snr_eop_bal = snr_bop_bal - snr_prin_cf + snr_int_shortfall
			mezz_eop_bal = mezz_bop_bal - mezz_prin_cf + mezz_int_shortfall
			resid_eop_bal = resid_bop_bal - resid_cf

			# ADV RATE
			snr_effective_adv_rate = snr_eop_bal / eop_bal
			mezz_effective_adv_rate = (snr_eop_bal + mezz_eop_bal) / eop_bal



			self.liability_res_df.loc[len(self.liability_res_df)] = [
																	period_i,
																	paid_fee,
																	snr_bop_bal,
																	snr_eop_bal,
																	snr_new_purchase,
																	snr_new_funding,
																	snr_schedule_int,
																	snr_schedule_prin,
																	snr_int_cf,
																	snr_prin_cf,
																	snr_total_cf,
																	snr_int_shortfall,
																	snr_effective_adv_rate,
																	mezz_bop_bal,
																	mezz_eop_bal,
																	mezz_new_purchase,
																	mezz_new_funding,
																	mezz_schedule_int,
																	mezz_schedule_prin,
																	mezz_int_cf,
																	mezz_prin_cf,
																	mezz_total_cf,
																	mezz_int_shortfall,
																	mezz_effective_adv_rate,
																	resid_bop_bal,
																	resid_eop_bal,
																	resid_new_purchase,
																	resid_new_funding,
																	resid_cf,
																	resid_extra_cf,
																	resid_total_cf
																	]
			next_matched_asset_record = self.ramped_poolCashflow.loc[self.ramped_poolCashflow['period'] == period_i + 1]





			
	


		self.asset_liability_res_df = pd.merge(self.asset_res_df, self.liability_res_df, left_on='period', right_on='period')
		# self.asset_liability_res_df.to_pickle("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\leveredecon.pickle")
		# IO_Utilities.IO_Util.open_in_html(self.asset_liability_res_df)



class Tiered_Trust(object):
	def __init__(self, poolCashflow_IN, struct_specifics_IN,ramping_vector_IN, transition_period_IN = 9999, px_IN = 100.0):
		self.poolCashflow = poolCashflow_IN
		self.struct_specifics = struct_specifics_IN

		self.ramping_vector = ramping_vector_IN.split(" ")
		self.transition_period = transition_period_IN
		self.px = px_IN

		#Term Sheet - General Terms
		self.term = self.struct_specifics['term']
		self.reinvestment_vector = self.struct_specifics['reinvestment_vector']
		self.pass_through_trigger_period = self.struct_specifics['pass_through_trigger_period']
		self.pass_through_trigger_period = min(self.pass_through_trigger_period,self.term)

		# Term Sheet - Senior Debt
		self.snr_int,self.snr_adv, self.snr_freq = self.struct_specifics['snr_intrate'],self.struct_specifics['snr_advrate'],self.struct_specifics['snr_freq']
		self.snr_per = 12/self.snr_freq
		self.snr_coupon_periods = range(0,self.term + self.snr_per,self.snr_per)[1:]

		# Term Sheet - Trust Fee
		self.trust_fee,self.trust_upfrontfee  = self.struct_specifics['trust_fee'],self.struct_specifics['trust_upfrontfee']

		# Term Sheet - Reserve Account
		self.extra_reserve_account_buffer = self.struct_specifics['extra_reserve_account_buffer']


		self.assets_container = []
		self.liability_container = []
		self.reserve_account = 0
		self.reserve_account_shortfall = 0
		self.extra_reserve_account = 0
		self.standard_cf_col = list(self.poolCashflow.columns.values)
		self.standard_cf_col.remove('period')

	
	def build_cashflow(self):
		self.reinvestment_vector = [float(item) for item in Calc_Utilities.Parser_Util.intex_parser(self.struct_specifics['reinvestment_vector'].split(" "), self.term)]
		self.reinvestment_vector[0] = 1
		self.ramping_vector_parsed = [float(item) * 1e8 for item in Calc_Utilities.Parser_Util.intex_parser(self.ramping_vector, self.term)]

		self.ramped_poolCashflow = Calc_Utilities.CashFlow_Util.ramping_cf(self.poolCashflow,self.ramping_vector_parsed)
		self.ramped_poolCashflow.loc[:,'fundings'] = self.ramped_poolCashflow.loc[:,'fundings'] * self.px/100.0

		self.pass_through_trigger_on = False

		# ASSET POOL
		period_i = 0
		self.asset_cf = self.ramped_poolCashflow
		bop_bal = 0
		prin_cf = self.asset_cf[self.asset_cf['period'] == period_i]['prin_cf'].values[0]
		int_cf = self.asset_cf[self.asset_cf['period'] == period_i]['int_cf'].values[0]
		total_cf = self.asset_cf[self.asset_cf['period'] == period_i]['total_cf'].values[0]
		new_purchase = self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]
		new_funding = self.asset_cf[self.asset_cf['period'] == period_i]['fundings'].values[0]

		eop_bal = self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]

		self.asset_res_df = pd.DataFrame(columns = ['period','ASSET_bop_bal','ASSET_prin_cf','ASSET_int_cf','ASSET_total_cf','ASSET_new_purchase','ASSET_new_funding','ASSET_eop_bal'])
		self.asset_res_df.loc[0] = [period_i,bop_bal,prin_cf,int_cf,total_cf,new_purchase,new_funding,eop_bal]
		


		# FEE
		paid_fee = 0

		# LIABILITY - SNR
		snr_bop_bal = 0
		snr_eop_bal = eop_bal * self.snr_adv

		snr_next_due_period = self.snr_coupon_periods[0]
		snr_new_due_int = 0
		snr_accumulative_due_int = 0
		snr_schedule_int = 0
		snr_schedule_prin = 0
		snr_int_cf = 0
		snr_prin_cf = 0
		snr_total_cf = snr_int_cf + snr_prin_cf
		snr_int_shortfall = 0
		snr_prin_shortfall = 0
		snr_total_shortfall = snr_int_shortfall + snr_prin_shortfall
		snr_new_funding = new_funding * self.snr_adv
		snr_new_purchase = snr_eop_bal
		snr_effective_adv_rate = snr_eop_bal/eop_bal


		# LIABILITY - RESERVE ACCOUNT
		reserve_bop_bal = 0
		reserve_eop_bal = 0
		reserve_bop_shortfall = 0
		reserve_eop_shortfall = 0
		reserve_bop_extra_reserve = 0
		reserve_eop_extra_reserve = 0
		reserve_account_buffer = self.extra_reserve_account_buffer


		# EQUITY
		resid_bop_bal = 0
		resid_eop_bal = eop_bal - snr_eop_bal
		resid_new_purchase = resid_eop_bal
		resid_new_funding = new_funding - snr_new_funding
		resid_cf = 0
		resid_extra_cf = 0
		resid_total_cf = resid_cf + resid_extra_cf


		self.liability_res_df = pd.DataFrame(columns = [
														'period',
														'FEE_paid_fee',
														'SNR_bop_bal',
														'SNR_eop_bal',
														'SNR_new_purchase',
														'SNR_new_funding',
														'SNR_next_due_period',
														'SNR_new_due_int',
														'SNR_accumulative_due_int',
														'SNR_schedule_int',
														'SNR_schedule_prin',
														'SNR_int_cf',
														'SNR_prin_cf',
														'SNR_total_cf',
														'SNR_int_shortfall',
														'SNR_prin_shortfall',
														'SNR_total_shortfall',
														'SNR_effective_adv_rate',
														'RESERVE_bop_reserve_account',
														'RESERVE_eop_reserve_account',
														'RESERVE_bop_reserve_account_shortfall',
														'RESERVE_eop_reserve_account_shortfall',
														'RESERVE_bop_extra_reserve_account',
														'RESERVE_eop_extra_reserve_account',
														'RESERVE_extra_reserve_account_buffer',
														'RESID_bop_bal',
														'RESID_eop_bal',
														'RESID_new_purchase',
														'RESID_new_funding',
														'RESID_cf',
														'RESID_extra_cf',
														'RESID_total_cf'
														])
		self.liability_res_df.loc[0] = [
										period_i,
										paid_fee,
										snr_bop_bal,
										snr_eop_bal,
										snr_new_purchase,
										snr_new_funding,
										snr_next_due_period,
										snr_new_due_int,
										snr_accumulative_due_int,
										snr_schedule_int,
										snr_schedule_prin,
										snr_int_cf,
										snr_prin_cf,
										snr_total_cf,
										snr_int_shortfall,
										snr_prin_shortfall,
										snr_total_shortfall,
										snr_effective_adv_rate,
										reserve_bop_bal,
										reserve_eop_bal,
										reserve_bop_shortfall,
										reserve_eop_shortfall,
										reserve_bop_extra_reserve,
										reserve_eop_extra_reserve,
										reserve_account_buffer,
										resid_bop_bal,
										resid_eop_bal,
										resid_new_purchase,
										resid_new_funding,
										resid_cf,
										resid_extra_cf,
										resid_total_cf
										]

		avail_cf = 0

		for period_i in range(1,self.term+1):
			if self.transition_period >= period_i:

				if period_i >= self.pass_through_trigger_period:
					self.pass_through_trigger_on = True

				asset_bop_bal = self.asset_res_df[self.asset_res_df['period'] == period_i - 1]['ASSET_eop_bal'].values[0]
				snr_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['SNR_eop_bal'].values[0]
				reserve_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['RESERVE_eop_reserve_account'].values[0]
				reserve_bop_shortfall = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['RESERVE_eop_reserve_account_shortfall'].values[0]
				reserve_bop_extra_reserve = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['RESERVE_eop_extra_reserve_account'].values[0]
				resid_bop_bal = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['RESID_eop_bal'].values[0]
				reserve_account_buffer = self.extra_reserve_account_buffer

				snr_due_period = self.liability_res_df[self.liability_res_df['period'] == period_i - 1]['SNR_next_due_period'].values[0]


				# ASSET CF
				prin_cf = self.asset_cf[self.asset_cf['period'] == period_i]['prin_cf'].values[0]
				int_cf = self.asset_cf[self.asset_cf['period'] == period_i]['int_cf'].values[0]
				total_cf = self.asset_cf[self.asset_cf['period'] == period_i]['total_cf'].values[0]
			
				if self.transition_period == period_i:
					total_cf = total_cf + self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]

				avail_cf = total_cf


				# FEE
				upfront_fee_due = 0 if period_i > 1 else self.trust_upfrontfee * asset_bop_bal
				periodic_fee_due = self.trust_fee * asset_bop_bal / 12
				total_fee_due = upfront_fee_due + periodic_fee_due
				paid_fee = min(avail_cf, total_fee_due)
				avail_cf = avail_cf - paid_fee


				# CALCULATE SNR INT
				snr_new_due_int = snr_bop_bal * self.snr_int / 12.0
				snr_accumulative_due_int = snr_accumulative_due_int + snr_new_due_int

				snr_int_cover = min(avail_cf,snr_new_due_int)
				avail_cf = avail_cf - snr_accumulative_due_int

				# RESERVE or PAY TO SNR INT
				if period_i == snr_due_period: # pay to snr account

					snr_schedule_int = snr_accumulative_due_int
					snr_int_cf = reserve_bop_bal + snr_int_cover
					snr_int_shortfall = min(snr_schedule_int - snr_int_cf,0)

					reserve_eop_bal = 0
					reserve_eop_shortfall = 0
					snr_accumulative_due_int = 0

				elif period_i != snr_due_period: # accumulate into reserve account
					
					snr_schedule_int = 0
					snr_int_cf = 0
					snr_int_shortfall = 0

					reserve_eop_bal = reserve_bop_bal + snr_int_cover
					reserve_eop_shortfall = (snr_accumulative_due_int - reserve_eop_bal,0)

				# PAY TO SNR PRIN
				if self.pass_through_trigger_on:
					snr_schedule_prin = snr_bop_bal
				else:
					snr_schedule_prin = 0

				snr_schedule_total = snr_schedule_int + snr_schedule_prin
				snr_prin_cf = min(avail_cf, snr_schedule_prin)
				snr_total_cf = snr_int_cf + snr_prin_cf

				avail_cf = avail_cf - snr_prin_cf

				# EQUITY
				resid_cf = min(avail_cf, resid_bop_bal)
				avail_cf = avail_cf - resid_cf

				resid_extra_cf = avail_cf
				avail_cf = avail_cf - resid_extra_cf

				resid_total_cf = resid_cf + resid_extra_cf

				# NEW PURCHASE
				snr_new_funding = 0 #Tiered Trust does not snr funding mechanism after initial period
				if period_i != self.term:
					resid_new_funding = (resid_cf + resid_extra_cf) * self.reinvestment_vector[period_i]

				snr_new_purchase = snr_new_funding / self.px * 100.0
				resid_new_purchase = resid_new_funding / self.px * 100.0

				new_funding = snr_new_funding + resid_new_funding
				new_purchase = snr_new_purchase + resid_new_purchase

				new_purchase_multiple = new_purchase/self.ramped_poolCashflow[self.ramped_poolCashflow['period'] == 0]['eop_bal'].values[0]

				if new_purchase_multiple >0:
					self.add_new_assets(new_purchase_multiple, period_i)


				# DEBT and EQUITY EOP BALANCE
				snr_eop_bal = snr_bop_bal \
								- snr_prin_cf \
								+ snr_int_shortfall \
								+ snr_new_purchase


				resid_eop_bal = resid_bop_bal \
								- resid_cf \
								+ resid_new_purchase \

				snr_effective_adv_rate = snr_eop_bal/eop_bal

				# NEXT SNR DUE period
				if period_i == self.term:
					snr_next_due_period = self.term
				else:
					snr_next_due_period = min([item for item in self.snr_coupon_periods if item > period_i])


				bop_bal = self.asset_cf[self.asset_cf['period'] == period_i]['bop_bal'].values[0]
				eop_bal = self.asset_cf[self.asset_cf['period'] == period_i]['eop_bal'].values[0]

				if self.transition_period == period_i:
					eop_bal = 0


				# ADV RATE
				snr_effective_adv_rate = snr_eop_bal/eop_bal

				self.asset_res_df.loc[len(self.asset_res_df)] = [
																period_i,
																bop_bal,
																prin_cf,
																int_cf,
																total_cf,
																new_purchase,
																new_funding,
																eop_bal
																]

				self.liability_res_df.loc[len(self.liability_res_df)] = [
												period_i,
												paid_fee,
												snr_bop_bal,
												snr_eop_bal,
												snr_new_purchase,
												snr_new_funding,
												snr_next_due_period,
												snr_new_due_int,
												snr_accumulative_due_int,
												snr_schedule_int,
												snr_schedule_prin,
												snr_int_cf,
												snr_prin_cf,
												snr_total_cf,
												snr_int_shortfall,
												snr_prin_shortfall,
												snr_total_shortfall,
												snr_effective_adv_rate,
												reserve_bop_bal,
												reserve_eop_bal,
												reserve_bop_shortfall,
												reserve_eop_shortfall,
												reserve_bop_extra_reserve,
												reserve_eop_extra_reserve,
												reserve_account_buffer,
												resid_bop_bal,
												resid_eop_bal,
												resid_new_purchase,
												resid_new_funding,
												resid_cf,
												resid_extra_cf,
												resid_total_cf
												]
		self.asset_liability_res_df = pd.merge(self.asset_res_df,self.liability_res_df,left_on = 'period',right_on = 'period',how = 'inner')
		
	def add_new_assets(self, multiple_IN, period_i):
		asset_multiple = multiple_IN
		bought_period = period_i
		ramped_poolCashflow = self.ramped_poolCashflow.copy()
		ramped_poolCashflow.loc[:,self.standard_cf_col] = ramped_poolCashflow.loc[:,self.standard_cf_col] * asset_multiple
		ramped_poolCashflow.loc[:,'period'] = ramped_poolCashflow.loc[:,'period'] + bought_period
		temp = self.asset_cf.append(ramped_poolCashflow,ignore_index = True)
		
		self.asset_cf = temp.groupby(['period'])[self.standard_cf_col].sum().reset_index()


class Levered_Financing(object):
	def __init__(self, poolCashflow_IN, 
					   first_struct_type_IN,
					   first_struct_specifics_IN,
					   first_struct_ramping_vector_IN,
					   transition_period_IN,
					   second_struct_type_IN,
					   second_struct_specifics_IN,
					   px_IN = 100.0):

		self.poolCashflow = poolCashflow_IN
		self.first_struct_type = first_struct_type_IN
		self.first_struct_specifics = first_struct_specifics_IN
		self.first_struct_ramping_vector = first_struct_ramping_vector_IN
		self.transition_period = transition_period_IN
		self.second_struct_type = second_struct_type_IN
		self.second_struct_specifics = second_struct_specifics_IN
		self.px = px_IN


	def run_financing(self):
		self.initialize_first_struct()
		self.run_first_struct()

		self.transitioned_cashflow = self.first_financing_mgmt.asset_cf[self.first_financing_mgmt.asset_cf['period']>=self.transition_period]
		self.transitioned_cashflow.loc[:,'period'] = range(0,len(self.transitioned_cashflow))
		if len(self.transitioned_cashflow) == 0:
			self.transitioned_cashflow = self.first_financing_mgmt.asset_cf[self.first_financing_mgmt.asset_cf['period'] == 0]
			self.transitioned_cashflow.loc[:,:] = 0

		self.transitioned_cashflow = self.transitioned_cashflow.reset_index(drop = True)
		starting_eop = self.transitioned_cashflow.loc[0,'eop_bal']

		self.transitioned_cashflow.loc[0,:] = 0
		self.transitioned_cashflow.loc[0,'eop_bal'] = starting_eop
		self.transitioned_cashflow.loc[0,'fundings'] = starting_eop
		self.second_struct_ramping_vector = str(starting_eop/1e8) + " " + "0"

		self.initialize_second_struct()
		self.run_second_struct()

	def initialize_first_struct(self):
		if self.first_struct_type == u'结构化信托(建仓)':
			self.first_financing_mgmt = Tiered_Trust(
													 self.poolCashflow,
													 self.first_struct_specifics,
													 self.first_struct_ramping_vector,
													 self.transition_period
													 )
		elif self.first_struct_type == u'证券化':
			self.first_financing_mgmt = Securitization(
													   self.poolCashflow,
													   self.first_struct_specifics,
													   self.first_struct_ramping_vector,
													   self.transition_period
													   )

	def run_first_struct(self):
		self.first_financing_mgmt.build_cashflow()

	def initialize_second_struct(self):
		if self.second_struct_type == u'结构化信托(建仓)':
			self.second_financing_mgmt = Tiered_Trust(
													 self.transitioned_cashflow,
													 self.second_struct_specifics,
													 self.second_struct_ramping_vector
													 )
		elif self.second_struct_type == u'证券化':
			self.second_financing_mgmt = Securitization(
													   self.transitioned_cashflow,
													   self.second_struct_specifics,
													   self.second_struct_ramping_vector
													   )

	def run_second_struct(self):
		self.second_financing_mgmt.build_cashflow()


def main():
	poolCashflow = pd.read_pickle("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\poolcashflow.pickle")
	securitization_struct_specifics = pickle.load( open( "F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\securitization_structspecifics.pkl", "rb" ))
	warehouse_struct_specifics = pickle.load( open( "F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\warehouse_structspecifics.pkl", "rb" ))

	ramping_vector_IN = '1 0'


	Levered_Financing_instance = Levered_Financing(poolCashflow,
												   u'证券化',
												   securitization_struct_specifics,
												   ramping_vector_IN,
												   18,
												   u'证券化',
												   securitization_struct_specifics,
												   100
												   )
	Levered_Financing_instance.run_financing()

	# tiered_trust_instance = Tiered_Trust(poolCashflow,struct_specifics,ramping_vector_IN = ramping_vector_IN,px_IN = px_IN)
	# whole_loan_purchase_instance = Whole_Loan_Purchase(poolCashflow,struct_specifics,ramping_vector_IN = ramping_vector_IN,px_IN = px_IN)
	# securitization_instance = Securitization(poolCashflow, struct_specifics, ramping_vector_IN)

if __name__ == "__main__":
	main()