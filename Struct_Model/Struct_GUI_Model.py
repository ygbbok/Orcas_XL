# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")
import Tkinter as Tkinter
import ttk as ttk
from Config import Config
import pickle
from IO_Utilities import IO_Utilities
from Calc_Utilities import Calc_Utilities
from Other_Utilities import Other_Utilities
from GUI_Utilities import GUI_Utilities

class Financing_GUI_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, struct_specifics_IN = None, title_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.title = title_IN
		self.master_frame = Tkinter.LabelFrame(self,width = 270,height = 300,borderwidth = 2)
		self.master_frame.pack(side = 'top',fill = 'both',expand = 'yes')
		self.master_frame.pack_propagate(False)
		self.live_struct_mgmt = None

		self.specifics_initialize(struct_specifics_IN = struct_specifics_IN)

		# self.load_struct()
	
	def specifics_initialize(self,struct_specifics_IN):
		self.line_1_frame = Tkinter.Frame(self.master_frame)
		self.line_1_frame.pack(side = 'top',anchor = 'nw')

		self.title_label = Tkinter.Label(self.line_1_frame,text = self.title,bg = 'yellow')
		self.title_label.pack(side = 'top')

		self.line_2_frame = Tkinter.Frame(self.master_frame)
		self.line_2_frame.pack(side = 'top',anchor = 'nw')

		self.struct_option_label = Tkinter.Label(self.line_2_frame,text = u"请选择融资方式")
		self.struct_option_label.pack(side = 'left')

		self.struct_option_strVar = Tkinter.StringVar()

		self.struct_option = ttk.Combobox(self.line_2_frame,textvariable = self.struct_option_strVar, values = Config.structmodel_list)
		self.struct_option.bind("<<ComboboxSelected>>", self.struct_setup)

		self.struct_option_strVar.set(Config.structmodel_list[0])

		self.struct_option.pack(side = 'left')

		self.line_3_frame = Tkinter.Frame(self.master_frame)
		self.line_3_frame.pack(side = 'top',anchor = 'nw')


	def struct_setup(self,events = None):
		if self.live_struct_mgmt is not None: self.live_struct_mgmt.destroy()
		value_IN = self.struct_option.get()

		self.live_struct_name = value_IN
		if self.live_struct_name == u'结构化信托(建仓)': self.live_struct_mgmt = Tiered_Trust_GUI_Mgmt(self.line_3_frame)
		elif self.live_struct_name == u'整体买断': self.live_struct_mgmt = Whole_Loan_Purchase_GUI_Mgmt(self.line_3_frame)
		elif self.live_struct_name == u'证券化': self.live_struct_mgmt = Securitization_GUI_Mgmt(self.line_3_frame)

	def load_struct(self,struct_specs_IN):
		self.live_struct_mgmt.load_struct(struct_specs_IN)


class Whole_Loan_Purchase_GUI_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, struct_specifics_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.master_frame = Tkinter.Frame(self)
		self.master_frame.pack(side = 'top')
		self.specs = {}
		self.specifics_initialize(struct_specifics_IN = struct_specifics_IN)

		self.load_struct()

	def get_specs(self,if_raw_IN = False):
		self.specs['upfrontfee'] = float(self.upfront_fee_entry.get())/100.0
		self.specs['mgmt_fee'] = float(self.mgmt_fee_entry.get())/100.0
		self.specs['mgmt_fee_freq'] = int(self.mgmt_fee_freq_entry.get())

		if if_raw_IN:
			self.specs['upfrontfee'] = self.upfront_fee_entry.get()
			self.specs['mgmt_fee'] = self.mgmt_fee_entry.get()
			self.specs['mgmt_fee_freq'] = self.mgmt_fee_freq_entry.get()


	def specifics_initialize(self,struct_specifics_IN):

		self.notebook = ttk.Notebook(self.master_frame)
		self.notebook.pack()

		# PAGE 1 ********************************************
		self.page_1_general = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200,borderwidth = 2)
		self.page_1_general.pack()
		self.page_1_general.pack_propagate(False)

		self.page_1_frame_line_1 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_2 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_3 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.upfront_fee_label = Tkinter.Label(self.page_1_frame_line_1,text = '一次性收费(%)',width = 12,relief = 'ridge')
		self.upfront_fee_label.pack(side = 'left', anchor = 'nw')
		self.upfront_fee_entry = Tkinter.Entry(self.page_1_frame_line_1, width=10)
		self.upfront_fee_entry.insert(0,1)
		self.upfront_fee_entry.pack(side = 'left', anchor = 'nw')

		self.mgmt_fee_label = Tkinter.Label(self.page_1_frame_line_2,text = '存续管理费(%)',width = 12,relief = 'ridge')
		self.mgmt_fee_label.pack(side = 'left', anchor = 'nw')
		self.mgmt_fee_entry = Tkinter.Entry(self.page_1_frame_line_2, width=10)
		self.mgmt_fee_entry.insert(0,1)
		self.mgmt_fee_entry.pack(side = 'left', anchor = 'nw')

		self.mgmt_fee_freq_label = Tkinter.Label(self.page_1_frame_line_3,text = '存续管理费频率',width = 12,relief = 'ridge')
		self.mgmt_fee_freq_label.pack(side = 'left', anchor = 'nw')
		self.mgmt_fee_freq_entry = Tkinter.Entry(self.page_1_frame_line_3, width=10)
		self.mgmt_fee_freq_entry.insert(0,12)
		self.mgmt_fee_freq_entry.pack(side = 'left', anchor = 'nw')

		self.notebook.add(self.page_1_general,text=u"一般条款")

	def load_struct(self,struct_specs_IN):
		pass

