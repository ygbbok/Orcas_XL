# -*- coding: utf-8 -*-

############# comment

import sys
import os
import shutil
reload(sys)
sys.setdefaultencoding( "gb2312" )

Orcas_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(Orcas_dir, 'Strats_Analytics\\'))


import pandas as pd
import numpy as np
import Tkinter as Tkinter
import ttk as ttk
from Struct_Model import Struct_CF_Model as Struct_CF_Model
from Struct_Model import Struct_GUI_Model as Struct_GUI_Model
import pickle
from datetime import datetime
from Config import Config


import matplotlib
import pylab
import Tix

from IO_Utilities import IO_Utilities
from Calc_Utilities import Calc_Utilities
from Other_Utilities import Other_Utilities

# Credit Model
from Credit_Model import Credit_GUI_Model
from Credit_Model import chinatopcredit_cashloan_5m10m
from Credit_Model import vallina_cpr_cdr
from Credit_Model import vallina_smm_mdr

# Cashflow Engine
from Cashflow_Engine import cashloan_ctc_mode
from Cashflow_Engine import generic_cashloan_mode

# Global Constant Variables

# Utilities
from IO_Utilities import IO_Utilities
from Other_Utilities import Other_Utilities
from GUI_Utilities import GUI_Utilities

# Strats related
from Strats import Strats_Interface
import Strats_Analytics
import Strats_Display
from RTD_Analytics import RTD_Analytics

# Vintage Analysis related
from Vintage import Vintage_Interface
reload(sys)
sys.setdefaultencoding("gb2312")

import getpass
orcas_user = getpass.getuser()

