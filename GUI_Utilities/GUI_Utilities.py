# -*- coding: utf-8 -*-
import pandas as pd
import Tkinter as Tkinter
import ttk as ttk
from datetime import datetime
import os
import locale
import sys
from Config import Config
import numpy as np
import matplotlib
import pylab
import pygtk
import string
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# *****************************************************
# commeng by Hong Fan
# *****************************************************
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

from IO_Utilities import IO_Utilities

Formatter_pct2 = lambda x: "{:.2%}".format(x)
Formatter_pct1 = lambda x: "{:.1%}".format(x)
Formatter_pct0 = lambda x: "{:.0%}".format(x)

Formatter_dec2 = lambda x: '{0:,.2f}'.format(x)
Formatter_dec1 = lambda x: '{0:,.1f}'.format(x)
Formatter_dec0 = lambda x: '{0:,.0f}'.format(x)

class Treeview_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, df_IN = pd.DataFrame()):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.frame = Tkinter.Frame(self)
		self.frame.pack()
 
		f = ttk.Frame(self.frame)
		f.pack(side='top', fill='both', expand='y')

		self.tree = ttk.Treeview(columns=tuple(df_IN.columns))

		ysb = ttk.Scrollbar(orient='vertical', command= self.tree.yview)
		xsb = ttk.Scrollbar(orient='horizontal', command= self.tree.xview)
		self.tree['yscroll'] = ysb.set
		self.tree['xscroll'] = xsb.set

		for item in self.tree.get_children(): self.tree.delete(item)
		# self.tree.heading('#0',         text='Index',           anchor='e')
		self.tree.heading('#0',         text='索引',           anchor='e')
		self.tree.column('#0',         stretch=0, width=40 , anchor='e')

		for col in list(df_IN.columns):
			# be careful with chinese character
			# self.tree.heading(col,text=str(col))
			self.tree.heading(col,text=col)
			if col == u'创立时间':
				self.tree.column(col, stretch=0, width=150)
			else:
				self.tree.column(col, stretch=0, width=70)

		#Populate data in the treeview
		for index,row in df_IN.iterrows(): self.tree.insert('', 'end',text=index, values = tuple(row[0:]))

		# add tree and scrollbars to frame
		self.tree.grid(in_=f, row=0, column=0, sticky='nsew')
		ysb.grid(in_=f, row=0, column=1, sticky='ns')
		xsb.grid(in_=f, row=1, column=0, sticky='ew')

		# set frame resizing priorities
		f.rowconfigure(0, weight=1)
		f.columnconfigure(0, weight=1)
	
	def update_dataframe(self,df_IN):
		for item in self.tree.get_children(): self.tree.delete(item)
		for index,row in df_IN.iterrows(): self.tree.insert('', 'end',text=index, values = tuple(row[0:]))

class TextBoxGroup_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, num_of_box_IN = 3,width_IN = 9):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.num_of_box = num_of_box_IN
		self.frame = Tkinter.Frame(self)
		self.frame.pack()

		self.nodes = {}
		for i in range(0,self.num_of_box):
			temp_node = Tkinter.Entry(self.frame, width = width_IN)
			temp_node.grid(row = 0, column = i)
			self.nodes[i] = temp_node

	def get(self, node_num):
		return self.nodes[node_num].get()

	def get_all(self):
		res = [self.nodes[i].get() for i in range(0,self.num_of_box)]

	def load_settings(self, settings_to_be_loaded):
		for i in range(0,self.num_of_box):
			temp_node = self.nodes[i]
			temp_node.delete("1.0",'end')
			temp_node.insert('end',settings_to_be_loaded[i])


