
# -*- coding: utf-8 -*-
import os
import shutil
import pandas as pd
import numpy as np
import sys
import webbrowser
import random
import string
from Strats_Analytics import Strats_Analytics
from IO_Util import IO_Util
reload(sys)
sys.setdefaultencoding("gb2312")


def analytics_procedure(
						rawtape_df,
						dimensions_settings,
						measures_settings,
						source_strats_folder_dir,
						temp_strats_folder_dir,
						strats_sort_by,
						strats_display_topn
						):

	load_strats_analytics_instance = False
	for idx,row in dimensions_settings.iterrows():
		dimension_column = row['column']
		sl = row['strats_label']
		group_rule = row['group_rule']
		source_starts_txt_file_dir = source_strats_folder_dir + "\\" + sl + "_" + "strats" + ".txt"
		temp_starts_txt_file_dir = temp_strats_folder_dir + "\\" + sl + "_" + "strats" + ".txt"
		res = pd.read_csv(source_starts_txt_file_dir, sep = "|",encoding = 'gb2312')

		if group_rule == group_rule: # with group rule
			pass
		else:
			if len(res)<=(strats_display_topn+1): # without group rule, but total bucket <= top N
				strats_total_line = res.loc[res.ix[:,0] == 'Total',:]
				strats_total_line =strats_total_line.loc[strats_total_line.index[0],:].values
				strats_wo_total_line = res.loc[res.ix[:,0] != 'Total',:]
				strats_wo_total_line = strats_wo_total_line.sort_values([strats_wo_total_line.columns.values[strats_sort_by]], ascending=[False])

				res = strats_wo_total_line
				res = res.reset_index(drop=True)
				res.loc[len(res)] = strats_total_line

			else:  # without group rule, and total bucket > top N
				if not load_strats_analytics_instance:
					Strats_Analytics_instance = Strats_Analytics(rawtape_df,dimensions_settings,measures_settings)
					load_strats_analytics_instance = True

				strats_total_line = res.loc[res.ix[:,0] == 'Total',:]
				strats_total_line =strats_total_line.loc[strats_total_line.index[0],:].values
				strats_wo_total_line = res.loc[res.ix[:,0] != 'Total',:]
				strats_wo_total_line = strats_wo_total_line.sort_values([strats_wo_total_line.columns.values[strats_sort_by]], ascending=[False])
				topn_bucket_list = strats_wo_total_line.head(strats_display_topn).ix[:,0].values

				the_target_other_dict = {"column":dimension_column,"topn_bucket_list":topn_bucket_list}
				Strats_Analytics_instance.update_target_other_dict(the_target_other_dict)
				Strats_Analytics_instance.run_tape_extension_procedure_target_other()
				others_line = Strats_Analytics_instance.analytics_procedure()

				strats_topn_line = strats_wo_total_line.head(strats_display_topn)
				res = strats_topn_line
				res = res.reset_index(drop=True)
				res.loc[len(res)] = others_line
				res.loc[len(res)] = strats_total_line
		
		res.to_csv(temp_starts_txt_file_dir, index = False, sep = "|",encoding = 'gb2312')
