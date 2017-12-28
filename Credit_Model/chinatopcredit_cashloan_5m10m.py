import pandas as pd
import numpy as np
import os
import sys
import math
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from Config import Config
from IO_Utilities import IO_Utilities
# IO_Utilities.IO_Util.open_in_html(static_betas_5m_prepay)

class chinatopcredit_cashloan_5m10m(object):
	def __init__(self, static_pool_IN,smm_multi_IN = 1, mdr_multi_IN = 1):
		self.static_pool = static_pool_IN
		self.smm_multi = smm_multi_IN
		self.mdr_multi = mdr_multi_IN

		self.idx_5m = self.static_pool[self.static_pool['term']==5].index
		self.idx_10m = self.static_pool[self.static_pool['term']==10].index
		self.idx_15m = self.static_pool[self.static_pool['term']==15].index
		self.idx_20m = self.static_pool[self.static_pool['term']==20].index

		self.prepay_5m_betas = pd.read_csv("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Credit_Model_Betas\chinatopcredit_5m_cashloan_prepay.csv")
		self.prepay_10m_betas = pd.read_csv("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Credit_Model_Betas\chinatopcredit_10m_cashloan_prepay.csv")
		self.default_5m_betas = pd.read_csv("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Credit_Model_Betas\chinatopcredit_5m_cashloan_default.csv")
		self.default_10m_betas = pd.read_csv("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Credit_Model_Betas\chinatopcredit_10m_cashloan_default.csv")

		self.smm_mdr_scale = pd.read_csv("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Credit_Model_Betas\smm_mdr_scale.csv")

		self.logit_prepay_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number','mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']).fillna(0)
		self.logit_default_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number','mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']).fillna(0)

		self.logit_prepay_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']
		self.logit_default_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']

		self.smm_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number','mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15','mob_16','mob_17','mob_18','mob_19','mob_20']).fillna(0)
		self.mdr_matrix = pd.DataFrame(index = self.static_pool.index,columns = ['BHHJ_Loan_Number','mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15','mob_16','mob_17','mob_18','mob_19','mob_20']).fillna(0)

		self.smm_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']
		self.mdr_matrix.loc[:,'BHHJ_Loan_Number'] = self.static_pool.loc[:,'BHHJ_Loan_Number']

	def run_prepay_default(self):

		static_feature_5m_raw = self.static_pool.loc[self.idx_5m,['borrower_age','gender','original_balance','platform_score','feeratio']]
		static_feature_10m_raw = self.static_pool.loc[self.idx_10m,['borrower_age','gender','original_balance','platform_score','feeratio']]

		# **************************************    5m term Prepay   **************************************
		static_feature_5m_prepay = pd.DataFrame(index = self.idx_5m, columns = ['Intercept','Borrower Age','Gender_Indicator','Amt_lt_1000','Amt_bt_1000_2000','Amt_bt_2000_3500','Amt_bt_3500_5000'])

		static_feature_5m_prepay['Intercept'] = 1
		static_feature_5m_prepay['Borrower Age'] = static_feature_5m_raw['borrower_age'].values
		static_feature_5m_prepay['Gender_Indicator'] = 1 * (static_feature_5m_raw['gender'] == 'M')
		static_feature_5m_prepay['Amt_lt_1000'] = 1 * (static_feature_5m_raw['original_balance'] <= 1000)
		static_feature_5m_prepay['Amt_bt_1000_2000'] = 1 * (static_feature_5m_raw['original_balance'] > 1000) * (static_feature_5m_raw['original_balance'] <= 2000)
		static_feature_5m_prepay['Amt_bt_2000_3500'] = 1 * (static_feature_5m_raw['original_balance'] > 2000) * (static_feature_5m_raw['original_balance'] <= 3500)
		static_feature_5m_prepay['Amt_bt_3500_5000'] = 1 * (static_feature_5m_raw['original_balance'] > 3500) * (static_feature_5m_raw['original_balance'] <= 5000)

		static_betas_5m_prepay = []
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'intercept','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'borrower age','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'gender','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'amt_lt_1000','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'amt_bt_1000_2000','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'amt_bt_2000_3500','Betas'].values[0])
		static_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'amt_bt_3500_5000','Betas'].values[0])

		logit_static_5m_prepay = (np.matrix(static_feature_5m_prepay)) * (np.matrix(static_betas_5m_prepay).T)

		dynamic_betas_5m_prepay = []
		dynamic_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'mob*(mob<=3)','Betas'].values[0])
		dynamic_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'mob*(mob>3)','Betas'].values[0])
		dynamic_betas_5m_prepay.append(self.prepay_5m_betas.loc[self.prepay_5m_betas['x'] == 'mob(>3)','Betas'].values[0])

		self.logit_prepay_matrix.loc[self.idx_5m,'mob_1'] = 1 * dynamic_betas_5m_prepay[0] + logit_static_5m_prepay
		self.logit_prepay_matrix.loc[self.idx_5m,'mob_2'] = 2 * dynamic_betas_5m_prepay[0] + logit_static_5m_prepay
		self.logit_prepay_matrix.loc[self.idx_5m,'mob_3'] = 3 * dynamic_betas_5m_prepay[0] + logit_static_5m_prepay
		self.logit_prepay_matrix.loc[self.idx_5m,'mob_4'] = 4 * dynamic_betas_5m_prepay[1] + dynamic_betas_5m_prepay[2] + logit_static_5m_prepay
		self.logit_prepay_matrix.loc[self.idx_5m,'mob_5'] = 5 * dynamic_betas_5m_prepay[1] + dynamic_betas_5m_prepay[2] + logit_static_5m_prepay
		
		self.smm_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] = self.logit_prepay_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']].applymap(lambda x: 1/(1+np.exp(-x)))
		self.smm_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] = self.smm_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] * self.smm_mdr_scale.loc[(self.smm_mdr_scale['term']==5) & (self.smm_mdr_scale['mdr_smm']=='smm'),'scale_factor'].values[0]
		# **************************************    5m term Prepay   **************************************


		# **************************************    5m term default   **************************************
		static_feature_5m_default = pd.DataFrame(index = static_feature_5m_raw.index, columns = ['Intercept','Gender_Indicator','Amt_lt_2000','Amt_bt_2000_3000','feeratio_bt_2_4','feeratio_bt_4_6','feeratio_bt_6_8','score_lt_590'])

		static_feature_5m_default['Intercept'] = 1
		static_feature_5m_default['Gender_Indicator'] = 1 * (static_feature_5m_raw['gender'] == 'M')
		static_feature_5m_default['Amt_lt_2000'] = 1 * (static_feature_5m_raw['original_balance'] <= 2000)
		static_feature_5m_default['Amt_bt_2000_3000'] = 1 * (static_feature_5m_raw['original_balance'] > 2000) * (static_feature_5m_raw['original_balance'] <= 3000)
		static_feature_5m_default['feeratio_bt_2_4'] = 1 * (static_feature_5m_raw['feeratio'] > 0.02) * (static_feature_5m_raw['feeratio'] <= 0.04)
		static_feature_5m_default['feeratio_bt_4_6'] = 1 * (static_feature_5m_raw['feeratio'] > 0.04) * (static_feature_5m_raw['feeratio'] <= 0.06)
		static_feature_5m_default['feeratio_bt_6_8'] = 1 * (static_feature_5m_raw['feeratio'] > 0.06) * (static_feature_5m_raw['feeratio'] <= 0.08)
		static_feature_5m_default['score_lt_590'] = 1 * (static_feature_5m_raw['platform_score'] <= 590)

		static_betas_5m_default = []
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'intercept','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'gender_indicator','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'amt_lt_2000','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'amt_bt_2000_3000','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'feeratio_bt_2_4','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'feeratio_bt_4_6','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'feeratio_bt_6_8','Betas'].values[0])
		static_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'score_lt_590','Betas'].values[0])

		logit_static_5m_default = (np.matrix(static_feature_5m_default)) * (np.matrix(static_betas_5m_default).T)

		dynamic_betas_5m_default = []
		dynamic_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'mob*(mob==1)','Betas'].values[0])
		dynamic_betas_5m_default.append(self.default_5m_betas.loc[self.default_5m_betas['x'] == 'mob*(mob>1)','Betas'].values[0])

		self.logit_default_matrix.loc[self.idx_5m,'mob_1'] = 1 * dynamic_betas_5m_default[0] + logit_static_5m_default
		self.logit_default_matrix.loc[self.idx_5m,'mob_2'] = 2 * dynamic_betas_5m_default[1] + logit_static_5m_default
		self.logit_default_matrix.loc[self.idx_5m,'mob_3'] = 3 * dynamic_betas_5m_default[1] + logit_static_5m_default
		self.logit_default_matrix.loc[self.idx_5m,'mob_4'] = 4 * dynamic_betas_5m_default[1] + logit_static_5m_default
		self.logit_default_matrix.loc[self.idx_5m,'mob_5'] = 5 * dynamic_betas_5m_default[1] + logit_static_5m_default

		self.mdr_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] = self.logit_default_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']].applymap(lambda x: 1/(1+np.exp(-x)))
		self.mdr_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] = self.mdr_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5']] * self.smm_mdr_scale.loc[(self.smm_mdr_scale['term']==5) & (self.smm_mdr_scale['mdr_smm']=='mdr'),'scale_factor'].values[0]
		# **************************************    5m term default   **************************************

		# **************************************    10m term Prepay   **************************************
		static_feature_10m_prepay = pd.DataFrame(index = self.idx_10m, columns = ['Intercept','Gender_Indicator','Amt_lt_1000','Amt_bt_1000_2500'])

		static_feature_10m_prepay['Intercept'] = 1
		static_feature_10m_prepay['Gender_Indicator'] = 1 * (static_feature_10m_raw['gender'] == 'M')
		static_feature_10m_prepay['Amt_lt_1000'] = 1 * (static_feature_10m_raw['original_balance'] <= 1000)
		static_feature_10m_prepay['Amt_bt_1000_2500'] = 1 * (static_feature_10m_raw['original_balance'] > 1000) * (static_feature_10m_raw['original_balance'] <= 2500)

		static_betas_10m_prepay = []
		static_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'intercept','Betas'].values[0])
		static_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'gender','Betas'].values[0])
		static_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'amt_lt_1000','Betas'].values[0])
		static_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'amt_bt_1000_2500','Betas'].values[0])

		logit_static_10m_prepay = (np.matrix(static_feature_10m_prepay)) * (np.matrix(static_betas_10m_prepay).T)

		dynamic_betas_10m_prepay = []
		dynamic_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'mob*(mob<=3)','Betas'].values[0])
		dynamic_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'mob*(mob>3)','Betas'].values[0])
		dynamic_betas_10m_prepay.append(self.prepay_10m_betas.loc[self.prepay_10m_betas['x'] == 'mob>3','Betas'].values[0])

		self.logit_prepay_matrix.loc[self.idx_10m,'mob_1'] = 1 * dynamic_betas_10m_prepay[0] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_2'] = 2 * dynamic_betas_10m_prepay[0] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_3'] = 3 * dynamic_betas_10m_prepay[0] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_4'] = 4 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_5'] = 5 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_6'] = 6 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_7'] = 7 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_8'] = 7 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_9'] = 7 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay
		self.logit_prepay_matrix.loc[self.idx_10m,'mob_10'] = 7 * dynamic_betas_10m_prepay[1] + dynamic_betas_10m_prepay[2] + logit_static_10m_prepay

		self.smm_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.logit_prepay_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']].applymap(lambda x: 1/(1+np.exp(-x)))
		self.smm_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.smm_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.smm_mdr_scale.loc[(self.smm_mdr_scale['term']==10) & (self.smm_mdr_scale['mdr_smm']=='smm'),'scale_factor'].values[0]
		# **************************************    10m term Prepay   **************************************


		# **************************************    10m term Default   **************************************
		static_feature_10m_default = pd.DataFrame(index = self.idx_10m, columns = ['Intercept','Gender_Indicator','Amt_lt_1000','Amt_bt_1000_2500','Feeratio_lt_7','Feeratio_bt_7_11','Score_lt_590'])

		static_feature_10m_default['Intercept'] = 1
		static_feature_10m_default['Gender_Indicator'] = 1 * (static_feature_10m_raw['gender'] == 'M')
		static_feature_10m_default['Amt_lt_1000'] = 1 * (static_feature_10m_raw['original_balance'] <= 1000)
		static_feature_10m_default['Amt_bt_1000_2500'] = 1 * (static_feature_10m_raw['original_balance'] > 1000) * (static_feature_10m_raw['original_balance'] <= 2500)
		static_feature_10m_default['Feeratio_lt_7'] = 1 * (static_feature_10m_raw['feeratio'] <= 0.07)
		static_feature_10m_default['Feeratio_bt_7_11'] = 1 * (static_feature_10m_raw['feeratio'] > 0.07) * (static_feature_10m_raw['feeratio'] <= 0.11)
		static_feature_10m_default['Score_lt_590'] = 1 * (static_feature_10m_raw['platform_score'] <= 590)

		static_betas_10m_default = []
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'intercept','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'gender','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'amt_lt_1000','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'amt_bt_1000_2500','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'feeratio_lt_7','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'feeratio_bt_7_11','Betas'].values[0])
		static_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'score_lt_590','Betas'].values[0])

		logit_static_10m_default = (np.matrix(static_feature_10m_default)) * (np.matrix(static_betas_10m_default).T)

		dynamic_betas_10m_default = []
		dynamic_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'mob*(mob==1)','Betas'].values[0])
		dynamic_betas_10m_default.append(self.default_10m_betas.loc[self.default_10m_betas['x'] == 'mob*(mob>1)','Betas'].values[0])

		self.logit_default_matrix.loc[self.idx_10m,'mob_1'] = 1 * dynamic_betas_10m_default[0] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_2'] = 2 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_3'] = 3 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_4'] = 4 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_5'] = 5 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_6'] = 6 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_7'] = 7 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_8'] = 7 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_9'] = 7 * dynamic_betas_10m_default[1] + logit_static_10m_default
		self.logit_default_matrix.loc[self.idx_10m,'mob_10'] = 7 * dynamic_betas_10m_default[1] + logit_static_10m_default

		self.mdr_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.logit_default_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']].applymap(lambda x: 1/(1+np.exp(-x)))
		self.mdr_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.mdr_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.smm_mdr_scale.loc[(self.smm_mdr_scale['term']==10) & (self.smm_mdr_scale['mdr_smm']=='mdr'),'scale_factor'].values[0]
		# **************************************    10m term Default   **************************************


		# ************************ multiply mdr and smm with multipliers ************************
		self.mdr_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.mdr_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.mdr_multi
		self.smm_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.smm_matrix.loc[self.idx_10m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.smm_multi

		self.mdr_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.mdr_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.mdr_multi
		self.smm_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] = self.smm_matrix.loc[self.idx_5m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10']] * self.smm_multi
		# ************************ multiply mdr and smm with multipliers ************************

		# **************************************    15m term Default and Prepay  **************************************
		self.mdr_matrix.loc[self.idx_15m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15']] = \
		[
		 0.0035,0.0056,0.0035,0.0078,0.0030,
		 0.005,0.005,0.005,0.005,0.005,
		 0.005,0.005,0.005,0.005,0.005
		]

		self.smm_matrix.loc[self.idx_15m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15']] = \
		[
		 0.0062,0.0363,0.0281,0.0163,0.0173,
		 0.015,0.015,0.015,0.015,0.015,
		 0.015,0.015,0.015,0.015,0.015
		]

		# **************************************    15m term Default and Prepay  **************************************



		# **************************************    20m term Default and Prepay  **************************************
		self.mdr_matrix.loc[self.idx_20m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15','mob_16','mob_17','mob_18','mob_19','mob_20']] = \
		[0.0045] * 20

		self.smm_matrix.loc[self.idx_20m,['mob_1','mob_2','mob_3','mob_4','mob_5','mob_6','mob_7','mob_8','mob_9','mob_10','mob_11','mob_12','mob_13','mob_14','mob_15','mob_16','mob_17','mob_18','mob_19','mob_20']] = \
		[0.0045] * 20

		# **************************************    20m term Default and Prepay  **************************************





def main():
	# df = pd.read_pickle('F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\staticpool.pickle')
	test_instance = chinatopcredit_cashloan_5m10m(df)


if __name__ == "__main__":
	main()