class ComboBoxGroup_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, num_of_box_IN = 3,width_IN = 9,combo_box_values_list_IN = None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.frame = Tkinter.Frame(self)
		self.frame.pack()
		self.num_of_box = num_of_box_IN

		if combo_box_values_list_IN is None:
			self.combo_box_values_list = [[]] * self.num_of_box 
		else:
			self.combo_box_values_list = combo_box_values_list_IN

		self.nodes = {}
		for i in range(0,self.num_of_box):
			temp_strvar = Tkinter.StringVar()
			temp_node = ttk.Combobox(self.frame, textvariable = temp_strvar,width = width_IN)
			temp_node['values'] = self.combo_box_values_list[i]
			temp_node.grid(row = 0, column = i)
			self.nodes[i] = temp_node

	def get(self,node_num):
		return self.nodes[node_num].get()

	def reload_combobox_values_list(self,combo_box_values_list_IN):
		self.combo_box_values_list = combo_box_values_list_IN
		for i in range(0,self.num_of_box):
			temp_node = self.nodes[i]
			temp_node['values'] = self.combo_box_values_list[i]

	def load_settings(self, settings_to_be_loaded):
		for i in range(0,self.num_of_box):
			temp_node = self.nodes[i]
			temp_node.set(settings_to_be_loaded[i])

	def get_all(self):
		res = [self.nodes[i].get() for i in range(0,self.num_of_box)]