class Tiered_Trust_GUI_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, struct_specifics_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.master_frame = Tkinter.Frame(self)
		self.master_frame.pack(side = 'top')
		self.specs = {}

		self.specifics_initialize(struct_specifics_IN = struct_specifics_IN)


	def get_specs(self,if_raw_IN = False):
		self.specs['term'] = int(self.term_entry.get())
		self.specs['snr_intrate'] = float(self.snr_intrate_entry.get())/100.0
		self.specs['snr_freq'] = int(self.snr_freq_entry.get())
		self.specs['snr_advrate'] = float(self.snr_advrate_entry.get())/100.0
		self.specs['trust_fee'] = float(self.trust_chanel_fee_entry.get())/100.0
		self.specs['trust_upfrontfee'] = float(self.trust_chanel_upfrontfee_entry.get())/100.0
		self.specs['reinvestment_vector'] = self.reinvestment_entry.get()
		self.specs['extra_reserve_account_buffer'] = float(self.extra_reserve_account_entry.get())*10000.0
		self.specs['pass_through_trigger_period'] = int(self.passthrough_trigger_entry.get())
		
		if if_raw_IN:
			self.specs['term'] = self.term_entry.get()
			self.specs['snr_intrate'] = self.snr_intrate_entry.get()
			self.specs['snr_freq'] = self.snr_freq_entry.get()
			self.specs['snr_advrate'] = self.snr_advrate_entry.get()
			self.specs['trust_fee'] = self.trust_chanel_fee_entry.get()
			self.specs['trust_upfrontfee'] = self.trust_chanel_upfrontfee_entry.get()
			self.specs['reinvestment_vector'] = self.reinvestment_entry.get()
			self.specs['extra_reserve_account_buffer'] = self.extra_reserve_account_entry.get()
			self.specs['pass_through_trigger_period'] = self.passthrough_trigger_entry.get()

	def specifics_initialize(self,struct_specifics_IN):

		self.notebook = ttk.Notebook(self.master_frame)
		self.notebook.pack()
		

		# PAGE 1 ********************************************
		self.page_1_general = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200,borderwidth = 2)
		self.page_1_general.pack()
		self.page_1_general.pack_propagate(False)

		self.page_1_frame_line_1 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_2 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_3 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.term_label = Tkinter.Label(self.page_1_frame_line_1,text = '期限(月)',width = 12,relief = 'ridge')
		self.term_label.pack(side = 'left', anchor = 'nw')
		self.term_entry = Tkinter.Entry(self.page_1_frame_line_1, width=10)
		self.term_entry.insert(0,12)
		self.term_entry.pack(side = 'left', anchor = 'nw')

		self.reinvestment_label = Tkinter.Label(self.page_1_frame_line_2,text = '循环购买方式',width = 12,relief = 'ridge')
		self.reinvestment_label.pack(side = 'left', anchor = 'nw')
		self.reinvestment_entry = Tkinter.Entry(self.page_1_frame_line_2, width=10)
		self.reinvestment_entry.insert(0,'1 for 6 0')
		self.reinvestment_entry.pack(side = 'left', anchor = 'nw')


		self.passthrough_trigger_label = Tkinter.Label(self.page_1_frame_line_3,text = u'进入摊还期期数',width = 12,relief = 'ridge')
		self.passthrough_trigger_label.pack(side = 'left', anchor = 'nw')
		self.passthrough_trigger_entry = Tkinter.Entry(self.page_1_frame_line_3, width=10)
		self.passthrough_trigger_entry.insert(0,'6')
		self.passthrough_trigger_entry.pack(side = 'left', anchor = 'nw')
		self.notebook.add(self.page_1_general,text=u"一般条款")

		# PAGE 2 ********************************************
		self.page_2_snr = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200)
		self.page_2_snr.pack()

		self.page_2_frame_line_1 = Tkinter.Frame(self.page_2_snr,pady = 0)
		self.page_2_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_2_frame_line_2 = Tkinter.Frame(self.page_2_snr)
		self.page_2_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_2_frame_line_3 = Tkinter.Frame(self.page_2_snr)
		self.page_2_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.snr_intrate_label = Tkinter.Label(self.page_2_frame_line_1,text = u'利率(%)',width = 12,relief = 'ridge')
		self.snr_intrate_label.pack(side = 'left', anchor = 'nw')
		self.snr_intrate_entry = Tkinter.Entry(self.page_2_frame_line_1, width=10)
		self.snr_intrate_entry.insert(0,8)
		self.snr_intrate_entry.pack(side = 'left', anchor = 'nw')

		self.snr_freq_label = Tkinter.Label(self.page_2_frame_line_2,text = u'付息频率',width = 12,relief = 'ridge')
		self.snr_freq_label.pack(side = 'left', anchor = 'nw')
		self.snr_freq_entry = Tkinter.Entry(self.page_2_frame_line_2, width=10)
		self.snr_freq_entry.insert(0,12)
		self.snr_freq_entry.pack(side = 'left', anchor = 'nw')

		self.snr_advrate_label = Tkinter.Label(self.page_2_frame_line_3,text = u'占比(%)',width = 12,relief = 'ridge')
		self.snr_advrate_label.pack(side = 'left', anchor = 'nw')
		self.snr_advrate_entry = Tkinter.Entry(self.page_2_frame_line_3, width=10)
		self.snr_advrate_entry.insert(0,80)
		self.snr_advrate_entry.pack(side = 'left', anchor = 'nw')

		self.notebook.add(self.page_2_snr,text=u"优先级")

		# PAGE 3 ********************************************
		self.page_3_trust = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200)
		self.page_3_trust.pack()
		self.page_3_trust.pack_propagate(False)

		self.page_3_frame_line_1 = Tkinter.Frame(self.page_3_trust,pady = 0)
		self.page_3_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_3_frame_line_2 = Tkinter.Frame(self.page_3_trust)
		self.page_3_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_3_frame_line_3 = Tkinter.Frame(self.page_3_trust)
		self.page_3_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.trust_chanel_fee_label = Tkinter.Label(self.page_3_frame_line_1,text = u'信托区间费用(%)',width = 16,relief = 'ridge')
		self.trust_chanel_fee_label.pack(side = 'left', anchor = 'nw')
		self.trust_chanel_fee_entry = Tkinter.Entry(self.page_3_frame_line_1, width=10)
		self.trust_chanel_fee_entry.insert(0,1)
		self.trust_chanel_fee_entry.pack(side = 'left', anchor = 'nw')

		self.trust_chanel_upfrontfee_label = Tkinter.Label(self.page_3_frame_line_2,text = u'信托一次性费用(%)',width = 16,relief = 'ridge')
		self.trust_chanel_upfrontfee_label.pack(side = 'left', anchor = 'nw')
		self.trust_chanel_upfrontfee_entry = Tkinter.Entry(self.page_3_frame_line_2, width=10)
		self.trust_chanel_upfrontfee_entry.insert(0,1)
		self.trust_chanel_upfrontfee_entry.pack(side = 'left', anchor = 'nw')


		self.notebook.add(self.page_3_trust,text=u"信托")


		# PAGE 4 ********************************************
		self.page_4_resreve = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200)
		self.page_4_resreve.pack()
		self.page_4_resreve.pack_propagate(False)

		self.page_4_frame_line_1 = Tkinter.Frame(self.page_4_resreve,pady = 0)
		self.page_4_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_4_frame_line_2 = Tkinter.Frame(self.page_4_resreve)
		self.page_4_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.extra_reserve_account_label = Tkinter.Label(self.page_4_frame_line_2,text = u'超额准备金阈值(万元)',width = 16,relief = 'ridge')
		self.extra_reserve_account_label.pack(side = 'left', anchor = 'nw')
		self.extra_reserve_account_entry = Tkinter.Entry(self.page_4_frame_line_2, width=10)
		self.extra_reserve_account_entry.insert(0,0)
		self.extra_reserve_account_entry.pack(side = 'left', anchor = 'nw')

		self.notebook.add(self.page_4_resreve,text=u"储备金")

	def load_struct(self, struct_specs_IN):
		self.term_entry.delete(0,'end')
		self.snr_intrate_entry.delete(0,'end')
		self.snr_freq_entry.delete(0,'end')
		self.snr_advrate_entry.delete(0,'end')
		self.trust_chanel_fee_entry.delete(0,'end')
		self.trust_chanel_upfrontfee_entry.delete(0,'end')
		self.reinvestment_entry.delete(0,'end')
		self.extra_reserve_account_entry.delete(0,'end')
		self.passthrough_trigger_entry.delete(0,'end')

		self.term_entry.insert(0,struct_specs_IN['term'])
		self.snr_intrate_entry.insert(0,struct_specs_IN['snr_intrate'])
		self.snr_freq_entry.insert(0,struct_specs_IN['snr_freq'])
		self.snr_advrate_entry.insert(0,struct_specs_IN['snr_advrate'])
		self.trust_chanel_fee_entry.insert(0,struct_specs_IN['trust_fee'])
		self.trust_chanel_upfrontfee_entry.insert(0,struct_specs_IN['trust_upfrontfee'])
		self.reinvestment_entry.insert(0,struct_specs_IN['reinvestment_vector'])
		self.extra_reserve_account_entry.insert(0,struct_specs_IN['extra_reserve_account_buffer'])
		self.passthrough_trigger_entry.insert(0,struct_specs_IN['pass_through_trigger_period'])

