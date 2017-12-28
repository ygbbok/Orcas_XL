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

		self.label_Vintageanalysis_RT_Dir = Tkinter.Label(self.line_2_frame, text = '样本数据文档路径:',width = 6,anchor = 'w')
		self.label_Vintageanalysis_RT_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Vintageanalysis_RT_Dir = Tkinter.Text(self.line_2_frame, height = 2, width = 45)
		self.text_Vintageanalysis_RT_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')

		# to be removed later
		# self.text_Vintageanalysis_RT_Dir.set("F:\Work\Bohai Huijin Asset Management\Investment\ABS Investment\Opportunities\5.RawTape\chinatopcredit.all.loantape.csv")
		# to be removed later


		self.line_3_frame = Tkinter.Frame(self.frame)
		self.line_3_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.line_3_left_frame = Tkinter.Frame(self.line_3_frame)
		self.line_3_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_3_right_frame = Tkinter.Frame(self.line_3_frame)
		self.line_3_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.label_Loan_Identity = Tkinter.Label(self.line_3_left_frame, text = '贷款编号字段:',width = 6,anchor = 'w')
		self.label_Loan_Identity.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Loan_Identity_strVar = Tkinter.StringVar()
		self.combobox_Loan_Identity = ttk.Combobox(self.line_3_left_frame, textvariable = self.Loan_Identity_strVar,width = 10)
		self.combobox_Loan_Identity.pack(side = RIGHT)
		

		self.label_Timeschedule = Tkinter.Label(self.line_3_right_frame, text = '时间先后顺序字段:',width = 6,anchor = 'w')
		self.label_Timeschedule.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.Timeschedule_strVar = Tkinter.StringVar()
		self.combobox_Timeschedule = ttk.Combobox(self.line_3_right_frame, textvariable = self.Timeschedule_strVar,width = 10)
		self.combobox_Timeschedule.pack(side = RIGHT)



		self.line_4_frame = Tkinter.Frame(self.frame)
		self.line_4_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Settings = Tkinter.Label(self.line_4_frame, text = "                                                      分批次资产分析设置记录                                                      ",borderwidth = 2,relief = 'ridge')
		self.label_Vintageanalysis_Settings.pack(side = TOP)

		self.line_5_frame = Tkinter.Frame(self.frame)
		self.line_5_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Idx = Tkinter.Label(self.line_5_frame, text = "分批次资产分析设置序号:")
		self.label_Vintageanalysis_Idx.pack(side = LEFT)

		self.Static_strVar = Tkinter.StringVar()
		self.combobox_Vintageanalysis_Idx = ttk.Combobox(self.line_5_frame, textvariable = self.Static_strVar,width = 10)
		self.combobox_Vintageanalysis_Idx.pack(side = RIGHT)
		# self.refresh_Vintageanalysis_records()

		def pop_strat_name(events):
			strat_idx_selected = self.combobox_Vintageanalysis_Idx.get()
			strat_name = self.strat_idx_records[self.strat_idx_records['Vintageanalysis_Idx'].astype(str) == str(strat_idx_selected)]['Vintageanalysis_Name'].values[0]
			self.text_Vintageanalysis_Name.delete("1.0",END)
			self.text_Vintageanalysis_Name.insert(END,strat_name)

		self.combobox_Vintageanalysis_Idx.bind("<<ComboboxSelected>>", pop_strat_name)

		self.line_6_frame = Tkinter.Frame(self.frame)
		self.line_6_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Vintageanalysis_Name = Tkinter.Label(self.line_6_frame, text = "分批次资产分析设置名称:",width = 20,anchor = 'w')
		self.label_Vintageanalysis_Name.pack(side = "left")

		self.text_Vintageanalysis_Name = Tkinter.Text(self.line_6_frame, height = 1, width = 10)
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