class ConditionGroup_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, title_list_IN = ["Column1","Column2","Column3"],
		add_condition_button_text_IN = u'添加条件',delete_condition_button_text_IN = u'删除条件',
		BoxGroup_width_IN = 11, style_IN = 'TextBox', Label_width_IN = 11, combo_box_values_list_IN = None):

		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack()

		self.title_list = title_list_IN
		self.col_num = len(self.title_list)
		self.combo_box_values_list = combo_box_values_list_IN

		self.button_frame = Tkinter.Frame(self.frame)
		self.button_frame.pack(expand = 1, fill="both")

		self.style = style_IN

		self.BoxGroup_width = BoxGroup_width_IN
		self.Label_width = Label_width_IN

		self.add_condition_button = Tkinter.Button(self.button_frame, text = add_condition_button_text_IN,command = self.add_condition,width = 12)
		self.add_condition_button.pack(side = 'left')

		self.delete_condition_button = Tkinter.Button(self.button_frame, text = delete_condition_button_text_IN,
			command = lambda : self.delete_condition(max(list(self.conditions_dict.keys())),True),width = 12)
		self.delete_condition_button.pack(side = 'left')

		self.title_frame = Tkinter.Frame(self.frame)
		self.title_frame.pack(expand = 1, fill="both")

		self.labels_dict = {}
		for i in range(1,self.col_num + 1):
			self.labels_dict[i] = Tkinter.Label(self.title_frame,text = self.title_list[i-1], width = self.Label_width)
			self.labels_dict[i].grid(row = 0, column = i-1)
		
		temp_line_name = str(datetime.now()) + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		
		self.conditions_dict = {}
		self.conditions_dict[temp_line_name] = [None,None, None,None,None]
		
		self.conditions_dict[temp_line_name][0] = Tkinter.Frame(self.frame)
		self.conditions_dict[temp_line_name][0].pack(side = 'top',expand = 1, fill="both")

		self.conditions_dict[temp_line_name][1] = Tkinter.Frame(self.conditions_dict[temp_line_name][0])
		self.conditions_dict[temp_line_name][1].pack(side = 'left',expand = 1, fill="both")

		if self.style == 'TextBox':
			self.conditions_dict[temp_line_name][2] = TextBoxGroup_Mgmt(self.conditions_dict[temp_line_name][1],num_of_box_IN = self.col_num,
				width_IN = self.BoxGroup_width)
		elif self.style == 'ComboBox':
			self.conditions_dict[temp_line_name][2] = ComboBoxGroup_Mgmt(self.conditions_dict[temp_line_name][1],num_of_box_IN = self.col_num,
				width_IN = self.BoxGroup_width, combo_box_values_list_IN = self.combo_box_values_list)

		self.conditions_dict[temp_line_name][2].pack()

		self.conditions_dict[temp_line_name][3] = Tkinter.Frame(self.conditions_dict[temp_line_name][0])
		self.conditions_dict[temp_line_name][3].pack(side = 'left',expand = 1, fill="both")

		self.conditions_dict[temp_line_name][4] = Tkinter.Button(self.conditions_dict[temp_line_name][3], text = u"x",
			command = lambda : self.delete_condition(self.conditions_dict[temp_line_name][4]),bg = 'red')
		self.conditions_dict[temp_line_name][4].pack()

		self.condition_num = len(self.conditions_dict)

	def add_condition(self):
		
		temp_line_name = str(datetime.now()) + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		
		self.conditions_dict[temp_line_name] = [None,None,None,None,None]

		self.conditions_dict[temp_line_name][0] = Tkinter.Frame(self.frame)
		self.conditions_dict[temp_line_name][0].pack(side = 'top',expand = 1, fill="both")

		self.conditions_dict[temp_line_name][1] = Tkinter.Frame(self.conditions_dict[temp_line_name][0])
		self.conditions_dict[temp_line_name][1].pack(side = 'left',expand = 1, fill="both")

		self.conditions_dict[temp_line_name][3] = Tkinter.Frame(self.conditions_dict[temp_line_name][0])
		self.conditions_dict[temp_line_name][3].pack(side = 'left',expand = 1, fill="both")

		if self.style == 'TextBox':
			self.conditions_dict[temp_line_name][2] = TextBoxGroup_Mgmt(self.conditions_dict[temp_line_name][1],num_of_box_IN = self.col_num,
				width_IN = self.BoxGroup_width)
		elif self.style == 'ComboBox':
			self.conditions_dict[temp_line_name][2] = ComboBoxGroup_Mgmt(self.conditions_dict[temp_line_name][1],num_of_box_IN = self.col_num,
				width_IN = self.BoxGroup_width,combo_box_values_list_IN = self.combo_box_values_list)
		
		self.conditions_dict[temp_line_name][2].pack()

		self.conditions_dict[temp_line_name][4] = Tkinter.Button(self.conditions_dict[temp_line_name][3], text = u"x", command = lambda : self.delete_condition(self.conditions_dict[temp_line_name][4]),bg = 'red')
		self.conditions_dict[temp_line_name][4].pack()

		self.condition_num = len(self.conditions_dict)

	def delete_condition(self,widget_ref,using_key_IN = False):
		if using_key_IN:
			found_key = widget_ref
		else:
			found_key = None
			for key,value in self.conditions_dict.items():
				if value[4] == widget_ref:
					found_key = key

		self.conditions_dict[found_key][0].destroy()
		self.conditions_dict[found_key][1].destroy()
		self.conditions_dict[found_key][2].destroy()
		self.conditions_dict[found_key][3].destroy()
		self.conditions_dict[found_key][4].destroy()

		self.conditions_dict.pop(found_key,None)
		self.condition_num = len(self.conditions_dict)

	def reload_combo_box_values_list(self,combo_box_values_list_IN):
		self.combo_box_values_list = combo_box_values_list_IN
		for key,value in self.conditions_dict.items():
			value[2].reload_combobox_values_list(self.combo_box_values_list)
	
	def get_all(self,dict_type = False):
		all_keys = self.conditions_dict.keys()
		all_keys.sort()
		if dict_type:
			self.res = []
			for i in range(0,self.condition_num):
				found_key = all_keys[i]
				temp = {}
				for j in range(0,self.conditions_dict[found_key][2].num_of_box):
					temp[self.title_list[j]] = self.conditions_dict[found_key][2].get(j)
				self.res.append(temp)
		else:
			self.res = {}
			for i in range(0,self.condition_num):
				temp = []
				found_key = all_keys[i]
				for j in range(0,self.conditions_dict[found_key][2].num_of_box):
					temp.append(self.conditions_dict[found_key][2].get(j))
				self.res[i] = temp

	def load_settings(self,settings_to_be_loaded):
		# delete existing settings
		while self.condition_num>0:
			self.delete_condition(max(list(self.conditions_dict.keys())),True)

		# load settings
		for idx,row in settings_to_be_loaded.iterrows():
			self.add_condition()
			self.conditions_dict[max(list(self.conditions_dict.keys()))][2].load_settings(list(row))