class Securitization_GUI_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, struct_specifics_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.master_frame = Tkinter.Frame(self)
		self.master_frame.pack(side = 'top')
		self.specs = {}

		self.specifics_initialize(struct_specifics_IN = struct_specifics_IN)


	def get_specs(self, if_raw_IN = False):
		self.specs['upfront_fee'] = float(self.upfront_fee_entry.get())/100.0
		self.specs['mgmt_fee'] = float(self.mgmt_fee_entry.get())/100.0
		self.specs['mgmt_fee_freq'] = int(self.mgmt_fee_freq_entry.get())
		self.specs['prin_cf_split'] = self.prin_cf_split_option_combobox.get()

		self.specs['snr_intrate'] = float(self.snr_1_intrate_entry.get())/100.0
		self.specs['snr_freq'] = int(self.snr_1_freq_entry.get())
		self.specs['snr_advrate'] = float(self.snr_1_advrate_entry.get())/100.0

		self.specs['mezz_intrate'] = float(self.mezz_intrate_entry.get())/100.0
		self.specs['mezz_freq'] = int(self.mezz_freq_entry.get())
		self.specs['mezz_advrate'] = float(self.mezz_advrate_entry.get())/100.0

		if if_raw_IN:
			self.specs['upfront_fee'] = self.upfront_fee_entry.get()
			self.specs['mgmt_fee'] = self.mgmt_fee_entry.get()
			self.specs['mgmt_fee_freq'] = self.mgmt_fee_freq_entry.get()
			self.specs['prin_cf_split'] = self.prin_cf_split_option_combobox.get()

			self.specs['snr_intrate'] = self.snr_1_intrate_entry.get()
			self.specs['snr_freq'] = self.snr_1_freq_entry.get()
			self.specs['snr_advrate'] = self.snr_1_advrate_entry.get()

			self.specs['mezz_intrate'] = self.mezz_intrate_entry.get()
			self.specs['mezz_freq'] = self.mezz_freq_entry.get()
			self.specs['mezz_advrate'] = self.mezz_advrate_entry.get()

	def specifics_initialize(self,struct_specifics_IN):

		self.notebook = ttk.Notebook(self.master_frame)
		self.notebook.pack()
		

		# PAGE 1 ********************************************
		self.page_1_general = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200,borderwidth = 2)
		self.page_1_general.pack()
		self.page_1_general.pack_propagate(False)

		self.page_1_frame_line_1 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_2 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_3 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_1_frame_line_4 = Tkinter.Frame(self.page_1_general)
		self.page_1_frame_line_4.pack(side = 'top',fill = 'x',anchor = 'n')

		self.upfront_fee_label = Tkinter.Label(self.page_1_frame_line_1,text = '一次性费用(%)',width = 18,relief = 'ridge')
		self.upfront_fee_label.pack(side = 'left', anchor = 'nw')
		self.upfront_fee_entry = Tkinter.Entry(self.page_1_frame_line_1, width=10)
		self.upfront_fee_entry.insert(0,1)
		self.upfront_fee_entry.pack(side = 'left', anchor = 'nw')

		self.mgmt_fee_label = Tkinter.Label(self.page_1_frame_line_2,text = '期间费用(%)',width = 18,relief = 'ridge')
		self.mgmt_fee_label.pack(side = 'left', anchor = 'nw')
		self.mgmt_fee_entry = Tkinter.Entry(self.page_1_frame_line_2, width=10)
		self.mgmt_fee_entry.insert(0,1)
		self.mgmt_fee_entry.pack(side = 'left', anchor = 'nw')

		self.mgmt_fee_freq_label = Tkinter.Label(self.page_1_frame_line_3,text = '期间费用频率',width = 18,relief = 'ridge')
		self.mgmt_fee_freq_label.pack(side = 'left', anchor = 'nw')
		self.mgmt_fee_freq_entry = Tkinter.Entry(self.page_1_frame_line_3, width=10)
		self.mgmt_fee_freq_entry.insert(0,12)
		self.mgmt_fee_freq_entry.pack(side = 'left', anchor = 'nw')

		self.prin_cf_split_label = Tkinter.Label(self.page_1_frame_line_4,text = '本金分配方式',width = 18,relief = 'ridge')
		self.prin_cf_split_label.pack(side = 'left', anchor = 'nw')
		self.prin_cf_split_strVar = Tkinter.StringVar()
		self.prin_cf_split_option_combobox = ttk.Combobox(self.page_1_frame_line_4, textvariable=self.prin_cf_split_strVar, values=[u'顺序瀑布',u'按存续比例'])
		self.prin_cf_split_strVar.set([u'顺序瀑布',u'按存续比例'][0])
		self.prin_cf_split_option_combobox.pack(side = 'left')

		self.notebook.add(self.page_1_general,text=u"一般条款")

		# PAGE 2 ********************************************
		self.page_2_snr_1 = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200)
		self.page_2_snr_1.pack()

		self.page_2_frame_line_1 = Tkinter.Frame(self.page_2_snr_1,pady = 0)
		self.page_2_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_2_frame_line_2 = Tkinter.Frame(self.page_2_snr_1)
		self.page_2_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_2_frame_line_3 = Tkinter.Frame(self.page_2_snr_1)
		self.page_2_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.snr_1_intrate_label = Tkinter.Label(self.page_2_frame_line_1,text = u'利率(%)',width = 12,relief = 'ridge')
		self.snr_1_intrate_label.pack(side = 'left', anchor = 'nw')
		self.snr_1_intrate_entry = Tkinter.Entry(self.page_2_frame_line_1, width=10)
		self.snr_1_intrate_entry.insert(0,4)
		self.snr_1_intrate_entry.pack(side = 'left', anchor = 'nw')

		self.snr_1_freq_label = Tkinter.Label(self.page_2_frame_line_2,text = u'付息频率',width = 12,relief = 'ridge')
		self.snr_1_freq_label.pack(side = 'left', anchor = 'nw')
		self.snr_1_freq_entry = Tkinter.Entry(self.page_2_frame_line_2, width=10)
		self.snr_1_freq_entry.insert(0,12)
		self.snr_1_freq_entry.pack(side = 'left', anchor = 'nw')

		self.snr_1_advrate_label = Tkinter.Label(self.page_2_frame_line_3,text = u'放款比率(%)',width = 12,relief = 'ridge')
		self.snr_1_advrate_label.pack(side = 'left', anchor = 'nw')
		self.snr_1_advrate_entry = Tkinter.Entry(self.page_2_frame_line_3, width=10)
		self.snr_1_advrate_entry.insert(0,65)
		self.snr_1_advrate_entry.pack(side = 'left', anchor = 'nw')

		self.notebook.add(self.page_2_snr_1,text=u"优先")


		# PAGE 4 ********************************************
		self.page_4_mezz = Tkinter.LabelFrame(self.master_frame,width = 400,height = 200)
		self.page_4_mezz.pack()

		self.page_4_frame_line_1 = Tkinter.Frame(self.page_4_mezz,pady = 0)
		self.page_4_frame_line_1.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_4_frame_line_2 = Tkinter.Frame(self.page_4_mezz)
		self.page_4_frame_line_2.pack(side = 'top',fill = 'x',anchor = 'n')

		self.page_4_frame_line_3 = Tkinter.Frame(self.page_4_mezz)
		self.page_4_frame_line_3.pack(side = 'top',fill = 'x',anchor = 'n')

		self.mezz_intrate_label = Tkinter.Label(self.page_4_frame_line_1,text = u'利率(%)',width = 12,relief = 'ridge')
		self.mezz_intrate_label.pack(side = 'left', anchor = 'nw')
		self.mezz_intrate_entry = Tkinter.Entry(self.page_4_frame_line_1, width=10)
		self.mezz_intrate_entry.insert(0,5)
		self.mezz_intrate_entry.pack(side = 'left', anchor = 'nw')

		self.mezz_freq_label = Tkinter.Label(self.page_4_frame_line_2,text = u'付息频率',width = 12,relief = 'ridge')
		self.mezz_freq_label.pack(side = 'left', anchor = 'nw')
		self.mezz_freq_entry = Tkinter.Entry(self.page_4_frame_line_2, width=10)
		self.mezz_freq_entry.insert(0,12)
		self.mezz_freq_entry.pack(side = 'left', anchor = 'nw')

		self.mezz_advrate_label = Tkinter.Label(self.page_4_frame_line_3,text = u'放款比率(%)',width = 12,relief = 'ridge')
		self.mezz_advrate_label.pack(side = 'left', anchor = 'nw')
		self.mezz_advrate_entry = Tkinter.Entry(self.page_4_frame_line_3, width=10)
		self.mezz_advrate_entry.insert(0,80)
		self.mezz_advrate_entry.pack(side = 'left', anchor = 'nw')

		self.notebook.add(self.page_4_mezz,text=u"夹层")

	def load_struct(self,struct_specs_IN):

		self.upfront_fee_entry.delete(0,'end')
		self.mgmt_fee_entry.delete(0,'end')
		self.mgmt_fee_freq_entry.delete(0,'end')
		self.prin_cf_split_option_combobox.delete(0,'end')
		self.snr_1_intrate_entry.delete(0,'end')
		self.snr_1_freq_entry.delete(0,'end')
		self.snr_1_advrate_entry.delete(0,'end')
		self.mezz_intrate_entry.delete(0,'end')
		self.mezz_freq_entry.delete(0,'end')
		self.mezz_advrate_entry.delete(0,'end')

		self.upfront_fee_entry.insert(0,struct_specs_IN['upfront_fee'])
		self.mgmt_fee_entry.insert(0,struct_specs_IN['mgmt_fee'])
		self.mgmt_fee_freq_entry.insert(0,struct_specs_IN['mgmt_fee_freq'])
		self.prin_cf_split_option_combobox.insert(0,struct_specs_IN['prin_cf_split'])
		self.snr_1_intrate_entry.insert(0,struct_specs_IN['snr_intrate'])
		self.snr_1_freq_entry.insert(0,struct_specs_IN['snr_freq'])
		self.snr_1_advrate_entry.insert(0,struct_specs_IN['snr_advrate'])
		self.mezz_intrate_entry.insert(0,struct_specs_IN['mezz_intrate'])
		self.mezz_freq_entry.insert(0,struct_specs_IN['mezz_freq'])
		self.mezz_advrate_entry.insert(0,struct_specs_IN['mezz_advrate'])

