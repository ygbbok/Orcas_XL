# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import math as math

import sys
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from GUI_Utilities import GUI_Utilities
class CashFlow_Util(object):
	@staticmethod
	def compress_cf(df_IN, frequency_IN):
		df_IN_columns = list(df_IN.columns.values)
		divisor = 12/frequency_IN
		df_IN.loc[:,'period'] = pd.Series([math.floor((idx-1)/divisor)+1 for idx in df_IN.index],index = df_IN.index)
		df_new = df_IN.groupby(['period'])[df_IN_columns].sum().reset_index(drop=True)
		return df_new

	@staticmethod
	def ramping_cf(df_IN,ramping_vector):
		res_df = pd.DataFrame()
		copy_of_col_names = df_IN.columns.values
		standard_cf_col = list(df_IN.columns.values)
		standard_cf_col.remove('period')
		for idx,ramping_element in enumerate(ramping_vector):
			ramping_scale = ramping_element * 1.0 /df_IN.loc[0,'eop_bal']
			if ramping_scale>0:
				ramped_cf =  ramping_scale * df_IN.loc[:,standard_cf_col]
				ramped_cf.loc[:,'period'] = df_IN.loc[:,'period']
				extended_cf = ramped_cf
				extended_cf.loc[:,'period'] = extended_cf.loc[:,'period'] + idx
				if len(res_df) == 0:
					res_df = extended_cf
				else:
					res_df = pd.concat([res_df,extended_cf],ignore_index = True)

		if 'period' in res_df.columns.values:
			res_df = res_df.groupby(['period']).sum().reset_index(drop=False)
			res_df = res_df.loc[:,copy_of_col_names]
		else:
			res_df = df_IN
		return res_df

class Parser_Util(object):
	@staticmethod
	def intex_parser(intex_list_IN, term_IN):
		term_IN = term_IN + 1

		if len(intex_list_IN)>3:
			if intex_list_IN[1] == "for":
				intex_list_IN = [intex_list_IN[0]] * int(intex_list_IN[2]) + intex_list_IN[3:]

		if term_IN == len(intex_list_IN):
			res = intex_list_IN

		if term_IN < len(intex_list_IN):
			res = intex_list_IN[0:term_IN]

		if term_IN > len(intex_list_IN):
			res = intex_list_IN + [intex_list_IN[-1]] * (term_IN - len(intex_list_IN))

		return res