class DisplayTable_Mgmt(Tkinter.Frame):
	def __init__(self, master=None, df_IN = pd.DataFrame(), formatting_mapper_IN = None, horizontal_mapper = True,index_col_width_IN = 16,contents_col_width_IN = 12, index_col_grouping_num_IN = 1,index_col_color_IN = 'yellow'):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack()

		self.df = df_IN
		self.formatting_mapper = formatting_mapper_IN
		self.index_col_width = index_col_width_IN
		self.contents_col_width = contents_col_width_IN
		self.index_col_grouping_num = index_col_grouping_num_IN
		self.index_col_color = index_col_color_IN
		self.node_dict = {}
		self.horizontal_mapper = horizontal_mapper
		self.setup()


	def setup(self):
		r0_c0_node = Tkinter.Label(self.frame, width=self.index_col_width, text="")
		r0_c0_node.grid(row = 0, column = 0)

		self.node_dict[(0,0)] = r0_c0_node
		row_switch = False
		j = 1
		for col_name in self.df.columns.values:
			new_node = Tkinter.Label(self.frame, width=(self.index_col_width if j == 0 else self.contents_col_width), text = col_name,relief = 'ridge',background = Config.Orcas_blue)
			new_node.grid(row = 0, column = j,sticky="nsew", padx=1, pady=1)
			self.node_dict[(0,j)] = new_node
			j += 1

		i = 1
		for idx,row in self.df.iterrows():
			bg_color = Config.Orcas_grey if row_switch else Config.Orcas_snow
			j = 0
			if self.index_col_grouping_num == 1:
				new_node = Tkinter.Label(self.frame, width=(self.index_col_width if j == 0 else self.contents_col_width), text = idx,relief = 'ridge',background = bg_color)
				new_node.grid(row = i, column = j,sticky="nsew",padx=1, pady=1,rowspan = 1)
				self.node_dict[(i,j)] = new_node
			elif self.index_col_grouping_num > 1:
				new_node = Tkinter.Label(self.frame, width=self.index_col_width, text = idx, relief = 'ridge',background = self.index_col_color)
				if i in range(1,len(self.df),self.index_col_grouping_num):
					new_node.grid(row = i, column = j,sticky="nsew",padx=1, pady=1,rowspan = self.index_col_grouping_num)
					self.node_dict[(i,j)] = new_node

			j += 1
			for item in row:
				if self.horizontal_mapper:
					new_node = Tkinter.Label(self.frame, width=(self.index_col_width if j == 0 else self.contents_col_width), text = self.formatting_mapper[idx](row[j-1]),relief = 'ridge',background = bg_color)
				elif self.horizontal_mapper == False:
					new_node = Tkinter.Label(self.frame, width=(self.index_col_width if j == 0 else self.contents_col_width), text = self.formatting_mapper[row.index[j-1]](row[j-1]),relief = 'ridge',background = bg_color)

				new_node.grid(row = i, column = j,sticky="nsew",padx=1, pady=1)
				self.node_dict[(i,j)] = new_node
				j += 1

			i += 1
			row_switch = not(row_switch)


class Display_Unlevered_Econ_Cashflow_Mgmt(Tkinter.Frame):
	def __init__(self, master, run_num_list_IN = [], cashflow_df_list_IN = [],open_in_html_bool_IN = True):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack(side = 'top')

		self.notebook = ttk.Notebook(self.frame)
		self.notebook.pack()

		self.page_frame_holder = []
		self.treeview_gui_mgmt_holder = []

		self.run_num_list = run_num_list_IN
		self.cashflow_df_list = cashflow_df_list_IN

		self.open_in_html_bool = open_in_html_bool_IN

		self.length = len(self.run_num_list)

		self.setup()

	def setup(self):
		for idx,item in enumerate(self.run_num_list):
			self.page_frame_holder.append(Tkinter.Frame(self.frame))
			self.page_frame_holder[-1].pack(side = 'top')
			self.notebook.add(self.page_frame_holder[idx], text = "Run - " + str(item))
			temp = Treeview_Mgmt(master = self.page_frame_holder[-1], df_IN = self.cashflow_df_list[idx])
			self.treeview_gui_mgmt_holder.append(temp)

			if self.open_in_html_bool:
				IO_Utilities.IO_Util.open_in_html(self.cashflow_df_list[idx])


