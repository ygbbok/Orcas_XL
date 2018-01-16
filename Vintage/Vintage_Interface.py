#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import Tkinter as Tkinter
import os
import sys
import shutil
import pandas as pd
import numpy as np
import math
import pyodbc
import ttk as ttk
from Config import Config
from GUI_Utilities import GUI_Utilities

reload(sys)
sys.setdefaultencoding( "gb2312" )

from tkinter import Tk, StringVar, ttk
from Tkinter import *
from Tkinter import END

from IO_Utilities import IO_Utilities
from RTD_Analytics import RTD_Analytics

class Vintage_settings(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.frame = Tkinter.Frame(self)
		self.frame.pack()

		self.line_1_frame = Tkinter.Frame(self.frame)
		self.line_1_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Settings = Tkinter.Label(self.line_1_frame, text = "                                                      分批次资产分析参数设置                                                       ",borderwidth = 2,relief = 'ridge')
		self.label_Vintageanalysis_Settings.pack(side = TOP)

		self.line_2_frame = Tkinter.Frame(self.frame)
		self.line_2_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Repayment_Dir = Tkinter.Label(self.line_2_frame, text = '贷款回款文档路径:',width = 6,anchor = 'w')
		self.label_Vintageanalysis_Repayment_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Vintageanalysis_Repayment_Dir = Tkinter.Text(self.line_2_frame, height = 2, width = 45)
		self.text_Vintageanalysis_Repayment_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')

		self.line_3_frame = Tkinter.Frame(self.frame)
		self.line_3_frame.pack(side = 'top',expand = 'yes',fill = 'x')


		self.label_Vintageanalysis_Loantape_Dir = Tkinter.Label(self.line_3_frame, text = '贷款特征文档路径:',width = 6,anchor = 'w')
		self.label_Vintageanalysis_Loantape_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Vintageanalysis_Loantape_Dir = Tkinter.Text(self.line_3_frame, height = 2, width = 45)
		self.text_Vintageanalysis_Loantape_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')


		self.line_4_frame = Tkinter.Frame(self.frame)
		self.line_4_frame.pack(side = 'top',expand = 'yes',fill = 'x')


		self.line_4_left_frame = Tkinter.Frame(self.line_4_frame)
		self.line_4_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_4_right_frame = Tkinter.Frame(self.line_4_frame)
		self.line_4_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.label_repayment_Loan_Identity = Tkinter.Label(self.line_4_left_frame, text = '回款贷款字段:',width = 6,anchor = 'w')
		self.label_repayment_Loan_Identity.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Loan_Identity_repayment_strVar = Tkinter.StringVar()
		self.combobox_repayment_Loan_Identity = ttk.Combobox(self.line_4_left_frame, textvariable = self.Loan_Identity_repayment_strVar,width = 10)
		self.combobox_repayment_Loan_Identity.pack(side = RIGHT)
		

		self.label_Timeschedule = Tkinter.Label(self.line_4_right_frame, text = '时间先后顺序字段:',width = 6,anchor = 'w')
		self.label_Timeschedule.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Timeschedule_strVar = Tkinter.StringVar()
		self.combobox_Timeschedule = ttk.Combobox(self.line_4_right_frame, textvariable = self.Timeschedule_strVar,width = 10)
		self.combobox_Timeschedule.pack(side = RIGHT)

		self.line_5_frame = Tkinter.Frame(self.frame)
		self.line_5_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.line_5_left_frame = Tkinter.Frame(self.line_5_frame)
		self.line_5_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_5_right_frame = Tkinter.Frame(self.line_5_frame)
		self.line_5_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)


		self.label_Orig_Bal = Tkinter.Label(self.line_5_left_frame, text = '原始本金字段:',width = 6,anchor = 'w')
		self.label_Orig_Bal.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Orig_Bal_strVar = Tkinter.StringVar()
		self.combobox_Orig_Bal = ttk.Combobox(self.line_5_left_frame, textvariable = self.Orig_Bal_strVar,width = 10)
		self.combobox_Orig_Bal.pack(side = RIGHT)
		

		self.label_BOP_Bal = Tkinter.Label(self.line_5_right_frame, text = '期初本金字段:',width = 6,anchor = 'w')
		self.label_BOP_Bal.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.BOP_Bal_strVar = Tkinter.StringVar()
		self.combobox_BOP_Bal = ttk.Combobox(self.line_5_right_frame, textvariable = self.BOP_Bal_strVar,width = 10)
		self.combobox_BOP_Bal.pack(side = RIGHT)


		self.line_6_frame = Tkinter.Frame(self.frame)
		self.line_6_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.line_6_left_frame = Tkinter.Frame(self.line_6_frame)
		self.line_6_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_6_right_frame = Tkinter.Frame(self.line_6_frame)
		self.line_6_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)


		self.label_Sche_Bal = Tkinter.Label(self.line_6_left_frame, text = '应还本金字段:',width = 6,anchor = 'w')
		self.label_Sche_Bal.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Sche_Bal_strVar = Tkinter.StringVar()
		self.combobox_Sche_Bal = ttk.Combobox(self.line_6_left_frame, textvariable = self.Sche_Bal_strVar,width = 10)
		self.combobox_Sche_Bal.pack(side = RIGHT)
		
		self.label_Default_Bal = Tkinter.Label(self.line_6_right_frame, text = '违约金额字段:',width = 6,anchor = 'w')
		self.label_Default_Bal.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Default_Bal_strVar = Tkinter.StringVar()
		self.combobox_Default_Bal = ttk.Combobox(self.line_6_right_frame, textvariable = self.Default_Bal_strVar,width = 10)
		self.combobox_Default_Bal.pack(side = RIGHT)

		self.line_7_frame = Tkinter.Frame(self.frame)
		self.line_7_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.line_7_left_frame = Tkinter.Frame(self.line_7_frame)
		self.line_7_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_7_right_frame = Tkinter.Frame(self.line_7_frame)
		self.line_7_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.label_Prepay_Bal = Tkinter.Label(self.line_7_left_frame, text = '早偿金额字段:',width = 6,anchor = 'w')
		self.label_Prepay_Bal.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Prepay_Bal_strVar = Tkinter.StringVar()
		self.combobox_Prepay_Bal = ttk.Combobox(self.line_7_left_frame, textvariable = self.Prepay_Bal_strVar,width = 10)
		self.combobox_Prepay_Bal.pack(side = RIGHT)

		self.label_loantape_Loan_Identity = Tkinter.Label(self.line_7_right_frame, text = '贷款特征编号字段:',width = 6,anchor = 'w')
		self.label_loantape_Loan_Identity.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.loantape_Loan_Identity_strVar = Tkinter.StringVar()
		self.combobox_loantape_Loan_Identity = ttk.Combobox(self.line_7_right_frame, textvariable = self.loantape_Loan_Identity_strVar,width = 10)
		self.combobox_loantape_Loan_Identity.pack(side = RIGHT)


		self.line_8_frame = Tkinter.Frame(self.frame)
		self.line_8_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_add_code = Tkinter.Label(self.line_8_frame, text = "补充代码:",width = 15,anchor = 'w')
		self.label_add_code.pack(side = "left")

		self.text_add_code = Tkinter.Text(self.line_8_frame, height = 3, width = 15)
		self.text_add_code.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')


		self.line_9_frame = Tkinter.Frame(self.frame)
		self.line_9_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Settings = Tkinter.Label(self.line_9_frame, text = "                                                      分批次资产分析设置记录                                                      ",borderwidth = 2,relief = 'ridge')
		self.label_Vintageanalysis_Settings.pack(side = TOP)

		self.line_10_frame = Tkinter.Frame(self.frame)
		self.line_10_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Idx = Tkinter.Label(self.line_10_frame, text = "分批次资产分析设置序号:")
		self.label_Vintageanalysis_Idx.pack(side = LEFT)

		self.Static_strVar = Tkinter.StringVar()
		self.combobox_Vintageanalysis_Idx = ttk.Combobox(self.line_10_frame, textvariable = self.Static_strVar,width = 10)
		self.combobox_Vintageanalysis_Idx.pack(side = RIGHT)
		# self.refresh_Vintageanalysis_records()

		def pop_strat_name(events):
			strat_idx_selected = self.combobox_Vintageanalysis_Idx.get()
			strat_name = self.strat_idx_records[self.strat_idx_records['Vintageanalysis_Idx'].astype(str) == str(strat_idx_selected)]['Vintageanalysis_Name'].values[0]
			self.text_Vintageanalysis_Name.delete("1.0",END)
			self.text_Vintageanalysis_Name.insert(END,strat_name)

		self.combobox_Vintageanalysis_Idx.bind("<<ComboboxSelected>>", pop_strat_name)

		self.line_11_frame = Tkinter.Frame(self.frame)
		self.line_11_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Name = Tkinter.Label(self.line_11_frame, text = "分批次资产分析设置名称:",width = 20,anchor = 'w')
		self.label_Vintageanalysis_Name.pack(side = "left")

		self.text_Vintageanalysis_Name = Tkinter.Text(self.line_11_frame, height = 1, width = 10)
		self.text_Vintageanalysis_Name.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')


	def refresh_Vintageanalysis_records(self):
		sql_query = "SELECT [Vintageanalysis_Idx],[Vintageanalysis_Name] FROM [Orcas_Operation].[dbo].[Vintageanalysis_Idx_Name]"
		res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
		self.strat_idx_records = res_list[0]

		Vintageanalysis_idx =  self.strat_idx_records['Vintageanalysis_Idx'].values
		Vintageanalysis_name =  [unicode(item) for item in list(self.strat_idx_records['Vintageanalysis_Name'].values)]

		strVar = ''
		for i in range(0, Vintageanalysis_idx.size):
			strVar = strVar + str(Vintageanalysis_idx[i]) + ' '

		self.combobox_Vintageanalysis_Idx['values'] = strVar