class Securitization_GUI_Mgmt_biblebook(Tkinter.Frame): # a very complicated and generic one
	def __init__(self, master=None, struct_specifics_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.specifics_initialize(struct_specifics_IN = struct_specifics_IN)
		self.struct_display_order = {
									'Senior': 1,
									'Mezz': 2,
									'Resid': 3,
									'Special': 4,
									'Reserve_Account': 5,
									'Fees': 6,
									}

		self.structure_count_limit_dict = {
									'Fees': 1,
									'Senior': 26,
									'Mezz': 26,
									'Resid': 1,
									'Reserve_Account': 1,
									'Special': 5
									}
		self.structure_gui_mappings = {
									'Fees': Vallina_Fees_Element,
									'Senior': Vallina_Senior_Element,
									'Mezz': Vallina_Mezz_Element,
									'Resid': Vallina_Resid_Element,
									'Reserve_Account': Vallina_ReserveAccount_Element,
									'Special': Vallina_Special_Element
									}

		self.structure_count_dict = {
									'Fees': 0,
									'Senior': 0,
									'Mezz': 0,
									'Resid': 0,
									'Reserve_Account': 0,
									'Special': 0
									}
		self.structure_mgmt_dict = {
									'Fees': [],
									'Senior': [],
									'Mezz': [],
									'Resid': [],
									'Reserve_Account': [],
									'Special': []
		}



		self.set_up()
		self.load_struct(struct_specifics_IN)

	def load_struct(self, struct_specifics_IN):
		self.delete_all_tranche()
		self.specifics_initialize(struct_specifics_IN)
		if struct_specifics_IN == None:
			pass
		else:
			for tranche in self.struct_name_specifics.keys():
				for index, tranche_name in enumerate(self.struct_name_specifics[tranche]):
					input_specifics = dict(zip(list(self.struct_input_specifics[tranche].keys()), [values[index] for key, values in self.struct_input_specifics[tranche].iteritems()]))
					self.add_tranche(the_tranche_IN = tranche, tranche_name_IN = tranche_name, input_specifics_IN = input_specifics)

	def specifics_initialize(self, struct_specifics_IN = None):
		if struct_specifics_IN == None:
			self.struct_input_specifics = {	
										'Fees': {},
										'Senior': {},
										'Mezz': {},
										'Resid': {},
										'Reserve_Account': {},
										'Special': {}
									}
			self.struct_name_specifics = {	
										'Fees': [],
										'Senior': [],
										'Mezz': [],
										'Resid': [],
										'Reserve_Account': [],
										'Special': []
									}
		else:
			self.struct_input_specifics = struct_specifics_IN['input_specifics']
			self.struct_name_specifics = struct_specifics_IN['name_specifics']

		self.struct_specifics = {"input_specifics" : self.struct_input_specifics, "name_specifics" : self.struct_name_specifics}


	def get(self):
		self.specifics_initialize()

		instance_specifics = None
		for key, value in self.structure_mgmt_dict.iteritems():
			for dict_trancheName_trancheInstance in value:
				for trancheName, trancheInstance in dict_trancheName_trancheInstance.iteritems():
					self.struct_name_specifics[key].append(trancheName)
					instance_specifics = trancheInstance.get()
					for each_term_key, each_term_value in instance_specifics.iteritems():
						if each_term_key not in self.struct_input_specifics[key]:
							self.struct_input_specifics[key].update({each_term_key : [each_term_value]})
						else:
							self.struct_input_specifics[key][each_term_key].append(each_term_value)
		self.struct_specifics = {"input_specifics" : self.struct_input_specifics, "name_specifics" : self.struct_name_specifics}

	def set_up(self):
		self.line_1_frame = Tkinter.Frame(self)
		self.line_1_frame.pack(expand=1, fill="both", side = 'top')

		self.line_2_frame = Tkinter.Frame(self)
		self.line_2_frame.pack(expand=1, fill="both", side = 'top')

		self.structure_notebook = ttk.Notebook(self.line_2_frame)
		self.structure_notebook.pack()

		self.add_tranche_button = Tkinter.Button(self.line_1_frame, text = "Add Tranche", command = self.add_tranche)
		self.add_tranche_button.pack(side = 'left')

		self.delete_tranche_button = Tkinter.Button(self.line_1_frame, text = "Delete Current Tranche", command = self.delete_tranche)
		self.delete_tranche_button.pack(side = 'left')

		self.tranche_option_list = list(self.structure_count_dict.keys())
		self.tranche_option_list.sort(key=self.struct_display_order.get)
		self.tranche_option_strVar = Tkinter.StringVar(self.line_1_frame)
		self.tranche_option = apply(Tkinter.OptionMenu, (self.line_1_frame, self.tranche_option_strVar) + tuple(self.tranche_option_list))
		self.tranche_option_strVar.set(self.tranche_option_list[0])

		self.tranche_option.pack(side = 'left')
		

	def determine_tranche_name(self, tranche_IN):
		if self.structure_count_dict[tranche_IN] <  self.structure_count_limit_dict[tranche_IN]:
			if self.structure_count_limit_dict[tranche_IN] == 1:
				tranche_name = tranche_IN
			else:
				chr_count = 65
				while (tranche_IN + "_" + chr(chr_count + self.structure_count_dict[tranche_IN])) in [dict_item.keys()[0] for dict_item in self.structure_mgmt_dict[tranche_IN]]:
					chr_count += 1
				tranche_name = tranche_IN + "_" + chr(chr_count + self.structure_count_dict[tranche_IN])
		else:
			tranche_name = None

		return tranche_name

	def add_tranche(self, the_tranche_IN = None, tranche_name_IN = None, input_specifics_IN = {}):
		if the_tranche_IN == None and tranche_name_IN == None and input_specifics_IN == {}:
			the_tranche = self.tranche_option_strVar.get()
			tranche_name = self.determine_tranche_name(the_tranche)
			input_specifics = {}
		else:
			the_tranche = the_tranche_IN
			tranche_name = tranche_name_IN
			input_specifics = input_specifics_IN			
		
		if tranche_name == None:
			pass
		else:
			new_frame = Tkinter.Frame(self.line_2_frame)
			self.structure_notebook.add(new_frame, text = tranche_name)
			tranche_instance = self.structure_gui_mappings[the_tranche](new_frame, input_specifics)
			self.structure_notebook.select(new_frame)
			tranche_instance.set_up()
			self.structure_mgmt_dict[the_tranche].append({tranche_name : tranche_instance})
			self.structure_count_dict[the_tranche] += 1
		return

	def delete_tranche(self, to_be_deleted_IN = None):
		if to_be_deleted_IN == None:
			to_be_deleted = self.structure_notebook.tab(self.structure_notebook.select(), 'text')
			index = self.structure_notebook.index(self.structure_notebook.select())			
		else:
			to_be_deleted = to_be_deleted_IN
			index = [self.structure_notebook.tab(each_tab, 'text') for each_tab in self.structure_notebook.tabs()].index(to_be_deleted)

		self.structure_notebook.forget(index)

		for tranche_name, sub_tranche_list in self.structure_mgmt_dict.iteritems():
			for sub_tranche_index, sub_tranche in enumerate(sub_tranche_list):
				if sub_tranche.keys()[0] == to_be_deleted:
					self.structure_mgmt_dict[tranche_name].pop(sub_tranche_index)
					self.structure_count_dict[tranche_name] -= 1

	def delete_all_tranche(self):
		for to_be_deleted_IN in [self.structure_notebook.tab(tab_id,'text') for tab_id in self.structure_notebook.tabs()]:
			self.delete_tranche(to_be_deleted_IN)



class Vallina_Fees_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.parameter_initialize()
		self.pack()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) >0:
			self.servicingfee = self.specs['Servicing_Fee']
			self.servicingfee_type = self.specs['Servicing_Fee_Paytype']
			self.diligencefee = self.specs['Duediligence_Fee']
			self.diligencefee_type = self.specs['Duediligence_Fee_Paytype']
		else:
			self.servicingfee = 0
			self.servicingfee_type = 'Upfront'
			self.diligencefee = 0
			self.diligencefee_type = 'Upfront'

	def set_up(self):
		self.servicingfee_label = Tkinter.Label(self, text = "Servicing Fees")
		self.servicingfee_label.grid(row = 0, column = 0)

		self.servicingfee_entry = Tkinter.Entry(self, width=10)
		self.servicingfee_entry.grid(row = 0, column = 1)
		self.servicingfee_entry.insert(0,self.servicingfee)

		self.servicingfee_option_list = ["Upfront", "Monthly"]
		self.servicingfee_option_strVar = Tkinter.StringVar(self)
		self.servicingfee_option_strVar.set(self.servicingfee_type)
		self.servicingfee_option = apply(Tkinter.OptionMenu, (self, self.servicingfee_option_strVar) + tuple(self.servicingfee_option_list))
		self.servicingfee_option.grid(row = 0, column = 2)

		self.diligencefee_label = Tkinter.Label(self, text = "Diligence Fees")
		self.diligencefee_label.grid(row = 1, column = 0)

		self.diligencefee_entry = Tkinter.Entry(self, width=10)
		self.diligencefee_entry.grid(row = 1, column = 1)
		self.diligencefee_entry.insert(0, self.diligencefee)

		self.diligencefee_option_list = ["Upfront", "Monthly"]
		self.diligencefee_option_strVar = Tkinter.StringVar(self)
		self.diligencefee_option_strVar.set(self.diligencefee_type)
		self.diligencefee_option = apply(Tkinter.OptionMenu, (self, self.diligencefee_option_strVar) + tuple(self.diligencefee_option_list))
		self.diligencefee_option.grid(row = 1, column = 2)

	def get(self):
		self.specs = {}
		self.specs.update({"Servicing_Fee" : float(self.servicingfee_entry.get())})
		self.specs.update({"Servicing_Fee_Paytype" : self.servicingfee_option_strVar.get()})
		self.specs.update({"Duediligence_Fee" : float(self.diligencefee_entry.get())})
		self.specs.update({"Duediligence_Fee_Paytype" : self.diligencefee_option_strVar.get()})
		return self.specs.copy()


