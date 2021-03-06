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
# sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from IO_Utilities import IO_Utilities
from RTD_Analytics import RTD_Analytics


class Strats_settings(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.frame = Tkinter.Frame(self)
		self.frame.pack()

		self.line_1_frame = Tkinter.Frame(self.frame)
		self.line_1_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Strats_Settings = Tkinter.Label(self.line_1_frame, text = "                                                      分层统计参数设置                                                       ",borderwidth = 2,relief = 'ridge')
		self.label_Strats_Settings.pack(side = TOP)

		self.line_2_frame = Tkinter.Frame(self.frame)
		self.line_2_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Strats_RT_Dir = Tkinter.Label(self.line_2_frame, text = '样本数据文档路径:',width = 6,anchor = 'w')
		self.label_Strats_RT_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Strats_RT_Dir = Tkinter.Text(self.line_2_frame, height = 2, width = 45)
		self.text_Strats_RT_Dir.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')


		self.line_3_frame = Tkinter.Frame(self.frame)
		self.line_3_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.line_3_left_frame = Tkinter.Frame(self.line_3_frame)
		self.line_3_left_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.line_3_right_frame = Tkinter.Frame(self.line_3_frame)
		self.line_3_right_frame.pack(side = 'left', expand = 'yes', fill = 'x',padx = 3)

		self.label_Sort_By = Tkinter.Label(self.line_3_left_frame, text = '排序度量编号:',width = 6,anchor = 'w')
		self.label_Sort_By.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Sort_By = Tkinter.Text(self.line_3_left_frame, height = 1, width = 5)
		self.text_Sort_By.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')

		self.label_Display_Top_N = Tkinter.Label(self.line_3_right_frame, text = '显示靠前记录:',width = 6,anchor = 'w')
		self.label_Display_Top_N.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')
		self.text_Display_Top_N = Tkinter.Text(self.line_3_right_frame, height = 1, width = 5)
		self.text_Display_Top_N.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')

		self.line_4_frame = Tkinter.Frame(self.frame)
		self.line_4_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_add_code = Tkinter.Label(self.line_4_frame, text = "补充代码:",width = 15,anchor = 'w')
		self.label_add_code.pack(side = "left")

		self.text_add_code = Tkinter.Text(self.line_4_frame, height = 1, width = 15)
		self.text_add_code.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')

		self.line_5_frame = Tkinter.Frame(self.frame)
		self.line_5_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Strats_Settings = Tkinter.Label(self.line_5_frame, text = "                                                      分层统计设置记录                                                      ",borderwidth = 2,relief = 'ridge')
		self.label_Strats_Settings.pack(side = TOP)

		self.line_6_frame = Tkinter.Frame(self.frame)
		self.line_6_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Strats_Idx = Tkinter.Label(self.line_6_frame, text = "分层统计设置序号:")
		self.label_Strats_Idx.pack(side = LEFT)

		self.Static_strVar = Tkinter.StringVar()
		self.combobox_Strats_Idx = ttk.Combobox(self.line_6_frame, textvariable = self.Static_strVar,width = 10)
		self.combobox_Strats_Idx.pack(side = RIGHT)
		self.refresh_strats_records()

		def pop_strat_name(events):
			strat_idx_selected = self.combobox_Strats_Idx.get()
			strat_name = self.strat_idx_records[self.strat_idx_records['Strats_Idx'].astype(str) == str(strat_idx_selected)]['Strats_Name'].values[0]
			self.text_Strats_Name.delete("1.0",END)
			self.text_Strats_Name.insert(END,strat_name)

		self.combobox_Strats_Idx.bind("<<ComboboxSelected>>", pop_strat_name)

		self.line_7_frame = Tkinter.Frame(self.frame)
		self.line_7_frame.pack(side = 'top',expand = 'yes',fill = 'x')

		self.label_Strats_Name = Tkinter.Label(self.line_7_frame, text = "分层统计设置名称:",width = 15,anchor = 'w')
		self.label_Strats_Name.pack(side = "left")

		self.text_Strats_Name = Tkinter.Text(self.line_7_frame, height = 1, width = 15)
		self.text_Strats_Name.pack(side = 'left',anchor = 'w',expand = 'yes',fill = 'x')




	def refresh_strats_records(self):
		sql_query = "SELECT [Strats_Idx],[Strats_Name] FROM [Orcas_Operation].[dbo].[Strats_Idx_Name]"
		res_list = IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 1,database = Config.orcas_operation_db)
		self.strat_idx_records = res_list[0]

		strats_idx =  self.strat_idx_records['Strats_Idx'].values
		strats_name =  [unicode(item) for item in list(self.strat_idx_records['Strats_Name'].values)]

		strVar = ''
		for i in range(0, strats_idx.size):
			strVar = strVar + str(strats_idx[i]) + ' '

		self.combobox_Strats_Idx['values'] = strVar