class StandardBond_Util(object):
	@staticmethod
	def schedule_pmt(balance_IN, term_IN, rate_IN, type_IN):
		
		# type : Bullet, IO, Amortized, Waterfall
		if type_IN == "Bullet":
			if term_IN > 1:
				schedule_pmt = 0
				schedule_int = 0
			elif term_IN == 1:
				schedule_pmt = rate_IN * balance_IN + balance_IN
				schedule_int = rate_IN * balance_IN

		if type_IN == "IO":
			if term_IN > 1:
				schedule_pmt = rate_IN * balance_IN
				schedule_int = rate_IN * balance_IN
			elif term_IN == 1:
				schedule_pmt = rate_IN * balance_IN + balance_IN
				schedule_int = rate_IN * balance_IN

		if type_IN == "Waterfall":
			schedule_pmt = rate_IN * balance_IN + balance_IN
			schedule_int = rate_IN * balance_IN

		if type_IN == "Amortized":
			schedule_pmt = np.pmt(rate_IN, term_IN, -balance_IN)
			schedule_int = rate_IN * balance_IN
		schedule_prin = schedule_pmt - schedule_int
		return schedule_pmt, schedule_int, schedule_prin

	@staticmethod
	def irr_calc(fundings_array_IN, cf_array_IN, frequency_IN = 12,px = 100):
		if sum(cf_array_IN) < 0.5 * sum(fundings_array_IN) * px * 1.0/100: # less than half of investment is returned
			return -1
		else:
			return np.irr(-1 * fundings_array_IN * px * 1.0 / 100+ cf_array_IN) * frequency_IN

	@staticmethod
	def pnl_calc(fundings_array_IN, cf_array_IN):
		return sum(-1 * fundings_array_IN + cf_array_IN)

	@staticmethod
	def totalfundings_calc(fundings_array_IN):
		return sum(fundings_array_IN)

	@staticmethod
	def WAL_calc(cf_array_IN, frequency_IN):
		cf_array_IN = cf_array_IN.astype(float)
		period_array = np.array(range(0,cf_array_IN.shape[0]))
		return sum(period_array * cf_array_IN)/sum(cf_array_IN)/float(frequency_IN)

	@staticmethod
	def MacDur_calc(yield_IN, cf_array_IN, frequency_IN):
		pv = np.npv(yield_IN/frequency_IN, cf_array_IN)

		cf_array_IN = cf_array_IN.astype(float)
		period_array = np.array(range(0,cf_array_IN.shape[0]))

		return sum(period_array * (cf_array_IN/np.power(1+yield_IN/frequency_IN,period_array))) \
			   /pv \
			   /frequency_IN

	@staticmethod
	def Cum_Default_calc(fundings_array_IN, default_array_IN):
		pseudo_cum_fundings = fundings_array_IN.cumsum()
		pseudo_cum_default = default_array_IN.cumsum()
		res = pseudo_cum_default/pseudo_cum_fundings
		return res

	@staticmethod
	def Cum_Prepay_calc(fundings_array_IN, prepay_array_IN):
		pseudo_cum_fundings = fundings_array_IN.cumsum()
		pseudo_cum_prepay = prepay_array_IN.cumsum()
		res = pseudo_cum_prepay/pseudo_cum_fundings
		return res
	@staticmethod
	def Cum_Loss_calc(fundings_array_IN, loss_array_IN):
		pseudo_cum_fundings = fundings_array_IN.cumsum()
		pseudo_cum_loss = loss_array_IN.cumsum()
		period = np.array(range(0,len(fundings_array_IN)))
		loss = pseudo_cum_loss/pseudo_cum_fundings 
		loss[np.isnan(loss)] = 0
		res = {'period':period,'loss':loss}
		return res

	@staticmethod
	def SMM_calc(bop_bal_array_IN,schedulprin_array_IN,prepay_array_IN):
		period = np.array(range(0,len(bop_bal_array_IN)))
		smm = prepay_array_IN/(bop_bal_array_IN - schedulprin_array_IN)
		smm[np.isnan(smm)] = 0
		res = {'period':period,'smm':smm}
		return res

	@staticmethod
	def MDR_calc(bop_bal_array_IN,schedulprin_array_IN,default_array_IN):
		period = np.array(range(0,len(bop_bal_array_IN)))
		mdr = default_array_IN/(bop_bal_array_IN-schedulprin_array_IN)
		mdr[np.isnan(mdr)] = 0
		res = {'period':period,'mdr':mdr}
		return res

	@staticmethod
	def Severity_calc(bop_bal_array_IN,default_array_IN,expected_recovery_array_IN):
		period = np.array(range(0,len(default_array_IN)))
		sev = (default_array_IN - expected_recovery_array_IN)/default_array_IN
		sev[np.isnan(sev)] = 0
		res = {'period':period,'sev':sev}
		return res