class Vallina_Senior_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.pack()
		self.parameter_initialize()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) > 0:
			self.advrate = self.specs['Adv']
			self.intrate = self.specs['Rate']
			self.freq = self.specs['Frequency']
			self.scheduletype = self.specs['scheduleType']
		else:
			self.advrate = 0.50686
			self.intrate = 0.0500
			self.freq = 1
			self.scheduletype = 'IO'

	def set_up(self):
		self.advrate_label = Tkinter.Label(self, text = "Adv Rate")
		self.advrate_label.grid(row = 0, column = 0)

		self.advrate_entry = Tkinter.Entry(self, width=10)
		self.advrate_entry.grid(row = 0, column = 1)
		self.advrate_entry.insert(0,self.advrate * 100)

		self.intrate_label = Tkinter.Label(self, text = "Int Rate")
		self.intrate_label.grid(row = 1, column = 0)

		self.intrate_entry = Tkinter.Entry(self, width=10)
		self.intrate_entry.grid(row = 1, column = 1)
		self.intrate_entry.insert(0, self.intrate * 100)

		self.freq_label = Tkinter.Label(self, text = "Frequency")
		self.freq_label.grid(row = 2, column = 0)

		self.freq_entry = Tkinter.Entry(self, width=10)
		self.freq_entry.grid(row = 2, column = 1)
		self.freq_entry.insert(0,self.freq)

		self.scheduletype_label = Tkinter.Label(self, text = "Schedule Type")
		self.scheduletype_label.grid(row = 3, column = 0)

		self.scheduletype_option_list = ['Bullet', 'IO', 'Waterfall', 'Amortized']
		self.scheduletype_strVar = Tkinter.StringVar(self)
		self.scheduletype_strVar.set(self.scheduletype)
		self.scheduletype_option = apply(Tkinter.OptionMenu, (self, self.scheduletype_strVar) + tuple(self.scheduletype_option_list))
		self.scheduletype_option.grid(row = 3, column = 1)

	def get(self):
		self.specs = {}
		self.specs.update({'Adv' : float(self.advrate_entry.get())/100.0})
		self.specs.update({'Rate' : float(self.intrate_entry.get())/100.0})
		self.specs.update({'scheduleType' : self.scheduletype_strVar.get()})
		self.specs.update({'Frequency' : float(self.freq_entry.get())})
		return self.specs.copy()