class Display_LeveredEconomics_Charts_Mgmt_OrcasFormat(Tkinter.Frame):
	def __init__(self, master, financing_mgmt_instance_IN):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack(side = 'top')

		self.financing_mgmt_instance = financing_mgmt_instance_IN
		self.data_setup()
		self.widget_setup()

	def data_setup(self):
		# First Financing ******************************
		self.first_financing_period = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['period'])

		self.first_financing_bal_snr = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['SNR_eop_bal'])
		self.first_financing_bal_mezz = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['MEZZ_eop_bal']) + self.first_financing_bal_snr
		self.first_financing_bal_resid = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['RESID_eop_bal']) + self.first_financing_bal_mezz
		self.first_financing_bal_asset = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['ASSET_eop_bal'])

		self.first_financing_cf_snr = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['SNR_total_cf'])
		self.first_financing_cf_mezz = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['MEZZ_total_cf']) + self.first_financing_cf_snr
		self.first_financing_cf_resid = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['RESID_total_cf']) + self.first_financing_cf_mezz
		self.first_financing_cf_asset = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['ASSET_total_cf'])

		self.first_financing_adv_snr = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['SNR_effective_adv_rate'])
		self.first_financing_adv_mezz = np.array(self.financing_mgmt_instance.first_financing_mgmt.asset_liability_res_df['MEZZ_effective_adv_rate'])

		# Second Financing ******************************
		self.second_financing_period = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['period'])

		self.second_financing_bal_snr = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['SNR_eop_bal'])
		self.second_financing_bal_mezz = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['MEZZ_eop_bal']) + self.second_financing_bal_snr
		self.second_financing_bal_resid = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['RESID_eop_bal']) + self.second_financing_bal_mezz
		self.second_financing_bal_asset = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['ASSET_eop_bal'])

		self.second_financing_cf_snr = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['SNR_total_cf'])
		self.second_financing_cf_mezz = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['MEZZ_total_cf']) + self.second_financing_cf_snr
		self.second_financing_cf_resid = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['RESID_total_cf']) + self.second_financing_cf_mezz
		self.second_financing_cf_asset = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['ASSET_total_cf'])

		self.second_financing_adv_snr = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['SNR_effective_adv_rate'])
		self.second_financing_adv_mezz = np.array(self.financing_mgmt_instance.second_financing_mgmt.asset_liability_res_df['MEZZ_effective_adv_rate'])		

	def widget_setup(self):
		fig = Figure(figsize = (7,7))
		rect = fig.patch
		rect.set_facecolor(Config.Orcas_grey)


		# ---------------------------------------------------------------------------------------- #
		ax7 = fig.add_subplot(337)
		ax4 = fig.add_subplot(334,sharex=ax7)
		ax1 = fig.add_subplot(331,sharex=ax7)
		
		ax1.set_title('Balance',fontsize = 8)
		ax4.set_title('Cashflow',fontsize = 8)
		ax7.set_title('Adv Rate',fontsize = 8)


		ax1.fill_between(self.first_financing_period, 0, self.first_financing_bal_snr,color = '#%02x%02x%02x' % (8, 142, 139),label='Snr Bal')
		ax1.fill_between(self.first_financing_period, self.first_financing_bal_snr,self.first_financing_bal_mezz,color = '#%02x%02x%02x' % (10, 186, 181),label='Mezz Bal')
		ax1.fill_between(self.first_financing_period, self.first_financing_bal_mezz, self.first_financing_bal_resid,color = '#%02x%02x%02x' % (13, 237, 232),label='Resid Bal')
		ax1.plot(self.first_financing_period, self.first_financing_bal_asset, "-",color = 'black',linewidth = 1,label='Asset Bal')
		ax1.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax1.get_xticklabels(), visible=False)

		ax4.fill_between(self.first_financing_period, 0, self.first_financing_cf_snr,color = '#%02x%02x%02x' % (8, 142, 139),label='Snr CF')
		ax4.fill_between(self.first_financing_period, self.first_financing_cf_snr, self.first_financing_cf_mezz,color = '#%02x%02x%02x' % (10, 186, 181),label='Mezz CF')
		ax4.fill_between(self.first_financing_period, self.first_financing_cf_mezz, self.first_financing_cf_resid,color = '#%02x%02x%02x' % (13, 237, 232),label='Resid CF')
		ax4.plot(self.first_financing_period, self.first_financing_cf_asset, "-",color = 'black',linewidth = 1,label='Asset CF')
		ax4.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax4.get_xticklabels(), visible=False)

		ax7.plot(self.first_financing_period, self.first_financing_adv_snr, "-",color = 'blue',linewidth = 1,label='Snr Adv')
		ax7.plot(self.first_financing_period, self.first_financing_adv_mezz, "-",color = 'black',linewidth = 1,label='Mezz Adv')
		ax7.set_ylim([0,1])
		ax7.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax7.get_xticklabels(), visible=True)

		# ---------------------------------------------------------------------------------------- #
		ax8 = fig.add_subplot(338)
		ax5 = fig.add_subplot(335,sharex=ax8)
		ax2 = fig.add_subplot(332,sharex=ax8)
		
		ax2.set_title('Balance',fontsize = 8)
		ax5.set_title('Cashflow',fontsize = 8)
		ax8.set_title('Adv Rate',fontsize = 8)


		ax2.fill_between(self.second_financing_period, 0, self.second_financing_bal_snr,color = '#%02x%02x%02x' % (8, 142, 139),label='Snr Bal')
		ax2.fill_between(self.second_financing_period, self.second_financing_bal_snr,self.second_financing_bal_mezz,color = '#%02x%02x%02x' % (10, 186, 181),label='Mezz Bal')
		ax2.fill_between(self.second_financing_period, self.second_financing_bal_mezz, self.second_financing_bal_resid,color = '#%02x%02x%02x' % (13, 237, 232),label='Resid Bal')
		ax2.plot(self.second_financing_period, self.second_financing_bal_asset, "-",color = 'black',linewidth = 1,label='Asset Bal')
		ax2.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax2.get_xticklabels(), visible=False)

		ax5.fill_between(self.second_financing_period, 0, self.second_financing_cf_snr,color = '#%02x%02x%02x' % (8, 142, 139),label='Snr CF')
		ax5.fill_between(self.second_financing_period, self.second_financing_cf_snr, self.second_financing_cf_mezz,color = '#%02x%02x%02x' % (10, 186, 181),label='Mezz CF')
		ax5.fill_between(self.second_financing_period, self.second_financing_cf_mezz, self.second_financing_cf_resid,color = '#%02x%02x%02x' % (13, 237, 232),label='Resid CF')
		ax5.plot(self.second_financing_period, self.second_financing_cf_asset, "-",color = 'black',linewidth = 1,label='Asset CF')
		ax5.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax5.get_xticklabels(), visible=False)

		ax8.plot(self.second_financing_period, self.second_financing_adv_snr, "-",color = 'blue',linewidth = 1,label='Snr Adv')
		ax8.plot(self.second_financing_period, self.second_financing_adv_mezz, "-",color = 'black',linewidth = 1,label='Mezz Adv')
		ax8.set_ylim([0,1])
		ax8.legend(loc='upper right',ncol = 2,prop={'size':5})
		plt.setp(ax8.get_xticklabels(), visible=True)




		self.canvas = FigureCanvasTkAgg(fig,master=self.frame)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

