
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

reload(sys)
sys.setdefaultencoding( "gb2312" )

class Strats_Analytics(object):
	def __init__(self, the_rawtape, the_dimensions_settings, the_measures_settings, the_rules_mapping = None, the_target_other_dict = None,add_code_IN = ''):
		self.rawtape = the_rawtape
		self.dimensions_settings = the_dimensions_settings
		self.measures_settings = the_measures_settings
		self.rules_mapping = the_rules_mapping


		self.datatype_dict = dict()
		# self.rtd_res = pd.DataFrame(columns = ['name','datatype','count','unique','mode','mean','std', 'min', '25%','50%','75%','max','sum'])
		self.add_code = add_code_IN
		self.data_parser = Data_Parser(self.rawtape,self.add_code)

		self.run_data_parser()

		self.func_dict = dict()
		self.target_other_dict = the_target_other_dict
		

	def run_data_parser(self):
		self.data_parser.parser_procedure()
		self.rawtape = self.data_parser.df
		self.datatype_dict = self.data_parser.datatype_dict


	def update_target_other_dict(self, the_target_other_dict):
		self.target_other_dict = the_target_other_dict
	
	def run_tape_extension_procedure(self):
		self.rawtape_extension = self.rawtape.copy()

		self.dimensions_settings.loc[:][u'strats_label_effective'] = self.dimensions_settings.loc[:][u'strats_label']
		self.dimensions_settings.loc[self.dimensions_settings[u'strats_label_effective'] == self.dimensions_settings[u'column'],u'strats_label_effective'] += "(sl)"
		
		# for key,value in self.datatype_dict.items():
		# 	print key
		# 	print value


		for index, row in self.dimensions_settings.iterrows():
			effective_sl = row['strats_label_effective']
			col = row['column']

			datatype = self.datatype_dict[unicode(col)]

			if row['group_rule']>0: #group rule has input, otherwise NULL				
				rule_mapping = self.rules_mapping.loc[self.rules_mapping['Rule_Name'] == row['group_rule'],:]
				rule_mapping.loc[:,'Lower_Bound'] = rule_mapping.loc[:,'Lower_Bound'].fillna(-np.Infinity)
				rule_mapping.loc[:,'Upper_Bound'] = rule_mapping.loc[:,'Upper_Bound'].fillna(np.Infinity)
				length = len(rule_mapping)

				raw_bins = [rule_mapping.loc[rule_mapping.index[0],u'Lower_Bound']] + (list(rule_mapping.loc[:,'Upper_Bound']))
				print raw_bins

				if datatype in ["float","int"]:
					effective_bins = [float(item) for item in raw_bins]
				elif datatype in ["datetime"]:
					effective_bins = [datetime.datetime.strptime(item, "%Y/%m/%d") for item in raw_bins]
				bins_cut = pd.cut(np.array(self.rawtape_extension[col]), bins = effective_bins, right=False, labels=np.array(rule_mapping[u'Label']), retbins=False, precision=3, include_lowest=True)
				self.rawtape_extension.loc[:,effective_sl] = bins_cut
				self.rawtape_extension.loc[:,effective_sl] = self.rawtape_extension.loc[:,effective_sl].astype('string')
			else:
				self.rawtape_extension.loc[:,effective_sl] = self.rawtape_extension.loc[:,col]
			self.rawtape_extension.loc[:,effective_sl] = self.rawtape_extension.loc[:,effective_sl].fillna("MISSING")
		self.rawtape_extension.loc[:,'Total'] = 'Total'
		self.rawtape_extension.loc[:,'Temp_Null'] = np.nan

	def run_tape_extension_procedure_target_other(self):
		col = self.target_other_dict["column"]
		topn_bucket_list = self.target_other_dict["topn_bucket_list"]

		self.rawtape_extension = self.rawtape.copy()
		
		self.rawtape_extension.loc[:][u'other_target'] = "Others"
		self.rawtape_extension.loc[self.rawtape_extension[col].isin(topn_bucket_list),u'other_target'] = 'Not Others'
		self.rawtape_extension.loc[:,'Total'] = 'Total'
		self.rawtape_extension.loc[:,'Temp_Null'] = np.nan

	def func_define(self,calc_method, helper = None):
		if calc_method == 'Count':
			self.func_dict[calc_method] = lambda x: np.size(x)
		if calc_method == 'Count %':
			self.func_dict[calc_method] = lambda x: np.size(x)/(len(self.rawtape_extension)*1.0)
		if calc_method == 'Sum':
			self.func_dict[calc_method] = lambda x: np.sum(x)
		if calc_method == 'Min':
			self.func_dict[calc_method] = lambda x: np.min(x)
		if calc_method == 'Sum %':
			self.func_dict[calc_method] = lambda x: np.sum(x)*1.0/self.rawtape_extension[x.name].sum()
		if calc_method == 'Wt_Avg':
			self.func_dict[calc_method + helper] = lambda x: 0 if self.rawtape_extension.loc[x.index, helper].sum() == 0 else np.average(x, weights=self.rawtape_extension.loc[x.index, helper])
		if calc_method == 'Avg':
			self.func_dict[calc_method] = lambda x: np.average(x)
		if calc_method == 'Divide':
			self.func_dict[calc_method + helper] = lambda x: np.sum(x)*1.0/self.rawtape_extension.loc[x.index, helper].sum()
		if calc_method == 'Countif_Over30':
			self.func_dict[calc_method] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>30)
		if calc_method == 'Countif_Over60':
			self.func_dict[calc_method] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>60)
		if calc_method == 'Countif_Over90':
			self.func_dict[calc_method] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>90)
		if calc_method == 'Countif_Over30_Ratio':
			self.func_dict[calc_method + helper] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>30)*1.0/len(self.rawtape_extension.loc[x.index, helper])
		if calc_method == 'Countif_Over60_Ratio':
			self.func_dict[calc_method + helper] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>60)*1.0/len(self.rawtape_extension.loc[x.index, helper])
		if calc_method == 'Countif_Over90_Ratio':
			self.func_dict[calc_method + helper] = lambda x: sum(self.rawtape_extension.loc[x.index,x.name]>90)*1.0/len(self.rawtape_extension.loc[x.index, helper])

	def analytics_procedure(self):

		measures_column_set =  set(self.measures_settings.loc[self.measures_settings[u'column']>0, u'column'].values)
		measures_helper_set =  set(self.measures_settings.loc[self.measures_settings[u'calc_helper']>0, u'calc_helper'].values)
		measures_union_col_list = list(measures_column_set | measures_helper_set)

		# define group calc function
		for calc_method,calc_helper in zip(list(self.measures_settings['calc_method']),list(self.measures_settings['calc_helper'])):
			self.func_define(calc_method,calc_helper)

		calc_func_handle = {}
		for measure_col in self.measures_settings[u'column'].unique():
			calc_func_handle[measure_col] = {}

			calc_method_list = self.measures_settings.loc[self.measures_settings['column'] == measure_col,'calc_method']
			calc_helper_list = self.measures_settings.loc[self.measures_settings['column'] == measure_col,'calc_helper']
			col_name_list = self.measures_settings.loc[self.measures_settings['column'] == measure_col,'col_name']

			for calc_method,calc_helper,col_name in zip(calc_method_list,calc_helper_list,col_name_list):
				calc_full_name = calc_method + (calc_helper if calc_helper == calc_helper else "")
				calc_func_handle[measure_col][col_name] = self.func_dict[calc_full_name]

		col_name_list = self.measures_settings.loc[:,'col_name'].values
		
		if self.target_other_dict is not None:

			effective_sl = "other_target"
			groupby_handle = self.rawtape_extension.groupby(effective_sl)
			other_target_res = groupby_handle.agg(calc_func_handle)
			other_target_res.columns = other_target_res.columns.droplevel(level = 0)
			other_target_res = other_target_res.loc[:,col_name_list]
			others_line = ['Others'] + list(other_target_res.loc['Others'])
		
			return others_line
		else:

			effective_sl = "Total"
			groupby_handle = self.rawtape_extension.groupby(effective_sl)
			total_res = groupby_handle.agg(calc_func_handle)
			total_res.columns = total_res.columns.droplevel(level = 0)
			total_res = total_res.loc[:,col_name_list]

			strats_res = {}
			for dimension_idx, dimension_row in self.dimensions_settings.iterrows():
				sl = dimension_row['strats_label']
				effective_sl = dimension_row['strats_label_effective']
				groupby_handle = self.rawtape_extension.groupby(effective_sl)
				res = groupby_handle.agg(calc_func_handle)
				res.columns = res.columns.droplevel(level = 0)
				res = res.loc[:,col_name_list]
				
				res = res.reset_index(drop = False)

				res.loc[len(res)] = ['Total'] + list(total_res.loc['Total'])

				strats_res[sl] = res

			return strats_res