class Vallina_Mezz_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.pack()
		self.parameter_initialize()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) > 0:
			self.advrate = self.specs['Adv']
			self.intrate = self.specs['Rate']
			self.freq = self.specs['Frequency']
			self.scheduletype = self.specs['scheduleType']
		else:
			self.advrate = 0.50686
			self.intrate = 0.0500
			self.freq = 1
			self.scheduletype = 'IO'

	def set_up(self):
		self.advrate_label = Tkinter.Label(self, text = "Adv Rate")
		self.advrate_label.grid(row = 0, column = 0)

		self.advrate_entry = Tkinter.Entry(self, width=10)
		self.advrate_entry.grid(row = 0, column = 1)
		self.advrate_entry.insert(0,self.advrate * 100)

		self.intrate_label = Tkinter.Label(self, text = "Int Rate")
		self.intrate_label.grid(row = 1, column = 0)

		self.intrate_entry = Tkinter.Entry(self, width=10)
		self.intrate_entry.grid(row = 1, column = 1)
		self.intrate_entry.insert(0, self.intrate * 100)

		self.freq_label = Tkinter.Label(self, text = "Frequency")
		self.freq_label.grid(row = 2, column = 0)

		self.freq_entry = Tkinter.Entry(self, width=10)
		self.freq_entry.grid(row = 2, column = 1)
		self.freq_entry.insert(0,self.freq)

		self.scheduletype_label = Tkinter.Label(self, text = "Schedule Type")
		self.scheduletype_label.grid(row = 3, column = 0)

		self.scheduletype_option_list = ['Bullet', 'IO', 'Waterfall', 'Amortized']
		self.scheduletype_strVar = Tkinter.StringVar(self)
		self.scheduletype_strVar.set(self.scheduletype)
		self.scheduletype_option = apply(Tkinter.OptionMenu, (self, self.scheduletype_strVar) + tuple(self.scheduletype_option_list))
		self.scheduletype_option.grid(row = 3, column = 1)

	def get(self):
		self.specs = {}
		self.specs.update({'Adv' : float(self.advrate_entry.get())/100.0})
		self.specs.update({'Rate' : float(self.intrate_entry.get())/100.0})
		self.specs.update({'scheduleType' : self.scheduletype_strVar.get()})
		self.specs.update({'Frequency' : float(self.freq_entry.get())})
		return self.specs.copy()