class Display_Charts_Mgmt_OrcasFormat(Tkinter.Frame):
	def __init__(self, master, datadict_IN, keys_IN):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack(side = 'top')

		self.datadict = datadict_IN
		self.keys = keys_IN
		self.legends = []
		self.setup()

	def setup(self):
		self.legends = []
		self.smm_curves = []
		self.mdr_curves = []
		self.sev_curves = []
		self.loss_curves = []

		for key,value in self.datadict.items():

			self.legends.append(key)
			self.smm_curves.append(value['smm_curve'])
			self.mdr_curves.append(value['mdr_curve'])
			self.sev_curves.append(value['severity_curve'])
			self.loss_curves.append(value['cum_loss_curve'])

		smm_curve_x = []
		smm_curve_y = []
		for smm_curve in self.smm_curves:
			if len(smm_curve['period'])>len(smm_curve_x) : smm_curve_x = smm_curve['period']
			smm_curve_y.append(smm_curve['smm'])

		mdr_curve_x = []
		mdr_curve_y = []
		for mdr_curve in self.mdr_curves:
			if len(mdr_curve['period'])>len(mdr_curve_x) : mdr_curve_x = mdr_curve['period']		
			mdr_curve_y.append(mdr_curve['mdr'])

		sev_curve_x = []
		sev_curve_y = []
		for sev_curve in self.sev_curves:
			if len(sev_curve['period'])>len(sev_curve_x) : sev_curve_x = sev_curve['period']
			sev_curve_y.append(sev_curve['sev'])

		loss_curve_x = []
		loss_curve_y = []
		for loss_curve in self.loss_curves:
			if len(loss_curve['period'])>len(loss_curve_x) : loss_curve_x = loss_curve['period']
			loss_curve_y.append(loss_curve['loss'])




		fig = Figure(figsize = (7,4.5))

		rect = fig.patch
		rect.set_facecolor(Config.Orcas_grey)
		ax1 = fig.add_subplot(221)
		ax1.set_title('SMM Curve',fontsize = 8)
		for smm_curve_y_item in smm_curve_y:
			if len(smm_curve_x) > len(np.transpose(smm_curve_y_item)):
				smm_curve_y_item_ploted = np.transpose(smm_curve_y_item) * 100
				smm_curve_y_item_ploted = np.concatenate([smm_curve_y_item_ploted,np.array([np.nan] * (len(smm_curve_x) - len(np.transpose(smm_curve_y_item))))])
			else:
				smm_curve_y_item_ploted = np.transpose(smm_curve_y_item) * 100

			ax1.plot(smm_curve_x,smm_curve_y_item_ploted)
			ax1.grid(b=True, which='both', color='0.65',linestyle='-.')

		ax2= fig.add_subplot(222)
		ax2.set_title('MDR Curve',fontsize = 8)
		for mdr_curve_y_item in mdr_curve_y:
			if len(mdr_curve_x) > len(np.transpose(mdr_curve_y_item)):
				mdr_curve_y_item_ploted = np.transpose(mdr_curve_y_item) * 100
				mdr_curve_y_item_ploted = np.concatenate([mdr_curve_y_item_ploted,np.array([np.nan] * (len(mdr_curve_x) - len(np.transpose(mdr_curve_y_item))))])
			else:
				mdr_curve_y_item_ploted = np.transpose(mdr_curve_y_item) * 100

			ax2.plot(mdr_curve_x,mdr_curve_y_item_ploted)
			ax2.grid(b=True, which='both', color='0.65',linestyle='-.')

		ax3= fig.add_subplot(223)
		ax3.set_title('SEV Curve',fontsize = 8)
		cnt_i = 0
		for sev_curve_y_item in sev_curve_y:
			if len(sev_curve_x) > len(np.transpose(sev_curve_y_item)):
				sev_curve_y_item_ploted = np.transpose(sev_curve_y_item) * 100
				sev_curve_y_item_ploted = np.concatenate([sev_curve_y_item_ploted,np.array([np.nan] * (len(sev_curve_x) - len(np.transpose(sev_curve_y_item))))])
			else:
				sev_curve_y_item_ploted = np.transpose(sev_curve_y_item) * 100

			ax3.plot(mdr_curve_x,sev_curve_y_item_ploted, label = self.legends[cnt_i])
			legend = ax3.legend(loc='best', shadow=False,fontsize = 'xx-small',fancybox=True)
			ax3.grid(b=True, which='both', color='0.65',linestyle='-.')

			cnt_i += 1

		ax4= fig.add_subplot(224)
		ax4.set_title('Cum Loss Curve',fontsize = 8)
		for loss_curve_y_item in loss_curve_y:
			if len(loss_curve_x) > len(np.transpose(loss_curve_y_item)):
				loss_curve_y_item_ploted = np.transpose(loss_curve_y_item) * 100
				loss_curve_y_item_ploted = np.concatenate([loss_curve_y_item_ploted,np.array([np.nan] * (len(loss_curve_x) - len(np.transpose(loss_curve_y_item))))])
			else:
				loss_curve_y_item_ploted = np.transpose(loss_curve_y_item)  * 100

			ax4.plot(mdr_curve_x,loss_curve_y_item_ploted)
			ax4.grid(b=True, which='both', color='0.65',linestyle='-.')


		self.canvas = FigureCanvasTkAgg(fig,master=self.frame)

		# unsolved problem : how to make charts interactive

		# self.toolbar = NavigationToolbar(self.canvas, self.frame)
		# self.toolbar.update()
		# self.plot_widget = self.canvas.get_tk_widget()
		# self.plot_widget.pack(side='top', fill='both', expand=1)
		# self.toolbar.pack(side='top', fill='both', expand=1)

		self.canvas.show()
		self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

		# matplotlib.pyplot.plot([1,2,3,4])
		# matplotlib.pyplot.ylabel('some numbers')
		# matplotlib.pyplot.show()