class Orcas_Wrapper(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.grand_left_frame = Tkinter.Frame(self)
		self.grand_right_frame = Tkinter.Frame(self)

		self.grand_left_frame.pack(side = 'left')
		self.grand_right_frame.pack(side = 'left')

		self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame)
		self.grand_right_lower_frame = Tkinter.Frame(self.grand_right_frame)

		self.grand_right_upper_frame.pack(side = 'top')
		self.grand_right_lower_frame.pack(side = 'top')

		self.notebook = ttk.Notebook(self.grand_left_frame)
		self.notebook.pack()

		self.dashboard_label = Tkinter.Label(self.grand_left_frame,text='未载入任何资产池分析实例',bg = Config.Orcas_green)
		self.dashboard_label.pack(side = 'top',anchor = 'center',expand = 'yes',fill = 'x')


		self.live_structure = None
		self.live_structure_gui = None
		
		self.StratsPage_design()
		self.notebook.add(self.StratsPage_Frame, text="统计分层分析")

		self.VintageAnalysisPage_design()
		self.notebook.add(self.VintageAnalysisPage_Frame, text="Vintage Analysis")

		self.Mgmt_Static_Pool_df = pd.read_pickle(Config.Mgmt_Static_Pool_File)
		self.StaticPoolPage_design()
		self.notebook.add(self.StaticPoolPage_Frame, text=u"资产池")

		self.Mgmt_Static_Pool_list = [unicode(item) for item in list(self.Mgmt_Static_Pool_df[u'资产池编号'].astype(str) + " - "
			+ self.Mgmt_Static_Pool_df[u'资产池名称'].astype(str))]
		self.Mgmt_Unlevered_Economics_df = pd.read_pickle(Config.Mgmt_Unlevered_Economics_Run_File)
		self.Mgmt_Levered_Economics_df = pd.read_pickle(Config.Mgmt_Levered_Economics_Run_File)


		self.UnleveredEconomicsPage_design()
		self.notebook.add(self.UnleveredEconomicsPage_Frame, text=u"资产池现金流分析")

		self.FinancingMgmtPage_design()
		self.notebook.add(self.FinancingMgmtPage_Frame, text="ABS结构化融资分析")

		self.cashflow_df = pd.DataFrame()

	def update_unlevered_economics_static_pool_optionmenu(self):
		self.Mgmt_Static_Pool_list = list(self.Mgmt_Static_Pool_df[u'资产池编号'].astype(str) + " - " + self.Mgmt_Static_Pool_df[u'资产池名称'].astype(str))
		self.Static_Pool_option['values'] = [unicode(item) for item in self.Mgmt_Static_Pool_list]

	def createStaticPool(self):

		static_pool_name = self.StaticPoolName_TextBox.get()

		self.StaticPool_list = self.StaticPool_text.get("1.0","end-1c")
		self.StaticPool_list = self.StaticPool_list.split('\n')
		self.StaticPool_list = [item for item in self.StaticPool_list if len(item)>0]

		if len(self.StaticPool_list)>0:
			BHHJ_Loan_Number_array = np.array(self.StaticPool_list)

		elif len(self.StaticPool_list) == 0:				
			self.StaticPoolCondition_Instance.get_all(dict_type = True)

			sql_script = IO_Utilities.SQL_Util.script_generator_engine_1(table_IN = "[dbo].[BHHJ_marketplace_consumer_loan]",condition_list_IN = self.StaticPoolCondition_Instance.res)
			self.live_static_pool_df = IO_Utilities.SQL_Util.query_sql_procedure(sql_script_IN = sql_script)[0]

			BHHJ_Loan_Number_array = np.array(self.live_static_pool_df['BHHJ_Loan_Number'].values)
		
		new_static_pool_num = max(self.Mgmt_Static_Pool_df[u'资产池编号']) + 1
		np.save(Config.Static_Pool_Folder+ str(new_static_pool_num) + ".npy",BHHJ_Loan_Number_array)

		self.Mgmt_Static_Pool_df.loc[max(self.Mgmt_Static_Pool_df.index)+1] = [new_static_pool_num,static_pool_name,orcas_user,datetime.now()]
		self.Mgmt_Static_Pool_df.to_pickle(Config.Mgmt_Static_Pool_File)
		self.Mgmt_Static_Pool_treeview.update_dataframe(self.Mgmt_Static_Pool_df)

		self.update_unlevered_economics_static_pool_optionmenu()

	def StaticPoolPage_design(self):

		# self.temp_db_df = pd.DataFrame()
		self.live_static_pool_df = pd.DataFrame()

		self.StaticPoolPage_Frame = Tkinter.Frame(self.grand_left_frame)
		self.StaticPoolPage_Frame.pack(expand=1, fill="both")
		

		def deleteStaticPool():
			for selected in self.Mgmt_Static_Pool_treeview.tree.selection():
				selected_values = self.Mgmt_Static_Pool_treeview.tree.item(selected,'values')
				static_pool_num = selected_values[0]
				to_be_removed_npy = Config.Static_Pool_Folder+ str(static_pool_num) + ".npy"
				try:
					os.remove(to_be_removed_npy)
				except:
					pass

				self.Mgmt_Static_Pool_df = self.Mgmt_Static_Pool_df[self.Mgmt_Static_Pool_df[u'资产池编号']!=int(static_pool_num)]

			self.Mgmt_Static_Pool_df.to_pickle(Config.Mgmt_Static_Pool_File)
			self.Mgmt_Static_Pool_treeview.update_dataframe(self.Mgmt_Static_Pool_df)			

			self.update_unlevered_economics_static_pool_optionmenu()

		def loadStaticPool():

			selected = self.Mgmt_Static_Pool_treeview.tree.selection()[0]
			selected_values = self.Mgmt_Static_Pool_treeview.tree.item(selected,'values')
			static_pool_num = selected_values[0]
			to_be_loaded_npy = Config.Static_Pool_Folder+ str(static_pool_num) + ".npy"
			self.live_static_pool_npy = np.load(to_be_loaded_npy)

			preloaded_npy = np.concatenate((self.live_static_pool_npy,np.array([orcas_user] * len(self.live_static_pool_npy))))
			preloaded_npy = preloaded_npy.reshape((2,len(self.live_static_pool_npy))).T

			np.savetxt(Config.BHHJ_static_temp_pool_txt,preloaded_npy,fmt = "%s",delimiter="|")
			IO_Utilities.SQL_Util.delete_temp_pool_table()
			IO_Utilities.SQL_Util.upload_temp_pool_table()

			sql_script = IO_Utilities.SQL_Util.script_generator_engine_2(table_IN = "[dbo].[BHHJ_marketplace_consumer_loan]",orcas_user_IN = orcas_user)
			self.live_static_pool_df = IO_Utilities.SQL_Util.query_sql_procedure(sql_script_IN = sql_script)[0]

			IO_Utilities.IO_Util.open_in_html(self.live_static_pool_df)

		staticpoolpage_part_1 = Tkinter.LabelFrame(self.StaticPoolPage_Frame,borderwidth = 2, width = 600, height = 60)
		staticpoolpage_part_1.pack()
		staticpoolpage_part_1.pack_propagate(False)

		staticpoolpage_line_1 = Tkinter.Frame(staticpoolpage_part_1,pady = 2)
		staticpoolpage_line_1.pack(side = "top")

		self.CreateStaticPool_Button = Tkinter.Button(staticpoolpage_line_1, text = u"建立资产池", command = self.createStaticPool,
			bg=Config.Orcas_blue,width = 12)
		self.CreateStaticPool_Button.pack(side='left')

		self.DeleteStaticPool_Button = Tkinter.Button(staticpoolpage_line_1, text = u"移除资产池", command = deleteStaticPool,width = 12)
		self.DeleteStaticPool_Button.pack(side='left')

		self.LoadStaticPool_Button = Tkinter.Button(staticpoolpage_line_1, text = u"载入资产池", command = loadStaticPool,width = 12)
		self.LoadStaticPool_Button.pack(side='left')

		staticpoolpage_line_2 = Tkinter.Frame(staticpoolpage_part_1)
		staticpoolpage_line_2.pack(side = "top")

		databasetable_optionmenu_label = Tkinter.Label(staticpoolpage_line_2,text = "请选择数据库表格类型")
		databasetable_optionmenu_label.pack(side = 'left')

		self.databasetable_strVar = Tkinter.StringVar()
		self.databasetable_option = ttk.Combobox(staticpoolpage_line_2, textvariable=self.databasetable_strVar, values=Config.production_table_list)

		self.databasetable_strVar.set(Config.production_table_list[0])
		self.databasetable_option.pack(side = 'left')

		staticpoolpage_part_2 = Tkinter.LabelFrame(self.StaticPoolPage_Frame, borderwidth = 0, width = 600, height = 30)
		staticpoolpage_part_2.pack()
		staticpoolpage_part_2.pack_propagate(False)

		staticpoolpage_line_3 = Tkinter.Frame(staticpoolpage_part_2)
		staticpoolpage_line_3.pack(side = "top")

		self.StaticPoolName_TextBox = Tkinter.Entry(staticpoolpage_line_3, width=60,bg=Config.Orcas_blue)
		self.StaticPoolName_TextBox.insert(0,u"请输入资产池名称")
		self.StaticPoolName_TextBox.pack(side = 'top')

		staticpoolpage_part_3 = Tkinter.LabelFrame(self.StaticPoolPage_Frame,borderwidth = 2, width = 600, height = 100)
		staticpoolpage_part_3.pack()
		staticpoolpage_part_3.pack_propagate(False)

		staticpoolpage_line_4 = Tkinter.Frame(staticpoolpage_part_3)
		staticpoolpage_line_4.pack(side = "top")

		databasetable_optionmenu_label = Tkinter.Label(staticpoolpage_line_4,text = "请放入静态池全部贷款编号(或选)")
		databasetable_optionmenu_label.pack(side = 'top')

		self.StaticPool_text = Tkinter.Text(staticpoolpage_line_4,width = 60,height = 5)
		self.StaticPool_text.pack(side = 'top')

		staticpoolpage_part_4 = Tkinter.LabelFrame(self.StaticPoolPage_Frame,borderwidth = 2, width = 600, height = 100)
		staticpoolpage_part_4.pack()

		self.StaticPoolCondition_Instance = GUI_Utilities.ConditionGroup_Mgmt(staticpoolpage_part_4,
			title_list_IN = [u"逻辑",u"表头",u"运算符",u"参数",u"数据类型"])
		self.StaticPoolCondition_Instance.pack()

		staticpoolpage_part_5 = Tkinter.LabelFrame(self.StaticPoolPage_Frame,borderwidth = 2, width = 600, height = 300)
		staticpoolpage_part_5.pack()
		staticpoolpage_part_5.pack_propagate(False)

		static_pool_mgmt_label = Tkinter.Label(staticpoolpage_part_5,text = u"********************* 静态资产池列表 *********************",bg='yellow')
		static_pool_mgmt_label.pack(side = 'top',pady = 10)
		self.Mgmt_Static_Pool_treeview = GUI_Utilities.Treeview_Mgmt(master = staticpoolpage_part_5, df_IN = self.Mgmt_Static_Pool_df)


	def runUnleveredEconomics(self):

		# Load Pool
		static_pool_selected = self.Static_Pool_strVar.get()
		static_pool_selected_parsed = static_pool_selected.split(" - ")[0]
		to_be_loaded_npy = Config.Static_Pool_Folder+ str(static_pool_selected_parsed) + ".npy"
		self.live_static_pool_npy = np.load(to_be_loaded_npy)
		preloaded_npy = np.concatenate((self.live_static_pool_npy,np.array([orcas_user] * len(self.live_static_pool_npy))))
		preloaded_npy = preloaded_npy.reshape((2,len(self.live_static_pool_npy))).T
		np.savetxt(Config.BHHJ_static_temp_pool_txt,preloaded_npy,fmt = "%s",delimiter="|")
		IO_Utilities.SQL_Util.delete_temp_pool_table()
		IO_Utilities.SQL_Util.upload_temp_pool_table()
		sql_script = IO_Utilities.SQL_Util.script_generator_engine_2(table_IN = "[dbo].[BHHJ_marketplace_consumer_loan]",orcas_user_IN = orcas_user)
		self.live_static_pool_df = IO_Utilities.SQL_Util.query_sql_procedure(sql_script_IN = sql_script)[0]

		# Credit Model
		self.live_credit_model_specs = self.live_credit_model_gui.get()

		if self.live_credit_model == 'CPR/CDR':
			pass
		if self.live_credit_model == 'SMM/MDR':
			smm_intex = self.live_credit_model_specs["SMM"]
			mdr_intex = self.live_credit_model_specs["MDR"]
			sev_level = float(self.live_credit_model_specs["SEV"])/100.0
			recovery_lag = int(self.live_credit_model_specs["RecoveryLag"])

			credit_model_instance = vallina_smm_mdr.vallina_smm_mdr(self.live_static_pool_df,smm_IN = smm_intex, mdr_IN = mdr_intex)

		if self.live_credit_model == 'CTC CASHLOAN(5m10m BASE)':
			# add other variables
			self.live_static_pool_df.loc[:,'feeratio'] = self.live_static_pool_df.loc[:,'service_fee']/self.live_static_pool_df.loc[:,'original_balance'] * 1.0

			# use CTC CASHLOAN(5m10m BASE) credit model
			sev_level = float(self.live_credit_model_specs["SEV"])/100.0
			recovery_lag = int(self.live_credit_model_specs["RecoveryLag"])
			smm_multi = float(self.live_credit_model_specs["SMM Multi"])
			mdr_multi = float(self.live_credit_model_specs["MDR Multi"])

			credit_model_instance = chinatopcredit_cashloan_5m10m.chinatopcredit_cashloan_5m10m(self.live_static_pool_df,smm_multi_IN = smm_multi, mdr_multi_IN = mdr_multi)

		credit_model_instance.run_prepay_default()
		# Credit Model Finished

		# Cashflow Engine
		if self.live_credit_model == 'CPR/CDR':
			pass
		if self.live_credit_model == 'SMM/MDR':
			# cashflow_engine_instance = generic_cashloan_mode.generic_cashloan_mode(credit_model_instance.static_pool, credit_model_instance.smm_matrix,credit_model_instance.mdr_matrix,sev_level,recovery_lag)
			cashflow_engine_instance = cashloan_ctc_mode.cashloan_ctc_mode(credit_model_instance.static_pool, credit_model_instance.smm_matrix,credit_model_instance.mdr_matrix,sev_level,recovery_lag)
		if self.live_credit_model == 'CTC CASHLOAN(5m10m BASE)':
			cashflow_engine_instance = cashloan_ctc_mode.cashloan_ctc_mode(credit_model_instance.static_pool, credit_model_instance.smm_matrix,credit_model_instance.mdr_matrix,sev_level,recovery_lag)

		cashflow_engine_instance.run_cashflow()

		# Cashflow Engine Finished
		new_unlevered_economics_run_num = max(self.Mgmt_Unlevered_Economics_df[u'资产池分析实例编号']) + 1
		
		output = open(Config.Unlevered_Economics_Run_Folder + str(new_unlevered_economics_run_num) + '.ll.pkl', 'wb')
		pickle.dump(cashflow_engine_instance.cashflow, output)
		output.close()
		

		self.Mgmt_Unlevered_Economics_df.loc[max(self.Mgmt_Unlevered_Economics_df.index)+1] = [new_unlevered_economics_run_num,self.newUnleveredEconomics_entry.get(),'chinatopcredit_cashloan_5m10m','cashloan_ctc_mode',static_pool_selected,orcas_user,datetime.now()]
		self.Mgmt_Unlevered_Economics_df.to_pickle(Config.Mgmt_Unlevered_Economics_Run_File)
		self.Mgmt_Unlevered_Economics_Run_treeview.update_dataframe(self.Mgmt_Unlevered_Economics_df)



	def loadUnleveredEconomics_ll(self,unlevered_run_num):
		self.live_ll_unlevered_economics_cfs = []
		if unlevered_run_num is None:
			selected_runs = self.Mgmt_Unlevered_Economics_Run_treeview.tree.selection()
			for selected_run in selected_runs:
				selected = selected_run
				selected_values = self.Mgmt_Unlevered_Economics_Run_treeview.tree.item(selected,'values')
				unlevered_economics_run_num = selected_values[0]
				to_be_loaded_pkl = Config.Unlevered_Economics_Run_Folder+ str(unlevered_economics_run_num) + ".ll.pkl"
				ll_pkl_file = open(to_be_loaded_pkl, 'rb')
				ll_cashflow_pkl = pickle.load(ll_pkl_file)
				ll_pkl_file.close()
				self.live_ll_unlevered_economics_cfs.append(ll_cashflow_pkl)
		else:
			to_be_loaded_pkl = Config.Unlevered_Economics_Run_Folder+ str(unlevered_run_num) + ".ll.pkl"
			ll_pkl_file = open(to_be_loaded_pkl, 'rb')
			ll_cashflow_pkl = pickle.load(ll_pkl_file)
			ll_pkl_file.close()
			self.live_ll_unlevered_economics_cfs.append(ll_cashflow_pkl)

	def pushCashflowToDB(self,unlevered_run_num = None):
		self.loadUnleveredEconomics_ll(unlevered_run_num)
		for live_ll_unlevered_economics_cf_dict in self.live_ll_unlevered_economics_cfs:
			rand_bhhj_loan_number =  live_ll_unlevered_economics_cf_dict.keys()[0]
			df_col = list(live_ll_unlevered_economics_cf_dict[rand_bhhj_loan_number].columns.values)
			df_col.insert(0,'BHHJ_Loan_Number')
			df_col.append('PUSH_TIME')

			combined_cf_df = pd.DataFrame(columns = df_col)

			for bhhj_loan_number,cf_df in live_ll_unlevered_economics_cf_dict.items():
				cf_df['BHHJ_Loan_Number'] = bhhj_loan_number
				cf_df['PUSH_TIME'] = datetime.now()
				cf_df = cf_df[df_col]
				if len(combined_cf_df) == 0:
					combined_cf_df = cf_df
				else:
					combined_cf_df = combined_cf_df.append(cf_df,ignore_index = True)

			combined_cf_df.to_csv(Config.BHHJ_Forecast_temp_txt,sep = "|",index = False)
			IO_Utilities.SQL_Util.upload_bhhj_forecast_cf()


	def UnleveredEconomicsPage_design(self):
		self.cashflow_aggregator_instances = []
		self.live_agg_unlevered_economics_run_aggregation_cfs = []
		self.live_unlevered_economics_run_analytics_builders = []
		self.live_unlevered_economics_run_analytics_table_results = []
		self.live_unlevered_economics_run_analytics_chart_results = []
		self.live_unlevered_economics_run_number_placeholder = []

		self.UnleveredEconomicsPage_Frame = Tkinter.Frame(self.grand_left_frame)
		self.UnleveredEconomicsPage_Frame.pack(expand=1, fill="both")

		unleveredeconomics_line_1 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_1.pack(expand = 1, fill = "both",side = 'top')

		unleveredeconomics_line_1_left = Tkinter.Frame(unleveredeconomics_line_1)
		unleveredeconomics_line_1_left.pack(expand = 1, fill = "both",side = 'left')

		unleveredeconomics_line_1_left_1 = Tkinter.Frame(unleveredeconomics_line_1_left)
		unleveredeconomics_line_1_left_1.pack(expand = 1, fill = "both",side = 'top')

		creditmodel_optionmenu_label = Tkinter.Label(unleveredeconomics_line_1_left_1,text = "选择信用模型",width = 12,anchor = 'nw')
		creditmodel_optionmenu_label.pack(side = 'left')

		self.live_credit_model_gui = None

		def showUnleveredEconomicsStats(events = None):
			self.live_unlevered_economics_run_analytics_builders = []
			self.live_unlevered_economics_run_analytics_table_results =  []
			self.live_unlevered_economics_run_analytics_chart_results = []
			self.static_pool_px = float(self.Static_Pool_px_TextBox.get())

			run_stats_display_df= pd.DataFrame()
			run_charts_display_dict = {}

			for idx,unlevered_economics_run_number in enumerate(self.live_unlevered_economics_run_number_placeholder):
				live_agg_unlevered_economics_run_aggregation_cf = self.live_agg_unlevered_economics_run_aggregation_cfs[idx]

				unlevered_economics_run_yield = Calc_Utilities.StandardBond_Util.irr_calc(np.array(live_agg_unlevered_economics_run_aggregation_cf['fundings']), np.array(live_agg_unlevered_economics_run_aggregation_cf['total_cf']), frequency_IN = 12, px = self.static_pool_px)

				live_unlevered_economics_run_analytics_builder = Calc_Utilities.AggAsset_Analytics(bondDF_IN = live_agg_unlevered_economics_run_aggregation_cf, annualyield_IN = unlevered_economics_run_yield, frequency_IN = 12,px_IN = self.static_pool_px)

				live_unlevered_economics_run_analytics_table_res = live_unlevered_economics_run_analytics_builder.build_analytics_table()
				live_unlevered_economics_run_analytics_chart_res = live_unlevered_economics_run_analytics_builder.build_analytics_charts()

				run_stats_display_df_temp = pd.DataFrame(live_unlevered_economics_run_analytics_table_res,index = ["Run - " + str(unlevered_economics_run_number)]).transpose()
				run_stats_display_df_temp = run_stats_display_df_temp.reindex(index = live_unlevered_economics_run_analytics_builder.rank_mappings)
				run_charts_display_dict[self.Mgmt_Unlevered_Economics_df.loc[self.Mgmt_Unlevered_Economics_df[u'资产池分析实例编号'] == int(unlevered_economics_run_number)][u'资产池分析实例名称'].values[0]] = live_unlevered_economics_run_analytics_chart_res

				self.live_unlevered_economics_run_analytics_builders.append(live_unlevered_economics_run_analytics_builder)
				self.live_unlevered_economics_run_analytics_table_results.append(live_unlevered_economics_run_analytics_table_res)
				self.live_unlevered_economics_run_analytics_chart_results.append(live_unlevered_economics_run_analytics_chart_res)

				if len(run_stats_display_df) == 0:
					run_stats_display_df = run_stats_display_df_temp
				else:
					run_stats_display_df = pd.merge(run_stats_display_df, run_stats_display_df_temp, left_index=True, right_index=True)

			self.grand_right_upper_frame.destroy()
			self.grand_right_lower_frame.destroy()

			self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)
			self.grand_right_lower_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)

			self.grand_right_upper_frame.pack(side = 'top')
			self.grand_right_lower_frame.pack(side = 'top')

			# Display the curves charts
			GUI_Utilities.Display_Charts_Mgmt_OrcasFormat(master = self.grand_right_upper_frame,datadict_IN = run_charts_display_dict, keys_IN = ['smm_curve','mdr_curve','severity_curve','cum_loss_curve'])

			# Display the stats table
			GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_lower_frame,df_IN = run_stats_display_df,formatting_mapper_IN = self.live_unlevered_economics_run_analytics_builders[0].formatting_mappings)


		def credit_model_gui_pop(events = None):
			value = self.creditmodel_option.get()
			self.live_credit_model  = value
			if self.live_credit_model_gui is not None: self.live_credit_model_gui.pack_forget()
				
			if value == 'CPR/CDR':
				self.live_credit_model_gui = Credit_GUI_Model.CPR_CDR_Model(self.unleveredeconomics_line_1_right)
			if value == 'SMM/MDR':
				self.live_credit_model_gui = Credit_GUI_Model.SMM_MDR_Model(self.unleveredeconomics_line_1_right)
			if value == 'CTC CASHLOAN(5m10m BASE)':
				self.live_credit_model_gui = Credit_GUI_Model.CTC_5m10m_Model(self.unleveredeconomics_line_1_right)
				

		self.creditmodel_strVar = Tkinter.StringVar()
		self.creditmodel_option = ttk.Combobox(unleveredeconomics_line_1_left_1,textvariable = self.creditmodel_strVar, values = Config.creditmodel_list)
		self.creditmodel_option.bind("<<ComboboxSelected>>", credit_model_gui_pop)
		self.creditmodel_strVar.set(Config.creditmodel_list[0])


		self.creditmodel_option.pack(side = 'top',anchor = 'w')

		self.unleveredeconomics_line_1_right = Tkinter.Frame(unleveredeconomics_line_1)
		self.unleveredeconomics_line_1_right.pack(expand = 1, fill = "both",side = 'left')
		credit_model_gui_pop()

		unleveredeconomics_line_2 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_2.pack(expand = 1, fill = "both",side = 'top')

		unleveredeconomics_line_3 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_3.pack(expand = 1, fill = "both",side = 'top')

		unleveredeconomics_line_1_left_2 = Tkinter.Frame(unleveredeconomics_line_1_left)
		unleveredeconomics_line_1_left_2.pack(expand = 1, fill = "both",side = 'top')

		unleveredeconomics_line_1_left_3 = Tkinter.Frame(unleveredeconomics_line_1_left)
		unleveredeconomics_line_1_left_3.pack(expand = 1, fill = "both",side = 'top')


		static_pool_optionmenu_label = Tkinter.Label(unleveredeconomics_line_1_left_2,text = "选择资产池",width = 12,anchor = 'nw')
		static_pool_optionmenu_label.pack(side = 'left',anchor = 'w')

		self.Static_Pool_strVar = Tkinter.StringVar()
		self.Static_Pool_option = ttk.Combobox(unleveredeconomics_line_1_left_2,textvariable = self.Static_Pool_strVar, values = self.Mgmt_Static_Pool_list)
		self.Static_Pool_strVar.set(self.Mgmt_Static_Pool_list[0])

		self.Static_Pool_option.pack(side = 'left',anchor = 'w')

		Static_Pool_px_label = Tkinter.Label(unleveredeconomics_line_1_left_3,text = "资产池价格",width = 12,anchor = 'nw')
		Static_Pool_px_label.pack(side = 'left',anchor = 'w')


		self.Static_Pool_px_TextBox = Tkinter.Entry(unleveredeconomics_line_1_left_3, width=10)
		self.Static_Pool_px_TextBox.bind("<Return>", showUnleveredEconomicsStats)
		self.Static_Pool_px_TextBox.insert(0,100)
		self.Static_Pool_px_TextBox.pack(side = 'left',anchor = 'w')

		unleveredeconomics_line_3 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_3.pack(expand = 1, fill = "both",side = 'top')

		unlevered_economics_run_mgmt_label = Tkinter.Label(unleveredeconomics_line_3,text = "**************************** 资产池分析(不含融资)列表 ****************************",bg = 'yellow')
		unlevered_economics_run_mgmt_label.pack(side = 'top')
		self.Mgmt_Unlevered_Economics_Run_treeview = GUI_Utilities.Treeview_Mgmt(master = unleveredeconomics_line_3, df_IN = self.Mgmt_Unlevered_Economics_df)

		unleveredeconomics_line_4 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_4.pack(expand = 1, fill = "both",side = 'top')

		

		self.load_subpool_indicator = Tkinter.IntVar()
		self.load_subpool_checkbutton = Tkinter.Checkbutton(unleveredeconomics_line_4, text=u"载入资产子池", variable=self.load_subpool_indicator)
		self.load_subpool_checkbutton.pack(side = 'top')

		self.unleveredeconomics_subpool_text = Tkinter.Text(unleveredeconomics_line_4,width = 70,height = 5)
		self.unleveredeconomics_subpool_text.pack(side = 'top')
	
		unleveredeconomics_line_5 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_5.pack(expand = 1, fill = "both",side = 'top')

		unleveredeconomics_line_6 = Tkinter.Frame(self.UnleveredEconomicsPage_Frame)
		unleveredeconomics_line_6.pack(expand = 1, fill = "both",side = 'top')

		self.runUnleveredEconomics_Button = Tkinter.Button(unleveredeconomics_line_5, text = u"新创现金流分析(不含融资)", command = self.runUnleveredEconomics,bg = Config.Orcas_blue)
		self.runUnleveredEconomics_Button.pack(side = 'left',fill = 'x',expand='yes')

		newUnleveredEconomics_label = Tkinter.Label(unleveredeconomics_line_5,text = u"资产池分析实例名称")
		newUnleveredEconomics_label.pack(side = 'left',fill = 'x',expand='yes')

		self.newUnleveredEconomics_entry = Tkinter.Entry(unleveredeconomics_line_5,width = 30,bg = Config.Orcas_blue)
		self.newUnleveredEconomics_entry.pack(side = 'left',fill = 'x',expand='yes')

		def deleteUnleveredEconomics():
			for selected in self.Mgmt_Unlevered_Economics_Run_treeview.tree.selection():
				selected_values = self.Mgmt_Unlevered_Economics_Run_treeview.tree.item(selected,'values')
				unlevered_economics_run_num = selected_values[0]
				to_be_removed_pkl = Config.Unlevered_Economics_Run_Folder+ str(unlevered_economics_run_num) + ".ll.pkl"
				to_be_removed_agg_pkl = Config.Unlevered_Economics_Run_Folder+ str(unlevered_economics_run_num) + ".aggregation.pkl"
				to_be_removed_agg_instance_pkl  = Config.Unlevered_Economics_Run_Folder+ str(unlevered_economics_run_num) + ".agg_instance.pkl"

				try:
					os.remove(to_be_removed_pkl)
				except:
					pass

				try:
					os.remove(to_be_removed_agg_pkl)
				except:
					pass	

				try:
					os.remove(to_be_removed_agg_instance_pkl)
				except:
					pass

				self.Mgmt_Unlevered_Economics_df = self.Mgmt_Unlevered_Economics_df[self.Mgmt_Unlevered_Economics_df[u'资产池分析实例编号']!=int(unlevered_economics_run_num)]

			self.Mgmt_Unlevered_Economics_df.to_pickle(Config.Mgmt_Unlevered_Economics_Run_File)
			self.Mgmt_Unlevered_Economics_Run_treeview.update_dataframe(self.Mgmt_Unlevered_Economics_df)

		self.deleteUnleveredEconomics_Button = Tkinter.Button(unleveredeconomics_line_6, text = u"删除资产池分析实例", command = deleteUnleveredEconomics)
		self.deleteUnleveredEconomics_Button.pack(side = 'left',expand = 'yes',fill = 'x')



		def loadUnleveredEconomics(events = None):
			self.cashflow_aggregator_instances = []
			self.live_agg_unlevered_economics_run_aggregation_cfs = []
			self.live_unlevered_economics_run_analytics_builders = []
			self.live_unlevered_economics_run_analytics_table_results = []
			self.live_unlevered_economics_run_analytics_chart_results = []
			self.live_unlevered_economics_run_number_placeholder = []
			self.static_pool_px = float(self.Static_Pool_px_TextBox.get())


			run_stats_display_df= pd.DataFrame()
			run_charts_display_dict = {}

			selected_runs = self.Mgmt_Unlevered_Economics_Run_treeview.tree.selection()
			if len(selected_runs) == 1:
				if self.load_subpool_indicator.get():
					self.subpool_BHHJ_loan_number_list = self.unleveredeconomics_subpool_text.get("1.0","end-1c")
					self.subpool_BHHJ_loan_number_list = self.subpool_BHHJ_loan_number_list.split('\n')
					self.subpool_BHHJ_loan_number_list = [item for item in self.subpool_BHHJ_loan_number_list if len(item)>0]
					saved_agg = False
				else:
					self.subpool_BHHJ_loan_number_list = []
					saved_agg = True
			
			else: # if multiple runs are selected, ignore the subpool indicator
				self.subpool_BHHJ_loan_number_list = []
				saved_agg = True

			# Calc/Load Agg cashflow file
			for selected_run in selected_runs:
				selected = selected_run
				selected_values = self.Mgmt_Unlevered_Economics_Run_treeview.tree.item(selected,'values')
				unlevered_economics_run_num = selected_values[0]
				to_be_loaded_pkl = Config.Unlevered_Economics_Run_Folder+ str(unlevered_economics_run_num) + ".ll.pkl"
				to_be_saved_pkl = Config.Unlevered_Economics_Run_Folder + str(unlevered_economics_run_num) + '.aggregation.pkl'
				to_be_saved_agg_instance_pkl = Config.Unlevered_Economics_Run_Folder + str(unlevered_economics_run_num) + '.agg_instance.pkl'

				if os.path.exists(to_be_saved_pkl) and not(self.load_subpool_indicator.get()):
					live_agg_unlevered_economics_run_aggregation_cf = pd.read_pickle(to_be_saved_pkl)
					with file(to_be_saved_agg_instance_pkl, 'rb') as f: cashflow_aggregator_instance = pickle.load(f)

				else:
					ll_pkl_file = open(to_be_loaded_pkl, 'rb')
					ll_cashflow_pkl = pickle.load(ll_pkl_file)
					ll_pkl_file.close()

					if not(saved_agg):
						ll_cashflow_pkl = { bhhj_loan_number: ll_cashflow_pkl[bhhj_loan_number] for bhhj_loan_number in self.subpool_BHHJ_loan_number_list if bhhj_loan_number in ll_cashflow_pkl.keys()}

					cashflow_aggregator_instance = cashloan_ctc_mode.aggregator(ll_cashflow_pkl)
					cashflow_aggregator_instance.aggregate_cf()
					live_agg_unlevered_economics_run_aggregation_cf = cashflow_aggregator_instance.aggregate_cashflow
					
					if saved_agg:
						output = open(Config.Unlevered_Economics_Run_Folder + str(unlevered_economics_run_num) + '.aggregation.pkl', 'wb')
						pickle.dump(live_agg_unlevered_economics_run_aggregation_cf, output)
						output.close()

						output = open(Config.Unlevered_Economics_Run_Folder + str(unlevered_economics_run_num) + '.agg_instance.pkl', 'wb')
						pickle.dump(cashflow_aggregator_instance, output)
						output.close()

				live_agg_unlevered_economics_run_aggregation_cf.loc[:,'fundings'] = 0
				live_agg_unlevered_economics_run_aggregation_cf.loc[0,'fundings'] = live_agg_unlevered_economics_run_aggregation_cf.loc[0,'eop_bal']

				live_agg_unlevered_economics_run_aggregation_cf = live_agg_unlevered_economics_run_aggregation_cf.rename(columns = {
																																	'fundings':'fundings',
																																	'total_cf':'total_cf',
																																	'prin_cf':'prin_cf',
																																	'int_cf':'int_cf',
																																	'default':'default',
																																	'loss':'loss',
																																	'schedule_prin':'schedule_prin',
																																	'expected_recovery':'expected_recovery',
																																	'bop_bal':'bop_bal',
																																	'prepay':'prepay'
																																	})
				# bond stats calculation

				unlevered_economics_run_yield = Calc_Utilities.StandardBond_Util.irr_calc(np.array(live_agg_unlevered_economics_run_aggregation_cf['fundings']), np.array(live_agg_unlevered_economics_run_aggregation_cf['total_cf']), frequency_IN = 12, px = self.static_pool_px)

				live_unlevered_economics_run_analytics_builder = Calc_Utilities.AggAsset_Analytics(bondDF_IN = live_agg_unlevered_economics_run_aggregation_cf, annualyield_IN = unlevered_economics_run_yield, frequency_IN = 12,px_IN = self.static_pool_px)

				live_unlevered_economics_run_analytics_table_res = live_unlevered_economics_run_analytics_builder.build_analytics_table()
				live_unlevered_economics_run_analytics_chart_res = live_unlevered_economics_run_analytics_builder.build_analytics_charts()

				run_stats_display_df_temp = pd.DataFrame(live_unlevered_economics_run_analytics_table_res,index = ["Run - " + unlevered_economics_run_num]).transpose()
				run_stats_display_df_temp = run_stats_display_df_temp.reindex(index = live_unlevered_economics_run_analytics_builder.rank_mappings)
				run_charts_display_dict[self.Mgmt_Unlevered_Economics_df.loc[self.Mgmt_Unlevered_Economics_df[u'资产池分析实例编号'] == int(unlevered_economics_run_num)][u'资产池分析实例名称'].values[0]] = live_unlevered_economics_run_analytics_chart_res

				self.cashflow_aggregator_instances.append(cashflow_aggregator_instance)
				self.live_agg_unlevered_economics_run_aggregation_cfs.append(live_agg_unlevered_economics_run_aggregation_cf)
				self.live_unlevered_economics_run_analytics_builders.append(live_unlevered_economics_run_analytics_builder)
				self.live_unlevered_economics_run_analytics_table_results.append(live_unlevered_economics_run_analytics_table_res)
				self.live_unlevered_economics_run_analytics_chart_results.append(live_unlevered_economics_run_analytics_chart_res)
				self.live_unlevered_economics_run_number_placeholder.append(int(unlevered_economics_run_num))

				if len(run_stats_display_df) == 0:
					run_stats_display_df = run_stats_display_df_temp
				else:
					run_stats_display_df = pd.merge(run_stats_display_df, run_stats_display_df_temp, left_index=True, right_index=True)

			if events != None:
				self.grand_right_upper_frame.destroy()
				self.grand_right_lower_frame.destroy()

				self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)
				self.grand_right_lower_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)

				self.grand_right_upper_frame.pack(side = 'top')
				self.grand_right_lower_frame.pack(side = 'top')

				# Display the curves charts
				GUI_Utilities.Display_Charts_Mgmt_OrcasFormat(master = self.grand_right_upper_frame,datadict_IN = run_charts_display_dict, keys_IN = ['smm_curve','mdr_curve','severity_curve','cum_loss_curve'])

				# Display the stats table
				GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_lower_frame,df_IN = run_stats_display_df,formatting_mapper_IN = self.live_unlevered_economics_run_analytics_builders[0].formatting_mappings)

			# Update Dashboard #
			to_be_print = '已载入现金流分析实例 : '
			for live_unlevered_economics_run_number in self.live_unlevered_economics_run_number_placeholder:
				 to_be_print = to_be_print + str(live_unlevered_economics_run_number) + " | "

			self.dashboard_label['text'] = to_be_print


		self.loadUnleveredEconomics_Button = Tkinter.Button(unleveredeconomics_line_6, text = "载入资产池分析实例", command = loadUnleveredEconomics)
		self.loadUnleveredEconomics_Button.pack(side = 'left',fill = 'x', expand = 'yes')

		self.loadUnleveredEconomics_Button.bind("<Button-3>", loadUnleveredEconomics)

		def displayCashflow():
			if len(self.live_agg_unlevered_economics_run_aggregation_cfs) == 0:
				loadUnleveredEconomics()
			else:
				self.grand_right_upper_frame.destroy()
				self.grand_right_lower_frame.destroy()

				self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=200)
				self.grand_right_upper_frame.pack(side = 'top')

				GUI_Utilities.Display_Unlevered_Econ_Cashflow_Mgmt(master = self.grand_right_upper_frame, run_num_list_IN = self.live_unlevered_economics_run_number_placeholder, cashflow_df_list_IN = self.live_agg_unlevered_economics_run_aggregation_cfs)


		self.showUnleveredEconomics_Button = Tkinter.Button(unleveredeconomics_line_6, text = "资产池分析结果", command = showUnleveredEconomicsStats)
		self.showUnleveredEconomics_Button.pack(side = 'left',fill = 'x', expand = 'yes')

		self.displayCashflow_Button = Tkinter.Button(unleveredeconomics_line_6, text = u"展示详细现金流", command = displayCashflow)
		self.displayCashflow_Button.pack(side = 'left',expand = 'yes',fill = 'x')

		self.pushCashflowToDB_Button = Tkinter.Button(unleveredeconomics_line_6, text = u"上传详细现金流", command = self.pushCashflowToDB)
		self.pushCashflowToDB_Button.pack(side = 'left',expand = 'yes',fill = 'x')

	def StratsPage_design(self):
		self.StratsPage_Frame = Tkinter.Frame(self.grand_left_frame)
		self.StratsPage_Frame.pack(expand=1, fill="both")

		self.StratsPage_Upper_Frame = Tkinter.LabelFrame(self.StratsPage_Frame,width = 600,height = 150,borderwidth = 2)
		self.StratsPage_Upper_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.StratsPage_Upper_Frame.pack_propagate(False)

		self.StratsPage_Middle_Frame = Tkinter.LabelFrame(self.StratsPage_Frame,width = 600,height = 400,borderwidth = 2)
		self.StratsPage_Middle_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.StratsPage_Middle_Frame.pack_propagate(False)

		self.StratsPage_Lower_Frame = Tkinter.Frame(self.StratsPage_Frame)
		self.StratsPage_Lower_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')

		self.stratspage_left_frame = Tkinter.LabelFrame(self.StratsPage_Middle_Frame,width = 300,height = 550,borderwidth = 2)
		self.stratspage_left_frame.pack(side = 'left',anchor = 'n')
		self.stratspage_left_frame.pack_propagate(False)

		self.stratspage_right_frame = Tkinter.LabelFrame(self.StratsPage_Middle_Frame,width = 300,height = 550,borderwidth = 2)
		self.stratspage_right_frame.pack(side = 'left',anchor = 'n')
		self.stratspage_right_frame.pack_propagate(False)

		self.stratspage_left_line_2_frame = Tkinter.Frame(self.StratsPage_Upper_Frame)
		self.stratspage_left_line_2_frame.pack(side = 'top')
		self.strats_gui_mgmt = Strats_Interface.Strats_settings(self.stratspage_left_line_2_frame)

		self.stratspage_right_line_1_frame = Tkinter.Frame(self.stratspage_left_frame)
		self.stratspage_right_line_1_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.stratspage_right_line_1_canvas = Tkinter.Canvas(self.stratspage_right_line_1_frame, width=800, height=500, bg="white")
		self.stratspage_right_line_1_new_frame = Tkinter.Frame(self.stratspage_right_line_1_canvas)

		ysb = ttk.Scrollbar(self.stratspage_right_line_1_frame,orient='vertical', command= self.stratspage_right_line_1_canvas.yview)
		self.stratspage_right_line_1_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.stratspage_right_line_1_frame, orient='horizontal', command= self.stratspage_right_line_1_canvas.xview)
		self.stratspage_right_line_1_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.stratspage_right_line_1_canvas.pack(side = 'left')
		self.stratspage_right_line_1_canvas.create_window((0,1), window=self.stratspage_right_line_1_new_frame, anchor="nw")

		def reconfigure_scrollregion1(event):
			self.stratspage_right_line_1_canvas.configure(scrollregion=self.stratspage_right_line_1_canvas.bbox("all"))

		self.stratspage_right_line_1_new_frame.bind("<Configure>",reconfigure_scrollregion1)

		self.strats_dimension_settings = GUI_Utilities.ConditionGroup_Mgmt(self.stratspage_right_line_1_new_frame,title_list_IN=Config.dimension_settings_columns_gui,BoxGroup_width_IN = 9,Label_width_IN = 11,add_condition_button_text_IN = u'添加维度',delete_condition_button_text_IN = u'删除维度',style_IN = 'ComboBox')

		self.stratspage_right_line_2_frame = Tkinter.Frame(self.stratspage_right_frame)
		self.stratspage_right_line_2_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.stratspage_right_line_2_canvas = Tkinter.Canvas(self.stratspage_right_line_2_frame, width=800, height=500, bg="white")
		self.stratspage_right_line_2_new_frame = Tkinter.Frame(self.stratspage_right_line_2_canvas)

		ysb = ttk.Scrollbar(self.stratspage_right_line_2_frame,orient='vertical', command= self.stratspage_right_line_2_canvas.yview)
		self.stratspage_right_line_2_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.stratspage_right_line_2_frame, orient='horizontal', command= self.stratspage_right_line_2_canvas.xview)
		self.stratspage_right_line_2_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.stratspage_right_line_2_canvas.pack(side = 'left')
		self.stratspage_right_line_2_canvas.create_window((0,1), window=self.stratspage_right_line_2_new_frame, anchor="nw")

		def reconfigure_scrollregion2(event):
			self.stratspage_right_line_2_canvas.configure(scrollregion=self.stratspage_right_line_2_canvas.bbox("all"))
		self.stratspage_right_line_2_new_frame.bind("<Configure>",reconfigure_scrollregion2)

		self.strats_measures_settings = GUI_Utilities.ConditionGroup_Mgmt(self.stratspage_right_line_2_new_frame,
			title_list_IN=Config.measures_settings_columns_gui,BoxGroup_width_IN = 6,Label_width_IN = 8, add_condition_button_text_IN = u'添加度量',
			delete_condition_button_text_IN = u'删除度量',style_IN = 'ComboBox')


		def run_rtd(events = None):
			temp_rtd_txt = Config.temp_rtd_txt
			rt_txt = self.strats_gui_mgmt.text_Strats_RT_Dir.get("1.0","end-1c")
			df = pd.read_csv(rt_txt, sep = ',')
			RTD_Analytics_instance = RTD_Analytics(df)
			rtd_res = RTD_Analytics_instance.analytics_procedure()
			self.rtd_res = rtd_res
			IO_Utilities.IO_Util.output_to_txt(rtd_res, temp_rtd_txt)
			if events!=None:
				IO_Utilities.IO_Util.open_in_html(rtd_res)

		self.stratspage_rtd_run_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"统计描述", command = lambda : run_rtd, bg = Config.Orcas_blue)
		self.stratspage_rtd_run_button.pack(side = 'left',anchor = 'w')
		self.stratspage_rtd_run_button.bind("<Button-3>", run_rtd)


		def strats_columns_dropdown_setup():
			run_rtd()

			sql_query = "SELECT distinct([Calc_Method_Name]) FROM [Orcas_Operation].[dbo].[Strats_Calc_Method]"
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			calcmethod_dropdown_list =  [unicode(item) for item in res_list[0]['Calc_Method_Name'].values]

			sql_query = "SELECT distinct([Rule_Idx]) FROM [Orcas_Operation].[dbo].[Strats_GroupRule_Mapping]"
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			mappingrule_dropdown_list =  [unicode(item) for item in res_list[0]['Rule_Idx'].values]

			column_dropdown_list = [unicode(item) for item in list(self.rtd_res['name'].values)]
			dimension_label_list = []

			dimesion_dropdown_list = [column_dropdown_list,mappingrule_dropdown_list,dimension_label_list]

			measure_label_list = []
			format_list = Config.format_list

			measure_dropdownlist = [column_dropdown_list,calcmethod_dropdown_list,column_dropdown_list,measure_label_list,format_list]

			self.strats_dimension_settings.reload_combo_box_values_list(dimesion_dropdown_list)
			self.strats_measures_settings.reload_combo_box_values_list(measure_dropdownlist)


		self.stratspage_pre_run_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"参数预设", command = strats_columns_dropdown_setup,
			bg = Config.Orcas_blue)
		self.stratspage_pre_run_button.pack(side = 'left',anchor = 'w')

		def run_strats(events = None):
			strats_raw_tape_dir = self.strats_gui_mgmt.text_Strats_RT_Dir.get('0.0','end-1c')
			temp_strats_folder_dir = Config.temp_strats_txt
			rawtape_df = pd.read_csv(strats_raw_tape_dir, header = "infer", sep = ',',encoding='gb2312')
			strats_display_topn = int(self.strats_gui_mgmt.text_Display_Top_N.get('0.0','end-1c'))
			strats_sort_by = int(self.strats_gui_mgmt.text_Sort_By.get('0.0','end-1c'))

			self.strats_dimension_settings.get_all(dict_type =True)
			strats_dimension_df = pd.DataFrame(self.strats_dimension_settings.res)

			strats_dimension_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in zip(Config.dimension_settings_columns_gui,Config.dimension_settings_columns_txt)])
			strats_dimension_df = strats_dimension_df.rename(columns = strats_dimension_columns)
			strats_dimension_df = strats_dimension_df[Config.dimension_settings_columns_txt]


			self.strats_measures_settings.get_all(dict_type =True)
			strats_measures_df = pd.DataFrame(self.strats_measures_settings.res)

			strats_measures_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in zip(Config.measures_settings_columns_gui,Config.measures_settings_columns_txt)])
			strats_measures_df = strats_measures_df.rename(columns = strats_measures_columns)
			strats_measures_df = strats_measures_df[Config.measures_settings_columns_txt]

			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_GroupRule_Mapping]"
			mappinggroup_rule_df = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)[0]

			mappinggroup_rule_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in zip(Config.mappingrule_settings_columns_db,Config.mappingrule_settings_columns_txt)])
			mappinggroup_rule_df = mappinggroup_rule_df.rename(columns = mappinggroup_rule_columns)
			mappinggroup_rule_df = mappinggroup_rule_df[Config.mappingrule_settings_columns_txt]

			strats_dimension_df.to_csv(Config.default_dimension_settings_file,sep = Config.delimiter,index=False)
			strats_measures_df.to_csv(Config.default_measure_settings_file,sep = Config.delimiter,index=False)
			mappinggroup_rule_df.to_csv(Config.default_rules_mapping_file,sep = Config.delimiter,index=False)

			strats_dimension_df = pd.read_csv(Config.default_dimension_settings_file, header = "infer", sep = '|',encoding='gb2312')
			strats_measures_df = pd.read_csv(Config.default_measure_settings_file, header = "infer", sep = '|',encoding='gb2312')
			mappinggroup_rule_df = pd.read_csv(Config.default_rules_mapping_file, header = "infer", sep = '|',encoding='gb2312')

			Strats_Analytics_instance = Strats_Analytics.Strats_Analytics(rawtape_df,strats_dimension_df,strats_measures_df,mappinggroup_rule_df)
			Strats_Analytics_instance.run_tape_extension_procedure()
			strats_res_intermediate = Strats_Analytics_instance.analytics_procedure()


			if not os.path.exists(temp_strats_folder_dir):		
				os.makedirs(temp_strats_folder_dir)
			else:
				shutil.rmtree(temp_strats_folder_dir)
				os.makedirs(temp_strats_folder_dir)

			for key,value in strats_res_intermediate.items():
				txt_file_name = temp_strats_folder_dir + "\\" + key + "_" + "strats" + '.txt'
				value.to_csv(txt_file_name,index = False,sep = "|",encoding = 'gb2312')

			Strats_Display.analytics_procedure(rawtape_df,
												strats_dimension_df,
												strats_measures_df,
												temp_strats_folder_dir,
												temp_strats_folder_dir,
												strats_sort_by,
												strats_display_topn)

			strats_top_fame = Tkinter.Toplevel(width = 900,height = 550)
			strats_top_fame.title("分层统计" +  " - " + str(self.strats_gui_mgmt.text_Strats_Name.get('0.0','end-1c')))
			strats_top_fame.pack_propagate(False)

			strats_top_line_1_canvas = Tkinter.Canvas(strats_top_fame, width=900, height=550, bg="white")
			strats_top_line_1_new_frame = Tkinter.Frame(strats_top_line_1_canvas)

			ysb = ttk.Scrollbar(strats_top_fame,orient='vertical', command= strats_top_line_1_canvas.yview)
			strats_top_line_1_canvas.configure(yscrollcommand=ysb.set)
			ysb.pack(side = 'right',fill = 'y')

			xsb = ttk.Scrollbar(strats_top_fame, orient='horizontal', command= strats_top_line_1_canvas.xview)
			strats_top_line_1_canvas.configure(xscrollcommand=xsb.set)
			xsb.pack(side = 'bottom',fill = 'x')

			strats_top_line_1_canvas.pack(side = 'left')
			strats_top_line_1_canvas.create_window((0,0), window=strats_top_line_1_new_frame, anchor="nw")

			def reconfigure_scrollregion1_strat(event):
				strats_top_line_1_canvas.configure(scrollregion=strats_top_line_1_canvas.bbox("all"))
			strats_top_line_1_new_frame.bind("<Configure>",reconfigure_scrollregion1_strat)


			all_keys = self.strats_dimension_settings.conditions_dict.keys()
			all_keys.sort()

			for key in all_keys:
				sl_key = self.strats_dimension_settings.conditions_dict[key][2].get(2)

				new_strat_frame = Tkinter.Frame(strats_top_line_1_new_frame)
				new_strat_frame.pack(side = 'top',fill='both',expand = 'yes', pady = 5)

				new_strat_line_1_frame = Tkinter.Frame(new_strat_frame)
				new_strat_line_1_frame.pack(side = 'top',fill='both',expand = 'yes', pady = 5)

				strats_label = Tkinter.Label(new_strat_line_1_frame, text = u"分层统计" + " - " + sl_key,bg= 'yellow')
				strats_label.pack(side = 'top')

				txt_file_name = temp_strats_folder_dir + "\\" + sl_key + "_" + "strats" + '.txt'
				res = pd.read_csv(txt_file_name, header = "infer", sep = '|', encoding = 'gb2312')
				res = res.set_index(res.columns.values[0])
				formatter = {}
				strats_columns = res.columns.values
				formatter_holder = strats_measures_df[strats_measures_df['col_name'].isin(strats_columns)][['col_name','format']]
				formatter_holder.replace(np.NaN,'',inplace = True)
				formatter = dict([(item_a,Config.format_mapping[item_b]) for item_a,item_b in zip(formatter_holder['col_name'],formatter_holder['format'])])

				new_strat_line_2_frame = Tkinter.Frame(new_strat_frame)
				new_strat_line_2_frame.pack(side = 'top', fill = 'both', expand = 'yes', pady = 5)

				GUI_Utilities.DisplayTable_Mgmt(new_strat_line_2_frame,res,formatter,horizontal_mapper = False)


				if events != None:
					IO_Utilities.IO_Util.open_in_html(res)

		self.stratspage_strats_run_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"分层统计", command = run_strats,bg = Config.Orcas_blue)
		self.stratspage_strats_run_button.pack(side = 'left',anchor = 'w')
		self.stratspage_strats_run_button.bind("<Button-3>", run_strats)

		def display_mapping_group():
			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_GroupRule_Mapping]"
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			res = res_list[0]
			IO_Utilities.IO_Util.open_in_html(res)

		self.stratspage_display_group_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"分组规则", command = display_mapping_group,
			bg = Config.Orcas_blue)
		self.stratspage_display_group_button.pack(side = 'left',anchor = 'w')

		def modify_group_rule():
			self.group_rule_main = Tkinter.Tk()
			self.group_rule_main.title("分组调整")
			self.modify_group_rule_frame = Tkinter.Frame(self.group_rule_main)
			self.modify_group_rule_frame.pack(side = 'top')

			self.modify_group_rule_canvas = Tkinter.Canvas(self.modify_group_rule_frame, width=500, height=500#, bg="white"
				)
			self.modify_group_rule_new_frame = Tkinter.Frame(self.modify_group_rule_canvas)

			# self.GroupRulePage_Frame = Tkinter.Frame(self.modify_group_rule_frame)
			# self.GroupRulePage_Frame.pack(expand=1, fill="both")


			###################################### For GroupRule ######################################

			# self.stratspage_right_line_3_frame = Tkinter.Frame(self.stratspage_right_frame)
			# self.stratspage_right_line_3_frame.pack(side = 'top', fill ='both', expand = 'yes')
			# self.stratspage_right_line_3_canvas = Tkinter.Canvas(self.stratspage_right_line_3_frame, width=800, height=500, bg="white")
			# self.stratspage_right_line_3_new_frame = Tkinter.Frame(self.stratspage_right_line_3_canvas)

			ysb = ttk.Scrollbar(self.modify_group_rule_frame,orient='vertical', command= self.modify_group_rule_canvas.yview)
			self.modify_group_rule_canvas.configure(yscrollcommand=ysb.set)
			ysb.pack(side = 'right',fill = 'y')

			xsb = ttk.Scrollbar(self.modify_group_rule_frame, orient='horizontal', command= self.modify_group_rule_canvas.xview)
			self.modify_group_rule_canvas.configure(xscrollcommand=xsb.set)
			xsb.pack(side = 'bottom',fill = 'x')

			self.modify_group_rule_canvas.pack(side = 'left')
			self.modify_group_rule_canvas.create_window((0,1), window=self.modify_group_rule_new_frame, anchor="nw")

			def reconfigure_scrollregion3(event):
				self.modify_group_rule_canvas.configure(scrollregion=self.modify_group_rule_canvas.bbox("all"))
			self.modify_group_rule_new_frame.bind("<Configure>",reconfigure_scrollregion3)

			self.strats_measures_settings = GUI_Utilities.ConditionGroup_Mgmt(self.modify_group_rule_new_frame,
				title_list_IN = Config.mappingrule_settings_columns_gui, BoxGroup_width_IN = 6, Label_width_IN = 8, add_condition_button_text_IN = u'添加分组',
				delete_condition_button_text_IN = u'删除分组', style_IN = 'ComboBox')

			self.group_rule_lower_frame = Tkinter.Frame(self.group_rule_main)
			self.group_rule_lower_frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
			self.group_rule_quit_button = Tkinter.Button(self.group_rule_lower_frame, text = "关闭", command = self.group_rule_main.destroy)
        	# self.group_rule_quit_button.pack(side = 'bottom')


		self.modify_group_rule_button = Tkinter.Button(self.StratsPage_Lower_Frame, text = u"分组调整", command = modify_group_rule, bg = Config.Orcas_blue)
		self.modify_group_rule_button.pack(side = 'left',anchor = 'w')

		def load_strats_settings():
			strats_idx = self.strats_gui_mgmt.combobox_Strats_Idx.get()
			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_Idx_Name] WHERE [Strats_Idx] = " + strats_idx
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			strat_res = res_list[0]

			rt_dir = unicode(strat_res['RT_Dir'].values[0])
			display_top_n = unicode(strat_res['Display_Top_N'].values[0])
			sort_by = unicode(strat_res['Sort_by'].values[0])

			self.strats_gui_mgmt.text_Strats_RT_Dir.delete("1.0",'end')
			self.strats_gui_mgmt.text_Strats_RT_Dir.insert('end',rt_dir)

			self.strats_gui_mgmt.text_Display_Top_N.delete("1.0",'end')
			self.strats_gui_mgmt.text_Display_Top_N.insert('end',display_top_n)

			self.strats_gui_mgmt.text_Sort_By.delete("1.0",'end')
			self.strats_gui_mgmt.text_Sort_By.insert('end',sort_by)

			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_Dimensions] WHERE [Strats_Idx] = " + strats_idx
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			strats_dimension_res = res_list[0]

			strats_dimension_res.replace(np.NaN,'',inplace = True)
			strats_dimension_settings_load = strats_dimension_res[['Dime_Ori_Label','Rule_Idx','Dime_Std_Label']]
			
			self.strats_dimension_settings.load_settings(strats_dimension_settings_load)

			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_Measures] WHERE [Strats_Idx] = " + strats_idx
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			strats_measures_res = res_list[0]

			strats_measures_res.replace(np.NaN,'',inplace = True)
			strats_measures_settings_load = strats_measures_res[['Meas_Ori_Label','Calc_Method','Calc_Helper','Meas_Std_Label','format']]
			self.strats_measures_settings.load_settings(strats_measures_settings_load)

		self.stratspage_load_strats_settings_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"载入分层设置", command = load_strats_settings,bg = Config.Orcas_blue)
		self.stratspage_load_strats_settings_button.pack(side = 'left',anchor = 'w')


		def save_strats_settings():
			strats_raw_tape_dir = self.strats_gui_mgmt.text_Strats_RT_Dir.get('0.0','end-1c')
			strats_display_topn = int(self.strats_gui_mgmt.text_Display_Top_N.get('0.0','end-1c'))
			strats_sort_by = int(self.strats_gui_mgmt.text_Sort_By.get('0.0','end-1c'))

			strats_settings_name = self.strats_gui_mgmt.text_Strats_Name.get('0.0','end-1c')

			self.strats_dimension_settings.get_all(dict_type =True)
			strats_dimension_df = pd.DataFrame(self.strats_dimension_settings.res)

			strats_dimension_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in zip(Config.dimension_settings_columns_gui,Config.dimension_settings_columns_txt)])
			strats_dimension_df = strats_dimension_df.rename(columns = strats_dimension_columns)
			strats_dimension_df = strats_dimension_df[Config.dimension_settings_columns_txt]

			self.strats_measures_settings.get_all(dict_type =True)
			strats_measures_df = pd.DataFrame(self.strats_measures_settings.res)

			strats_measures_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in zip(Config.measures_settings_columns_gui,Config.measures_settings_columns_txt)])
			strats_measures_df = strats_measures_df.rename(columns = strats_measures_columns)
			strats_measures_df = strats_measures_df[Config.measures_settings_columns_txt]

			sql_query = "SELECT * FROM [Orcas_Operation].[dbo].[Strats_Idx_Name]"
			res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
			strats_idx_name_df = res_list[0]
			new_strats_idx = max(strats_idx_name_df['Strats_Idx']) + 1

			strats_idx_name_new_line = pd.DataFrame(columns = Config.strats_idx_name_db_table_columns)
			strats_idx_name_new_line.loc[0] = [new_strats_idx,strats_settings_name,strats_raw_tape_dir,strats_sort_by,strats_display_topn]
			strats_idx_name_new_line.to_csv(Config.strats_idx_name_temp_txt,sep = "|",header = False, index = False)

			strats_dimension_df.loc[:,'Strats_Idx'] = new_strats_idx
			strats_dimension_df.loc[:,'Dime_Idx'] = range(1,len(strats_dimension_df)+1)
			strats_dimension_df = strats_dimension_df[['Dime_Idx','column','strats_label','group_rule','Strats_Idx']]
			strats_dimension_df.to_csv(Config.strats_dimension_settings_temp_txt,sep = "|",header = False, index = False)

			strats_measures_df.loc[:,'Strats_Idx'] = new_strats_idx
			strats_measures_df.loc[:,'Meas_Idx'] = range(1,len(strats_measures_df)+1)
			strats_measures_df = strats_measures_df[['Meas_Idx','column','col_name','calc_method','calc_helper','Strats_Idx','format']]
			strats_measures_df.to_csv(Config.strats_measures_settings_temp_txt,sep = "|",header = False, index = False)

			IO_Utilities.SQL_Util.upload_orcas_operation_strats_tables()
			self.strats_gui_mgmt.refresh_strats_records()


		self.stratspage_save_strats_settings_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"保存分层设置", command = save_strats_settings,bg = Config.Orcas_blue)
		self.stratspage_save_strats_settings_button.pack(side = 'left',anchor = 'w')


		def delete_strats_settings():
			strats_idx_to_be_deleted = self.strats_gui_mgmt.combobox_Strats_Idx.get()
			IO_Utilities.SQL_Util.delete_orcas_operation_strats_records(strats_idx_to_be_deleted)
			self.strats_gui_mgmt.refresh_strats_records()
			

		self.stratspage_delete_strats_settings_button = Tkinter.Button(self.StratsPage_Lower_Frame,text = u"删除分层设置", command = delete_strats_settings,bg = Config.Orcas_blue)
		self.stratspage_delete_strats_settings_button.pack(side = 'left',anchor = 'w')


	def FinancingMgmtPage_design(self):
		self.FinancingMgmtPage_Frame = Tkinter.Frame(self.grand_left_frame)
		self.FinancingMgmtPage_Frame.pack(expand=1, fill="both")

		financingmgmt_line_1 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_1.pack(side = 'top')

		ramping_label = Tkinter.Label(financingmgmt_line_1,text = u"资产累计速率(亿元)",width = 18)
		ramping_label.pack(side ='left',anchor = 'w')
		self.ramping_TextBox = Tkinter.Entry(financingmgmt_line_1, width=10)
		self.ramping_TextBox.insert(0,'1 0')
		self.ramping_TextBox.pack(side = 'left',padx = 10)

		phase1_phase2_trans_label = Tkinter.Label(financingmgmt_line_1,text = u"融资阶段转移期数",width = 18)
		phase1_phase2_trans_label.pack(side = 'left',anchor = 'w')
		self.phase1_phase2_trans_TextBox = Tkinter.Entry(financingmgmt_line_1, width=10)
		self.phase1_phase2_trans_TextBox.insert(0,0)
		self.phase1_phase2_trans_TextBox.pack(side = 'left')

		financingmgmt_line_2 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_2.pack(side = 'top')

		financing_asset_px_center_label = Tkinter.Label(financingmgmt_line_2,text = u"资产居中价格",width = 10)
		financing_asset_px_center_label.pack(side ='left',anchor = 'w')
		self.financing_asset_px_center_TextBox = Tkinter.Entry(financingmgmt_line_2, width=10)
		self.financing_asset_px_center_TextBox.insert(0,100)
		self.financing_asset_px_center_TextBox.pack(side = 'left',padx = 1)

		financing_asset_px_steps_label = Tkinter.Label(financingmgmt_line_2,text = u"价格模拟步数",width = 10)
		financing_asset_px_steps_label.pack(side ='left',anchor = 'w')
		self.financing_asset_px_steps_TextBox = Tkinter.Entry(financingmgmt_line_2, width=10)
		self.financing_asset_px_steps_TextBox.insert(0,1)
		self.financing_asset_px_steps_TextBox.pack(side = 'left',padx = 10)

		financing_asset_px_step_size_label = Tkinter.Label(financingmgmt_line_2,text = u"价格模拟步长",width = 10)
		financing_asset_px_step_size_label.pack(side ='left',anchor = 'w')
		self.financing_asset_px_step_size_TextBox = Tkinter.Entry(financingmgmt_line_2, width=10)
		self.financing_asset_px_step_size_TextBox.insert(0,1)
		self.financing_asset_px_step_size_TextBox.pack(side = 'left',padx = 1)
	

		financingmgmt_line_3 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_3.pack(side = 'top')

		financing_specifcs_title = Tkinter.Label(financingmgmt_line_3, text='融资具体设计方案',bg = 'yellow')
		financing_specifcs_title.pack(side = 'top',expand = 'yes',fill='x')

		financingmgmt_line_4 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_4.pack(side = 'top')

		gridline_canvas = Tkinter.Canvas(financingmgmt_line_4, width=600, height=2, bg="grey")
		gridline_canvas.pack()

		financingmgmt_line_5 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_5.pack(side = 'top')

		financingmgmt_line_5_left = Tkinter.Frame(financingmgmt_line_5,width=50, height=100)
		financingmgmt_line_5_left.pack(side = 'left')

		financingmgmt_line_5_middle = Tkinter.Frame(financingmgmt_line_5)
		financingmgmt_line_5_middle.pack(side = 'left')

		gridline_canvas = Tkinter.Canvas(financingmgmt_line_5_middle, width=2, height=300, bg="grey")
		gridline_canvas.pack(side = 'top')

		financingmgmt_line_5_right = Tkinter.Frame(financingmgmt_line_5,width=50, height=100)
		financingmgmt_line_5_right.pack(side = 'left')

		self.first_financing_gui_mgmt = Struct_GUI_Model.Financing_GUI_Mgmt(financingmgmt_line_5_left,title_IN = u'第一阶段融资')
		self.second_financing_gui_mgmt = Struct_GUI_Model.Financing_GUI_Mgmt(financingmgmt_line_5_right,title_IN = u'第二阶段融资')

		financingmgmt_line_6 = Tkinter.Frame(self.FinancingMgmtPage_Frame,width = 1000)
		financingmgmt_line_6.pack(side = 'top',fill = 'x',expand = 'yes')

		financingmgmt_line_7 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_7.pack(side = 'top',fill = 'x')

		financingmgmt_line_8 = Tkinter.Frame(self.FinancingMgmtPage_Frame)
		financingmgmt_line_8.pack(side = 'top',fill = 'x',expand = 'yes')


		def runLeveredEconomics():
			# run first financing
			self.first_financing_gui_mgmt.live_struct_mgmt.get_specs()
			self.second_financing_gui_mgmt.live_struct_mgmt.get_specs()

			# self.live_agg_unlevered_economics_run_aggregation_cfs[0].to_pickle("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Debug\poolcashflow.pickle")

			self.Levered_Economics_Mgmt_instance = Struct_CF_Model.Levered_Financing(
														   self.live_agg_unlevered_economics_run_aggregation_cfs[0],
														   self.first_financing_gui_mgmt.live_struct_name,
														   self.first_financing_gui_mgmt.live_struct_mgmt.specs,
														   self.ramping_TextBox.get(),
														   int(self.phase1_phase2_trans_TextBox.get()),
														   self.second_financing_gui_mgmt.live_struct_name,
														   self.second_financing_gui_mgmt.live_struct_mgmt.specs
														   )
			self.Levered_Economics_Mgmt_instance.run_financing()
			

		def displayLeveredEconomics(events = None):
			self.px_center = float(self.financing_asset_px_center_TextBox.get())
			self.px_steps = int(self.financing_asset_px_steps_TextBox.get())
			self.px_step_size = float(self.financing_asset_px_step_size_TextBox.get())


			self.LeveredEconomics_Analytics_First_instance = Calc_Utilities.LeveredEconomics_Analytics(
													self.Levered_Economics_Mgmt_instance.first_financing_mgmt.asset_liability_res_df
													,self.px_center
													,self.px_steps
													,self.px_step_size)

			self.LeveredEconomics_Analytics_Second_instance = Calc_Utilities.LeveredEconomics_Analytics(
													self.Levered_Economics_Mgmt_instance.second_financing_mgmt.asset_liability_res_df
													,self.px_center
													,self.px_steps
													,self.px_step_size)

			self.grand_right_upper_frame.destroy()
			self.grand_right_lower_frame.destroy()

			self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)
			self.grand_right_lower_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)

			self.grand_right_upper_frame.pack(side = 'top')
			self.grand_right_lower_frame.pack(side = 'top')

			self.grand_right_upper_left_frame = Tkinter.Frame(self.grand_right_upper_frame,width=100, height=100)
			self.grand_right_upper_right_frame = Tkinter.Frame(self.grand_right_upper_frame,width=100, height=100)

			self.grand_right_upper_left_frame.pack(side = 'left')
			self.grand_right_upper_right_frame.pack(side = 'left')

			self.grand_right_lower_left_frame = Tkinter.Frame(self.grand_right_lower_frame,width=100, height=100)
			self.grand_right_lower_right_frame = Tkinter.Frame(self.grand_right_lower_frame,width=100, height=100)

			self.grand_right_lower_left_frame.pack(side = 'left')
			self.grand_right_lower_right_frame.pack(side = 'left')

			GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_upper_left_frame, df_IN = self.LeveredEconomics_Analytics_First_instance.res_ladder.set_index(['Tranche']),formatting_mapper_IN = self.LeveredEconomics_Analytics_First_instance.ladder_formatting_mappings, horizontal_mapper=False,contents_col_width_IN = 7,index_col_width_IN = 7,index_col_grouping_num_IN = (self.px_steps * 2 + 1), index_col_color_IN = Config.Orcas_blue)
			GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_lower_left_frame, df_IN = self.LeveredEconomics_Analytics_First_instance.res_first_financing_par.set_index(['variable']),formatting_mapper_IN = self.LeveredEconomics_Analytics_First_instance.first_financing_par_formatting_mappings, horizontal_mapper=True,index_col_width_IN = 20,contents_col_width_IN = 20)

			GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_upper_right_frame, df_IN = self.LeveredEconomics_Analytics_Second_instance.res_ladder.set_index(['Tranche']),formatting_mapper_IN = self.LeveredEconomics_Analytics_Second_instance.ladder_formatting_mappings, horizontal_mapper=False,contents_col_width_IN = 7,index_col_width_IN = 7,index_col_grouping_num_IN = (self.px_steps * 2 + 1), index_col_color_IN = Config.Orcas_blue)
			GUI_Utilities.DisplayTable_Mgmt(master = self.grand_right_lower_right_frame, df_IN = self.LeveredEconomics_Analytics_Second_instance.res_first_financing_par.set_index(['variable']),formatting_mapper_IN = self.LeveredEconomics_Analytics_Second_instance.first_financing_par_formatting_mappings, horizontal_mapper=True,index_col_width_IN = 20,contents_col_width_IN = 20)

			if events != None:
				IO_Utilities.IO_Util.open_in_html(self.LeveredEconomics_Analytics_First_instance.res_ladder)
				IO_Utilities.IO_Util.open_in_html(self.LeveredEconomics_Analytics_First_instance.res_first_financing_par)

				IO_Utilities.IO_Util.open_in_html(self.LeveredEconomics_Analytics_Second_instance.res_ladder)
				IO_Utilities.IO_Util.open_in_html(self.LeveredEconomics_Analytics_Second_instance.res_first_financing_par)

		def displayLeveredCF():
			IO_Utilities.IO_Util.open_in_html(self.Levered_Economics_Mgmt_instance.first_financing_mgmt.asset_liability_res_df)
			IO_Utilities.IO_Util.open_in_html(self.Levered_Economics_Mgmt_instance.second_financing_mgmt.asset_liability_res_df)


		def displayLeveredEconomicsGraph():
			self.grand_right_upper_frame.destroy()
			self.grand_right_lower_frame.destroy()

			self.grand_right_upper_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)
			# self.grand_right_lower_frame = Tkinter.Frame(self.grand_right_frame,width=100, height=100)

			self.grand_right_upper_frame.pack(side = 'top')
			# self.grand_right_lower_frame.pack(side = 'top')
			
			dispaly_leveredeconomics_charts_mgmt_instance = GUI_Utilities.Display_LeveredEconomics_Charts_Mgmt_OrcasFormat(self.grand_right_upper_frame,self.Levered_Economics_Mgmt_instance)



		self.Mgmt_Levered_Economics_Run_treeview = GUI_Utilities.Treeview_Mgmt(master = financingmgmt_line_6, df_IN = self.Mgmt_Levered_Economics_df)

		newFinancingStructure_label = Tkinter.Label(financingmgmt_line_7,text = u"融资结构名称",relief = 'ridge')
		newFinancingStructure_label.pack(side = 'left',fill = 'x',expand='yes')

		self.newFinancingStructure_entry = Tkinter.Entry(financingmgmt_line_7,width = 2,bg = Config.Orcas_blue)
		self.newFinancingStructure_entry.pack(side = 'left',fill = 'x',expand='yes')

		def saveFinancingStructure():
			self.first_financing_gui_mgmt.live_struct_mgmt.get_specs(if_raw_IN = True)
			self.second_financing_gui_mgmt.live_struct_mgmt.get_specs(if_raw_IN = True)

			first_financing_name = self.first_financing_gui_mgmt.live_struct_name
			first_financing_specs = self.first_financing_gui_mgmt.live_struct_mgmt.specs
			second_financing_name = self.second_financing_gui_mgmt.live_struct_name
			second_financing_specs = self.second_financing_gui_mgmt.live_struct_mgmt.specs

			other_specs = dict()
			other_specs['transition_period'] = self.phase1_phase2_trans_TextBox.get()
			other_specs['ramping_vector'] =  self.ramping_TextBox.get()
			other_specs['px_center'] =  self.financing_asset_px_center_TextBox.get()
			other_specs['px_steps'] =  self.financing_asset_px_steps_TextBox.get()
			other_specs['px_step_size'] =  self.financing_asset_px_step_size_TextBox.get()

			first_financing = {}
			first_financing['name'] = first_financing_name
			first_financing['specs'] = first_financing_specs

			second_financing = {}
			second_financing['name'] = second_financing_name
			second_financing['specs'] = second_financing_specs

			new_financing_struct_num = max(self.Mgmt_Levered_Economics_df[u'融资结构编号']) + 1
			new_financing_struct_name = self.newFinancingStructure_entry.get()

			output = open(Config.Levered_Economics_Run_Folder + str(new_financing_struct_num) + '.first_financing.pkl', 'wb')
			pickle.dump(first_financing, output)
			output.close()

			output = open(Config.Levered_Economics_Run_Folder + str(new_financing_struct_num) + '.second_financing.pkl', 'wb')
			pickle.dump(second_financing, output)
			output.close()

			output = open(Config.Levered_Economics_Run_Folder + str(new_financing_struct_num) + '.other_specs.pkl', 'wb')
			pickle.dump(other_specs, output)
			output.close()

			self.Mgmt_Levered_Economics_df.loc[max(self.Mgmt_Levered_Economics_df.index)+1] = [new_financing_struct_num,new_financing_struct_name,orcas_user,datetime.now()]
			self.Mgmt_Levered_Economics_df.to_pickle(Config.Mgmt_Levered_Economics_Run_File)
			self.Mgmt_Levered_Economics_Run_treeview.update_dataframe(self.Mgmt_Levered_Economics_df)


		def loadFinancingStructure():
			selected = self.Mgmt_Levered_Economics_Run_treeview.tree.selection()[0]
			selected_values = self.Mgmt_Levered_Economics_Run_treeview.tree.item(selected,'values')
			financing_struct_num = selected_values[0]

			to_be_loaded_first_financing = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.first_financing.pkl'
			to_be_loaded_second_financing = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.second_financing.pkl'
			to_be_loaded_other_specs  = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.other_specs.pkl'

			first_financing_pkl_file = open(to_be_loaded_first_financing, 'rb')
			first_financing_pkl = pickle.load(first_financing_pkl_file)
			first_financing_pkl_file.close()

			second_financing_pkl_file = open(to_be_loaded_second_financing, 'rb')
			second_financing_pkl = pickle.load(second_financing_pkl_file)
			second_financing_pkl_file.close()

			other_specs_pkl_file = open(to_be_loaded_other_specs, 'rb')
			other_specs_pkl = pickle.load(other_specs_pkl_file)
			other_specs_pkl_file.close()

			self.phase1_phase2_trans_TextBox.delete(0,'end')
			self.phase1_phase2_trans_TextBox.insert('end',other_specs_pkl['transition_period'])

			self.ramping_TextBox.delete(0,'end')
			self.ramping_TextBox.insert('end',other_specs_pkl['ramping_vector'])

			self.financing_asset_px_center_TextBox.delete(0,'end')
			self.financing_asset_px_center_TextBox.insert('end',other_specs_pkl['px_center'])

			self.financing_asset_px_steps_TextBox.delete(0,'end')
			self.financing_asset_px_steps_TextBox.insert('end',other_specs_pkl['px_steps'])

			self.financing_asset_px_step_size_TextBox.delete(0,'end')
			self.financing_asset_px_step_size_TextBox.insert('end',other_specs_pkl['px_step_size'])

			self.first_financing_gui_mgmt.live_struct_name = first_financing_pkl['name']
			self.second_financing_gui_mgmt.live_struct_name = second_financing_pkl['name']

			self.first_financing_gui_mgmt.struct_option_strVar.set(self.first_financing_gui_mgmt.live_struct_name)
			self.second_financing_gui_mgmt.struct_option_strVar.set(self.second_financing_gui_mgmt.live_struct_name)

			self.first_financing_gui_mgmt.struct_setup()
			self.second_financing_gui_mgmt.struct_setup()

			self.first_financing_gui_mgmt.load_struct(first_financing_pkl['specs'])
			self.second_financing_gui_mgmt.load_struct(second_financing_pkl['specs'])


		def deleteFinancingStructure():
			for selected in self.Mgmt_Levered_Economics_Run_treeview.tree.selection():
				selected_values = self.Mgmt_Levered_Economics_Run_treeview.tree.item(selected,'values')
				financing_struct_num = selected_values[0]
				to_be_removed_first_financing = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.first_financing.pkl'
				to_be_removed_second_financing = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.second_financing.pkl'
				to_be_removed_other_specs  = Config.Levered_Economics_Run_Folder + str(financing_struct_num) + '.other_specs.pkl'

				try:
					os.remove(to_be_removed_first_financing)
				except:
					pass

				try:
					os.remove(to_be_removed_second_financing)
				except:
					pass	

				try:
					os.remove(to_be_removed_other_specs)
				except:
					pass

				self.Mgmt_Levered_Economics_df = self.Mgmt_Levered_Economics_df[self.Mgmt_Levered_Economics_df[u'融资结构编号']!=int(financing_struct_num)]

			self.Mgmt_Levered_Economics_df.to_pickle(Config.Mgmt_Levered_Economics_Run_File)
			self.Mgmt_Levered_Economics_Run_treeview.update_dataframe(self.Mgmt_Levered_Economics_df)


		self.saveFinancingStructure_Button = Tkinter.Button(financingmgmt_line_8, text = u"保存融资结构", command = saveFinancingStructure,bg = Config.Orcas_blue)
		self.saveFinancingStructure_Button.pack(side = 'left')

		self.loadFinancingStructure_Button = Tkinter.Button(financingmgmt_line_8, text = u"载入融资结构", command = loadFinancingStructure,bg = Config.Orcas_blue)
		self.loadFinancingStructure_Button.pack(side = 'left')

		self.deleteFinancingStructure_Button = Tkinter.Button(financingmgmt_line_8, text = u"删除融资结构", command = deleteFinancingStructure,bg = Config.Orcas_blue)
		self.deleteFinancingStructure_Button.pack(side = 'left')

		self.runLeveredEconomics_Button = Tkinter.Button(financingmgmt_line_8, text = u"新创现金流分析(含融资)", command = runLeveredEconomics,bg = Config.Orcas_blue)
		self.runLeveredEconomics_Button.pack(side = 'left')

		self.displayLeveredCF_Button = Tkinter.Button(financingmgmt_line_8, text = u"融资现金流", command = displayLeveredCF,bg = Config.Orcas_blue)
		self.displayLeveredCF_Button.pack(side = 'left')

		self.displayLeveredEconomics_Button = Tkinter.Button(financingmgmt_line_8, text = u"融资现金流指标", command = displayLeveredEconomics,bg = Config.Orcas_blue)
		self.displayLeveredEconomics_Button.pack(side = 'left')
		self.displayLeveredEconomics_Button.bind("<Button-3>", displayLeveredEconomics)

		self.displayLeveredEconomicsGraph_Button = Tkinter.Button(financingmgmt_line_8, text = u"融资现金流走势", command = displayLeveredEconomicsGraph,bg = Config.Orcas_blue)
		self.displayLeveredEconomicsGraph_Button.pack(side = 'left')

	def VintageAnalysisPage_design(self):
		self.VintageAnalysisPage_Frame = Tkinter.Frame(self.grand_left_frame)
		self.VintageAnalysisPage_Frame.pack(expand=1, fill="both")

		self.VintageAnalysisPage_Upper_Frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Frame,width = 600,height = 100,borderwidth = 2)
		self.VintageAnalysisPage_Upper_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.VintageAnalysisPage_Upper_Frame.pack_propagate(False)

		self.VintageAnalysisPage_Middle_Frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Frame,width = 600,height = 400,borderwidth = 2)
		self.VintageAnalysisPage_Middle_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.VintageAnalysisPage_Middle_Frame.pack_propagate(False)

		self.VintageAnalysisPage_Lower_Frame = Tkinter.Frame(self.VintageAnalysisPage_Frame)
		self.VintageAnalysisPage_Lower_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')

		self.VintageAnalysisPage_Middle_1_Frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_Frame,width = 600,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_Middle_1_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.VintageAnalysisPage_Middle_1_Frame.pack_propagate(False)

		self.VintageAnalysisPage_Middle_2_Frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_Frame,width = 600,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_Middle_2_Frame.pack(expand=1, fill="both",anchor = 'n',side = 'top')
		self.VintageAnalysisPage_Middle_2_Frame.pack_propagate(False)

		self.VintageAnalysisPage_221_frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_1_Frame,width = 300,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_221_frame.pack(side = 'left',anchor = 'n')
		self.VintageAnalysisPage_221_frame.pack_propagate(False)

		self.VintageAnalysisPage_222_frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_1_Frame,width = 300,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_222_frame.pack(side = 'left',anchor = 'n')
		self.VintageAnalysisPage_222_frame.pack_propagate(False)

		self.VintageAnalysisPage_223_frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_2_Frame,width = 300,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_223_frame.pack(side = 'left',anchor = 'n')
		self.VintageAnalysisPage_223_frame.pack_propagate(False)

		self.VintageAnalysisPage_224_frame = Tkinter.LabelFrame(self.VintageAnalysisPage_Middle_2_Frame,width = 300,height = 200,borderwidth = 2)
		self.VintageAnalysisPage_224_frame.pack(side = 'left',anchor = 'n')
		self.VintageAnalysisPage_224_frame.pack_propagate(False)

		self.VintageAnalysisPage_left_line_2_frame = Tkinter.Frame(self.VintageAnalysisPage_Upper_Frame)
		self.VintageAnalysisPage_left_line_2_frame.pack(side = 'top')
		self.vintageanalysis_gui_mgmt = Vintage_Interface.Vintage_settings(self.VintageAnalysisPage_left_line_2_frame)

		self.VintageAnalysisPage_right_line_1_frame = Tkinter.Frame(self.VintageAnalysisPage_221_frame)
		self.VintageAnalysisPage_right_line_1_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.VintageAnalysisPage_right_line_1_canvas = Tkinter.Canvas(self.VintageAnalysisPage_right_line_1_frame, width=800, height=500, bg="white")
		self.VintageAnalysisPage_right_line_1_new_frame = Tkinter.Frame(self.VintageAnalysisPage_right_line_1_canvas)

		ysb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_1_frame,orient='vertical', command= self.VintageAnalysisPage_right_line_1_canvas.yview)
		self.VintageAnalysisPage_right_line_1_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_1_frame, orient='horizontal', command= self.VintageAnalysisPage_right_line_1_canvas.xview)
		self.VintageAnalysisPage_right_line_1_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.VintageAnalysisPage_right_line_1_canvas.pack(side = 'left')
		self.VintageAnalysisPage_right_line_1_canvas.create_window((0,1), window=self.VintageAnalysisPage_right_line_1_new_frame, anchor="nw")

		def reconfigure_scrollregion1(event):
			self.VintageAnalysisPage_right_line_1_canvas.configure(scrollregion=self.VintageAnalysisPage_right_line_1_canvas.bbox("all"))

		self.VintageAnalysisPage_right_line_1_new_frame.bind("<Configure>",reconfigure_scrollregion1)

		self.vintageanalysis_dimension_settings = GUI_Utilities.ConditionGroup_Mgmt(self.VintageAnalysisPage_right_line_1_new_frame,title_list_IN=Config.vintage_dimension_settings_columns_gui,BoxGroup_width_IN = 9,Label_width_IN = 11,add_condition_button_text_IN = u'添加维度',delete_condition_button_text_IN = u'删除维度',style_IN = 'ComboBox')

		self.VintageAnalysisPage_right_line_2_frame = Tkinter.Frame(self.VintageAnalysisPage_222_frame)
		self.VintageAnalysisPage_right_line_2_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.VintageAnalysisPage_right_line_2_canvas = Tkinter.Canvas(self.VintageAnalysisPage_right_line_2_frame, width=800, height=500, bg="white")
		self.VintageAnalysisPage_right_line_2_new_frame = Tkinter.Frame(self.VintageAnalysisPage_right_line_2_canvas)

		ysb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_2_frame,orient='vertical', command= self.VintageAnalysisPage_right_line_2_canvas.yview)
		self.VintageAnalysisPage_right_line_2_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_2_frame, orient='horizontal', command= self.VintageAnalysisPage_right_line_2_canvas.xview)
		self.VintageAnalysisPage_right_line_2_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.VintageAnalysisPage_right_line_2_canvas.pack(side = 'left')
		self.VintageAnalysisPage_right_line_2_canvas.create_window((0,1), window=self.VintageAnalysisPage_right_line_2_new_frame, anchor="nw")

		def reconfigure_scrollregion2(event):
			self.VintageAnalysisPage_right_line_2_canvas.configure(scrollregion=self.VintageAnalysisPage_right_line_2_canvas.bbox("all"))
		self.VintageAnalysisPage_right_line_2_new_frame.bind("<Configure>",reconfigure_scrollregion2)

		self.vintageanalysis_measures_settings = GUI_Utilities.ConditionGroup_Mgmt(self.VintageAnalysisPage_right_line_2_new_frame,
			title_list_IN=Config.vintage_measures_settings_columns_gui,BoxGroup_width_IN = 6,Label_width_IN = 8, add_condition_button_text_IN = u'添加指标',
			delete_condition_button_text_IN = u'删除指标',style_IN = 'ComboBox')


		self.VintageAnalysisPage_right_line_3_frame = Tkinter.Frame(self.VintageAnalysisPage_223_frame)
		self.VintageAnalysisPage_right_line_3_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.VintageAnalysisPage_right_line_3_canvas = Tkinter.Canvas(self.VintageAnalysisPage_right_line_3_frame, width=800, height=500, bg="white")
		self.VintageAnalysisPage_right_line_3_new_frame = Tkinter.Frame(self.VintageAnalysisPage_right_line_3_canvas)

		ysb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_3_frame,orient='vertical', command= self.VintageAnalysisPage_right_line_3_canvas.yview)
		self.VintageAnalysisPage_right_line_3_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_3_frame, orient='horizontal', command= self.VintageAnalysisPage_right_line_3_canvas.xview)
		self.VintageAnalysisPage_right_line_3_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.VintageAnalysisPage_right_line_3_canvas.pack(side = 'left')
		self.VintageAnalysisPage_right_line_3_canvas.create_window((0,1), window=self.VintageAnalysisPage_right_line_3_new_frame, anchor="nw")

		def reconfigure_scrollregion3(event):
			self.VintageAnalysisPage_right_line_3_canvas.configure(scrollregion=self.VintageAnalysisPage_right_line_3_canvas.bbox("all"))
		self.VintageAnalysisPage_right_line_3_new_frame.bind("<Configure>",reconfigure_scrollregion3)

		self.vintageanalysis_measures_settings = GUI_Utilities.ConditionGroup_Mgmt(self.VintageAnalysisPage_right_line_3_new_frame,
			title_list_IN=Config.vintage_condition_settings_columns_gui,BoxGroup_width_IN = 6,Label_width_IN = 8, add_condition_button_text_IN = u'添加条件',
			delete_condition_button_text_IN = u'删除条件',style_IN = 'ComboBox')


		self.VintageAnalysisPage_right_line_4_frame = Tkinter.Frame(self.VintageAnalysisPage_224_frame)
		self.VintageAnalysisPage_right_line_4_frame.pack(side = 'top', fill ='both', expand = 'yes')
		self.VintageAnalysisPage_right_line_4_canvas = Tkinter.Canvas(self.VintageAnalysisPage_right_line_4_frame, width=800, height=500, bg="white")
		self.VintageAnalysisPage_right_line_4_new_frame = Tkinter.Frame(self.VintageAnalysisPage_right_line_4_canvas)

		ysb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_4_frame,orient='vertical', command= self.VintageAnalysisPage_right_line_4_canvas.yview)
		self.VintageAnalysisPage_right_line_4_canvas.configure(yscrollcommand=ysb.set)
		ysb.pack(side = 'right',fill = 'y')

		xsb = ttk.Scrollbar(self.VintageAnalysisPage_right_line_4_frame, orient='horizontal', command= self.VintageAnalysisPage_right_line_4_canvas.xview)
		self.VintageAnalysisPage_right_line_4_canvas.configure(xscrollcommand=xsb.set)
		xsb.pack(side = 'bottom',fill = 'x')

		self.VintageAnalysisPage_right_line_4_canvas.pack(side = 'left')
		self.VintageAnalysisPage_right_line_4_canvas.create_window((0,1), window=self.VintageAnalysisPage_right_line_4_new_frame, anchor="nw")

		def reconfigure_scrollregion4(event):
			self.VintageAnalysisPage_right_line_4_canvas.configure(scrollregion=self.VintageAnalysisPage_right_line_4_canvas.bbox("all"))
		self.VintageAnalysisPage_right_line_4_new_frame.bind("<Configure>",reconfigure_scrollregion4)

		self.vintageanalysis_measures_settings = GUI_Utilities.ConditionGroup_Mgmt(self.VintageAnalysisPage_right_line_4_new_frame,
			title_list_IN=Config.vintage_grouping_settings_columns_gui,BoxGroup_width_IN = 6,Label_width_IN = 8, add_condition_button_text_IN = u'添加分组',
			delete_condition_button_text_IN = u'删除分组',style_IN = 'ComboBox')


		def run_vintage_analysis(events = None):
			print "to be deleloped"


		self.vintageanalysispage_run_vintage_button = Tkinter.Button(self.VintageAnalysisPage_Lower_Frame,text = u"批次分析", command = run_vintage_analysis,bg = Config.Orcas_blue)
		self.vintageanalysispage_run_vintage_button.pack(side = 'left',anchor = 'w')
		self.vintageanalysispage_run_vintage_button.bind("<Button-3>", run_vintage_analysis)

def main():
	root = Tkinter.Tk()
	Orcas_app = Orcas_Wrapper(master=root)
	Orcas_app.master.title("Orcas v1.0")
	Orcas_app.master.iconbitmap(Config.ORCAS_ICON)
	Orcas_app.mainloop()
	
	
if __name__ == "__main__":
	main()