class Vallina_Special_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.pack()
		self.parameter_initialize()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) > 0:
			self.portion = self.specs['Portion']
			self.intrate = self.specs['Rate']
			self.freq = self.specs['Frequency']
			self.scheduletype = self.specs['scheduleType']
		else:
			self.portion = 0.02166
			self.intrate = 0.0300
			self.freq = 2
			self.scheduletype = 'Waterfall'

	def set_up(self):
		self.portion_label = Tkinter.Label(self, text = "Portion")
		self.portion_label.grid(row = 0, column = 0)

		self.portion_entry = Tkinter.Entry(self, width=10)
		self.portion_entry.grid(row = 0, column = 1)
		self.portion_entry.insert(0,self.portion * 100)

		self.intrate_label = Tkinter.Label(self, text = "Int Rate")
		self.intrate_label.grid(row = 1, column = 0)

		self.intrate_entry = Tkinter.Entry(self, width=10)
		self.intrate_entry.grid(row = 1, column = 1)
		self.intrate_entry.insert(0, self.intrate * 100)

		self.freq_label = Tkinter.Label(self, text = "Frequency")
		self.freq_label.grid(row = 2, column = 0)

		self.freq_entry = Tkinter.Entry(self, width=10)
		self.freq_entry.grid(row = 2, column = 1)
		self.freq_entry.insert(0,self.freq)

		self.scheduletype_label = Tkinter.Label(self, text = "Schedule Type")
		self.scheduletype_label.grid(row = 3, column = 0)

		self.scheduletype_option_list = ['Bullet', 'IO', 'Waterfall', 'Amortized']
		self.scheduletype_option_strVar = Tkinter.StringVar(self)
		self.scheduletype_option_strVar.set(self.scheduletype)
		self.scheduletype_option = apply(Tkinter.OptionMenu, (self, self.scheduletype_option_strVar) + tuple(self.scheduletype_option_list))
		self.scheduletype_option.grid(row = 3, column = 1)		


	def get(self):
		self.specs = {}
		self.specs.update({'Portion' : float(self.portion_entry.get())/100.0})
		self.specs.update({'Rate' : float(self.intrate_entry.get())/100.0})
		self.specs.update({'scheduleType' : self.scheduletype_option_strVar.get()})
		self.specs.update({'Frequency' : float(self.freq_entry.get())})
		return self.specs.copy()