class AggAsset_Analytics(object):
	def __init__(self, bondDF_IN, annualyield_IN, frequency_IN,px_IN):
		# Standard Columns Name : fundings, total_cf, prin_cf, int_cf, default, loss
		self.bondDF = bondDF_IN
		self.annualyield = annualyield_IN
		self.frequency = frequency_IN
		self.px = px_IN

		self.formatting_mappings = {}
		self.update_formatting_mappings()
		self.rank_mappings = {}
		self.update_rank_mapping()

	def build_analytics_table(self):
		fundings_array = np.array(self.bondDF['fundings'])
		cf_array = np.array(self.bondDF['total_cf'])
		prin_cf_array = np.array(self.bondDF['prin_cf'])
		default_array = np.array(self.bondDF['default'])
		loss_array = np.array(self.bondDF['loss'])
		prepay_array = np.array(self.bondDF['prepay'])
		
		res = dict()
		res.update({u"价格":self.px})
		res.update({u"融资额度总和": StandardBond_Util.totalfundings_calc(fundings_array)})
		res.update({u"损益": StandardBond_Util.pnl_calc(fundings_array, cf_array)})
		res.update({u"内部回报率": StandardBond_Util.irr_calc(fundings_array, cf_array, self.frequency,self.px)})
		res.update({u"加权生命周期(现金流)": StandardBond_Util.WAL_calc(cf_array, self.frequency)})
		res.update({u"加权生命周期(本金)": StandardBond_Util.WAL_calc(prin_cf_array, self.frequency)})
		res.update({u"久期": StandardBond_Util.MacDur_calc(self.annualyield, cf_array, self.frequency)})
		res.update({u"累计早偿": StandardBond_Util.Cum_Prepay_calc(fundings_array,prepay_array)[-1]})
		res.update({u"累计违约": StandardBond_Util.Cum_Default_calc(fundings_array,default_array)[-1]})
		res.update({u"累计损失": StandardBond_Util.Cum_Loss_calc(fundings_array,loss_array)['loss'][-1]})

		return res

	def build_analytics_charts(self):
		fundings_array = np.array(self.bondDF['fundings'])
		bop_bal_array = np.array(self.bondDF['bop_bal'])
		prepay_array = np.array(self.bondDF['prepay'])
		scheduleprin_array = np.array(self.bondDF['schedule_prin'])
		default_array = np.array(self.bondDF['default'])
		loss_array = np.array(self.bondDF['loss'])
		expected_recovery_array = np.array(self.bondDF['expected_recovery'])

		res = dict()
		res.update({"smm_curve": StandardBond_Util.SMM_calc(bop_bal_array,scheduleprin_array,prepay_array)})
		res.update({"mdr_curve": StandardBond_Util.MDR_calc(bop_bal_array, scheduleprin_array,default_array)})
		res.update({"severity_curve": StandardBond_Util.Severity_calc(bop_bal_array,default_array,expected_recovery_array)})
		res.update({"cum_loss_curve": StandardBond_Util.Cum_Loss_calc(fundings_array, loss_array)})
				
		return res		

	def update_formatting_mappings(self):
		self.formatting_mappings[u'价格'] = GUI_Utilities.Formatter_dec2
		self.formatting_mappings[u'融资额度总和'] = GUI_Utilities.Formatter_dec0
		self.formatting_mappings[u'损益'] = GUI_Utilities.Formatter_dec0
		self.formatting_mappings[u'内部回报率'] = GUI_Utilities.Formatter_pct2
		self.formatting_mappings[u'加权生命周期(现金流)'] = GUI_Utilities.Formatter_dec2
		self.formatting_mappings[u'加权生命周期(本金)'] = GUI_Utilities.Formatter_dec2
		self.formatting_mappings[u'久期'] = GUI_Utilities.Formatter_dec2
		self.formatting_mappings[u'累计早偿'] = GUI_Utilities.Formatter_pct2
		self.formatting_mappings[u'累计违约'] = GUI_Utilities.Formatter_pct2
		self.formatting_mappings[u'累计损失'] = GUI_Utilities.Formatter_pct2


	def update_rank_mapping(self):
		self.rank_mappings = [u'价格',
							  u'融资额度总和',
							  u'损益',
							  u'内部回报率',
							  u'加权生命周期(现金流)',
							  u'加权生命周期(本金)',
							  u'久期',
							  u'累计早偿',
							  u'累计违约',
							  u'累计损失']