class Labeled_Entry(Tkinter.Frame):
	def __init__(self, master, label_IN, default_IN = 0, width_IN = 10):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.Frame(self)
		self.frame.pack(side = 'top')

		self.label = Tkinter.Label(self.frame, text = label_IN)
		self.label.pack(side = 'left')
		self.entry = Tkinter.Entry(self.frame, width = width_IN)
		self.entry.pack(side = 'left')
		self.entry.insert(0,default_IN)
	
	def get(self):
		return self.entry.get()

class Group_Rule(object):
	def __init__(self):
		pass

	@staticmethod
	def save_group_rule(mappingrule_settings, mappingrule_settings_columns_gui, mappingrule_settings_columns_txt):
		mappingrule_settings.get_all(dict_type =True)
		mapping_rule_df = pd.DataFrame(mappingrule_settings.res)

		mapping_rule_columns = dict([(unicode(item_a),unicode(item_b)) for item_a,item_b in
			zip(mappingrule_settings_columns_gui,mappingrule_settings_columns_txt)])
		mapping_rule_df = mapping_rule_df.rename(columns = mapping_rule_columns)
		mapping_rule_df = mapping_rule_df[mappingrule_settings_columns_txt]

		sql_query = "INSERT INTO [Strats_GroupRule_Mapping] ([Rule_Idx], [Lower_Bound], [Upper_Bound], [Label]) "

		insert_value = ""
		(row_num, col_num) = mapping_rule_df.shape

		for i in range(0, row_num):
			if (len(mapping_rule_df.iloc[i][0]) + len(mapping_rule_df.iloc[i][1]) + len(mapping_rule_df.iloc[i][2])
				+ len(mapping_rule_df.iloc[i][3])) != 0:
				insert_value = insert_value + "(" + "'" + mapping_rule_df.iloc[i][0] + "'" + ", " + "'" + mapping_rule_df.iloc[i][1] + "'" + ", " + "'" + mapping_rule_df.iloc[i][2] + "'" + ", '" + mapping_rule_df.iloc[i][3] + "')"
			if i != row_num - 1:
				insert_value = insert_value + ","	

		sql_query = sql_query + "VALUES " + insert_value
		IO_Utilities.SQL_Util.query_sql_procedure(sql_query, 0, database = Config.orcas_operation_db)