class Vallina_ReserveAccount_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.pack()
		self.parameter_initialize()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) > 0:
			self.fromfundings = self.specs['fundings']
			self.fromassetcf = self.specs['assetcf']
			self.assetcfcutperiod = self.specs['assetcf_timecut']
		else:
			self.fromfundings = 35 * 1e6
			self.fromassetcf = 75 * 1e6
			self.assetcfcutperiod = 12

	def set_up(self):
		self.fromfundings_label = Tkinter.Label(self, text = "From Fundings (Million)")
		self.fromfundings_label.grid(row = 0, column = 0)

		self.fromfundings_entry = Tkinter.Entry(self, width=10)
		self.fromfundings_entry.grid(row = 0, column = 1)
		self.fromfundings_entry.insert(0, self.fromfundings/1e6)

		self.fromassetcf_label = Tkinter.Label(self, text = "From Asset CF (Million)")
		self.fromassetcf_label.grid(row = 1, column = 0)

		self.fromassetcf_entry = Tkinter.Entry(self, width=10)
		self.fromassetcf_entry.grid(row = 1, column = 1)
		self.fromassetcf_entry.insert(0, self.fromassetcf/1e6)

		self.assetcfcutperiod_label = Tkinter.Label(self, text = "Asset CF Cut Period")
		self.assetcfcutperiod_label.grid(row = 2, column = 0)

		self.assetcfcutperiod_entry = Tkinter.Entry(self, width=10)
		self.assetcfcutperiod_entry.grid(row = 2, column = 1)
		self.assetcfcutperiod_entry.insert(0, self.assetcfcutperiod)

	def get(self):
		self.specs= {}
		self.specs.update({'fundings' : float(self.fromfundings_entry.get()) * 1e6})
		self.specs.update({'assetcf' : float(self.fromassetcf_entry.get()) * 1e6})
		self.specs.update({'assetcf_timecut' : float(self.assetcfcutperiod_entry.get())})
		return self.specs.copy()

class Vallina_Resid_Element(Tkinter.Frame):
	def __init__(self, master=None, input_specifics_IN = {}):
		Tkinter.Frame.__init__(self, master)
		self.specs = input_specifics_IN
		self.parameter_initialize()
		self.pack()
		self.set_up()

	def parameter_initialize(self):
		if len(self.specs) > 0:
			self.intrate = self.specs['Rate']
			self.scheduletype = self.specs['scheduleType']
			self.freq = self.specs['Frequency']
		else:
			self.intrate = 0
			self.scheduletype = 'IO'
			self.freq = 1

	def set_up(self):
		self.scheduletype_label = Tkinter.Label(self, text = "Schedule Type")
		self.scheduletype_label.grid(row = 0, column = 0)

		self.scheduletype_option_list = ['Bullet', 'IO', 'Waterfall', 'Amortized']
		self.scheduletype_option_strVar = Tkinter.StringVar(self)
		self.scheduletype_option_strVar.set(self.scheduletype)
		self.scheduletype_option = apply(Tkinter.OptionMenu, (self, self.scheduletype_option_strVar) + tuple(self.scheduletype_option_list))
		self.scheduletype_option.grid(row = 0, column = 1)

		self.freq_label = Tkinter.Label(self, text = "Frequency")
		self.freq_label.grid(row = 1, column = 0)

		self.freq_entry = Tkinter.Entry(self, width=10)
		self.freq_entry.grid(row = 1, column = 1)
		self.freq_entry.insert(0, self.freq)

	def get(self):
		self.specs = {}
		self.specs.update({'Rate' : 0.00})
		self.specs.update({'scheduleType' : self.scheduletype_option_strVar.get()})
		self.specs.update({'Frequency' : float(self.freq_entry.get())})
		return self.specs.copy()

def main():
	print 1
if __name__ == "__main__":
	main()