class LeveredEconomics_Analytics(object):
	def __init__(self, standardCF_IN,px_center_IN,px_steps_IN,px_step_size_IN):

		self.standardCF = standardCF_IN
		self.px_center = px_center_IN
		self.px_steps = px_steps_IN
		self.px_step_size = px_step_size_IN
		self.frequency = 12
		self.parse_px()

		self.build_analytics_table()

		self.ladder_formatting_mappings = {}
		self.first_financing_par_formatting_mappings = {}

		self.update_formatting_mappings()

		# self.rank_mappings = {}
		# self.update_rank_mapping()


	def update_formatting_mappings(self):

		self.ladder_formatting_mappings[u'Asset Px'] = GUI_Utilities.Formatter_dec1
		self.ladder_formatting_mappings[u'Yield'] = GUI_Utilities.Formatter_pct1
		self.ladder_formatting_mappings[u'Dur'] = GUI_Utilities.Formatter_dec2
		self.ladder_formatting_mappings[u'WAL'] = GUI_Utilities.Formatter_dec2
		self.ladder_formatting_mappings[u'CF WAL'] = GUI_Utilities.Formatter_dec2

		self.first_financing_par_formatting_mappings[u'资产净收益'] = GUI_Utilities.Formatter_pct1
		self.first_financing_par_formatting_mappings[u'资产费后净收益'] = GUI_Utilities.Formatter_pct1
		self.first_financing_par_formatting_mappings[u'债务成本'] = GUI_Utilities.Formatter_pct1
		self.first_financing_par_formatting_mappings[u'负债率'] = GUI_Utilities.Formatter_pct1
		self.first_financing_par_formatting_mappings[u'净息差'] = GUI_Utilities.Formatter_pct1
		self.first_financing_par_formatting_mappings[u'隐含ROE'] = GUI_Utilities.Formatter_pct1

	def build_analytics_table(self):
		
		self.res_snr = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])
		self.res_mezz = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])
		self.res_resid = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])
		self.res_equity = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])
		self.res_asset = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])
		self.res_ladder = pd.DataFrame(columns = [u'Tranche', u'Asset Px', u'Yield', u'Dur', u'WAL', u'CF WAL'])

		self.res_first_financing_par = pd.DataFrame(columns=['variable','VALUE AT PAR'])


		if 'MEZZ_new_funding' not in self.standardCF.columns.values:
			self.standardCF.loc[:,'MEZZ_new_funding'] = 0
			self.standardCF.loc[:,'MEZZ_total_cf'] = 0
			self.standardCF.loc[:,'MEZZ_prin_cf'] = 0
			self.standardCF.loc[:,'MEZZ_int_cf'] = 0
			self.standardCF.loc[:,'MEZZ_eop_bal'] = 0
			self.standardCF.loc[:,'MEZZ_effective_adv_rate'] = np.nan



		for each_px in self.px_step:
			snr_yield = StandardBond_Util.irr_calc(self.standardCF['SNR_new_funding'], self.standardCF['SNR_total_cf'], self.frequency,100.0)
			snr_dur = StandardBond_Util.MacDur_calc(snr_yield, self.standardCF['SNR_total_cf'],self.frequency)
			snr_wal = StandardBond_Util.WAL_calc(self.standardCF['SNR_prin_cf'], self.frequency)
			snr_cfwal = StandardBond_Util.WAL_calc(self.standardCF['SNR_total_cf'], self.frequency)


			mezz_yield = StandardBond_Util.irr_calc(self.standardCF['MEZZ_new_funding'], self.standardCF['MEZZ_total_cf'], self.frequency,100.0)
			mezz_dur = StandardBond_Util.MacDur_calc(mezz_yield, self.standardCF['MEZZ_total_cf'],self.frequency)
			mezz_wal = StandardBond_Util.WAL_calc(self.standardCF['MEZZ_prin_cf'], self.frequency)
			mezz_cfwal = StandardBond_Util.WAL_calc(self.standardCF['MEZZ_total_cf'], self.frequency)


			resid_yield = StandardBond_Util.irr_calc(self.standardCF['ASSET_new_funding'] * each_px/100.0 - self.standardCF['SNR_new_funding'] - self.standardCF['MEZZ_new_funding'], self.standardCF['RESID_total_cf'], self.frequency,100.0)

			resid_dur = StandardBond_Util.MacDur_calc(resid_yield, self.standardCF['RESID_total_cf'],self.frequency)
			resid_wal = StandardBond_Util.WAL_calc(self.standardCF['RESID_cf'], self.frequency)
			resid_cfwal = StandardBond_Util.WAL_calc(self.standardCF['RESID_total_cf'], self.frequency)

			equity_yield = resid_yield
			equity_dur = resid_dur
			equity_wal = resid_wal
			equity_cfwal = resid_cfwal

			asset_yield = StandardBond_Util.irr_calc(self.standardCF['ASSET_new_purchase'], self.standardCF['ASSET_total_cf'], self.frequency,each_px)
			asset_dur = StandardBond_Util.MacDur_calc(asset_yield, self.standardCF['ASSET_total_cf'],self.frequency)
			asset_wal = StandardBond_Util.WAL_calc(self.standardCF['ASSET_prin_cf'], self.frequency)
			asset_cfwal = StandardBond_Util.WAL_calc(self.standardCF['ASSET_total_cf'], self.frequency)

			self.res_snr.loc[len(self.res_snr)] = ["优先", each_px,snr_yield,snr_dur,snr_wal,snr_cfwal]
			self.res_mezz.loc[len(self.res_mezz)] = ["夹层",each_px,mezz_yield,mezz_dur,mezz_wal,mezz_cfwal]
			self.res_resid.loc[len(self.res_resid)] = ["劣后", each_px,resid_yield,resid_dur,resid_wal,resid_cfwal]
			self.res_equity.loc[len(self.res_equity)] = ["权益", each_px,equity_yield,equity_dur,equity_wal,equity_cfwal]
			self.res_asset.loc[len(self.res_asset)] = ["资产", each_px,asset_yield,asset_dur,asset_wal,asset_cfwal]


		self.res_ladder = self.res_ladder.append(self.res_snr,ignore_index = True)
		self.res_ladder = self.res_ladder.append(self.res_mezz,ignore_index = True)
		self.res_ladder = self.res_ladder.append(self.res_resid,ignore_index = True)
		self.res_ladder = self.res_ladder.append(self.res_equity,ignore_index = True)
		self.res_ladder = self.res_ladder.append(self.res_asset,ignore_index = True)


		asset_net_yield = StandardBond_Util.irr_calc(self.standardCF['ASSET_new_purchase'], self.standardCF['ASSET_total_cf'], self.frequency,100.0)
		asset_net_yield_post_fee = StandardBond_Util.irr_calc(self.standardCF['ASSET_new_purchase'], self.standardCF['ASSET_total_cf'] - self.standardCF['FEE_paid_fee'], self.frequency,100.0)
		debt_cost = sum(self.standardCF['SNR_int_cf'] + self.standardCF['MEZZ_int_cf'])/sum(self.standardCF['SNR_eop_bal'] + self.standardCF['MEZZ_eop_bal']) * self.frequency
		effective_adv_rate = sum(self.standardCF['SNR_eop_bal'] +  self.standardCF['MEZZ_eop_bal'])/sum(self.standardCF['ASSET_eop_bal'])		
		NIM = asset_net_yield_post_fee - debt_cost * effective_adv_rate
		implied_roe = NIM/(1-effective_adv_rate)

		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'资产净收益',asset_net_yield]
		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'资产费后净收益',asset_net_yield_post_fee]
		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'债务成本',debt_cost]
		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'负债率',effective_adv_rate]
		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'净息差',NIM]
		self.res_first_financing_par.loc[len(self.res_first_financing_par)] = [u'隐含ROE',implied_roe]







	def parse_px(self):
		self.px_step = np.arange(self.px_center - self.px_step_size * self.px_steps, self.px_center + self.px_step_size * (self.px_steps+1), self.px_step_size)


def main():
	standardCF_IN = pd.read_pickle("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\leveredecon.pickle")
	px_center_IN = 100
	px_steps_IN = 3
	px_step_size_IN = 0.5
	
	LeveredEconomics_Analytics_instance = LeveredEconomics_Analytics(standardCF_IN,px_center_IN,px_steps_IN,px_step_size_IN)




	# fundings_array = np.array([290,0,0,0,0,0,0,0])
	# cf_array = np.array([0,60,60,60,30,30,30,30])

	# a = StandardBond_Util.MacDur_calc(yield_IN = 0.120937, cf_array_IN = cf_array, frequency_IN = 12)
	# print a

	# fundings_array_IN = np.array([1,2,3])
	# default_array_IN = np.array([0.5,0.5,0.5])

	# a = StandardBond_Util.Cum_Default_calc(fundings_array_IN = fundings_array_IN, default_array_IN=default_array_IN)
	# print a	

if __name__ == "__main__":
	main()