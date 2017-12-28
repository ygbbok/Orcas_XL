# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")
import Tkinter as Tkinter
import ttk as ttk

from IO_Utilities import IO_Utilities
from Calc_Utilities import Calc_Utilities
from Other_Utilities import Other_Utilities

class CPR_CDR_Model(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.LabelFrame(self,borderwidth = 2)
		self.frame.pack()

		self.set_up()

	def set_up(self):
		self.descrtion_label = Tkinter.Label(self.frame, text = u"信用模型参数录入")
		self.descrtion_label.grid(row = 0, column = 0,columnspan = 2)


		self.CPR_label = Tkinter.Label(self.frame, text = "CPR")
		self.CPR_label.grid(row = 1, column = 0)

		self.CPR_entry = Tkinter.Entry(self.frame, width=10)
		self.CPR_entry.grid(row = 1, column = 1)
		self.CPR_entry.insert(0,0)

		self.CDR_label = Tkinter.Label(self.frame, text = "CDR")
		self.CDR_label.grid(row = 2, column = 0)

		self.CDR_entry = Tkinter.Entry(self.frame, width=10)
		self.CDR_entry.grid(row = 2, column = 1)
		self.CDR_entry.insert(0,0)

		self.SEV_label = Tkinter.Label(self.frame, text = "SEV")
		self.SEV_label.grid(row = 3, column = 0)

		self.SEV_entry = Tkinter.Entry(self.frame, width=10)
		self.SEV_entry.grid(row = 3, column = 1)
		self.SEV_entry.insert(0,0)

		self.RecoveryLag_label = Tkinter.Label(self.frame, text = "Recovery Lag")
		self.RecoveryLag_label.grid(row = 4, column = 0)

		self.RecoveryLag_entry = Tkinter.Entry(self.frame, width=10)
		self.RecoveryLag_entry.grid(row = 4, column = 1)
		self.RecoveryLag_entry.insert(0,0)

	def get(self):
		self.res_dict = {}
		self.res_dict.update({"CPR" : self.CPR_entry.get()})
		self.res_dict.update({"CDR" : self.CDR_entry.get()})
		self.res_dict.update({"SEV" : self.SEV_entry.get()})
		self.res_dict.update({"RecoveryLag" : self.RecoveryLag_entry.get()})

		return self.res_dict.copy()

	def destroy(self):
		self.frame.destroy()

class SMM_MDR_Model(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.LabelFrame(self,borderwidth = 2)
		self.frame.pack()

		self.set_up()

	def set_up(self):
		self.descrtion_label = Tkinter.Label(self.frame, text = u"信用模型参数录入")
		self.descrtion_label.grid(row = 0, column = 0,columnspan = 2)

		self.SMM_label = Tkinter.Label(self.frame, text = "SMM")
		self.SMM_label.grid(row = 1, column = 0)

		self.SMM_entry = Tkinter.Entry(self.frame, width=10)
		self.SMM_entry.grid(row = 1, column = 1)
		self.SMM_entry.insert(0,0)

		self.MDR_label = Tkinter.Label(self.frame, text = "MDR")
		self.MDR_label.grid(row = 2, column = 0)

		self.MDR_entry = Tkinter.Entry(self.frame, width=10)
		self.MDR_entry.grid(row = 2, column = 1)
		self.MDR_entry.insert(0,0)

		self.SEV_label = Tkinter.Label(self.frame, text = "SEV")
		self.SEV_label.grid(row = 3, column = 0)

		self.SEV_entry = Tkinter.Entry(self.frame, width=10)
		self.SEV_entry.grid(row = 3, column = 1)
		self.SEV_entry.insert(0,0)

		self.RecoveryLag_label = Tkinter.Label(self.frame, text = "Recovery Lag")
		self.RecoveryLag_label.grid(row = 4, column = 0)

		self.RecoveryLag_entry = Tkinter.Entry(self.frame, width=10)
		self.RecoveryLag_entry.grid(row = 4, column = 1)
		self.RecoveryLag_entry.insert(0,0)

	def get(self):
		self.res_dict = {}
		self.res_dict.update({"SMM" : self.SMM_entry.get()})
		self.res_dict.update({"MDR" : self.MDR_entry.get()})
		self.res_dict.update({"SEV" : self.SEV_entry.get()})
		self.res_dict.update({"RecoveryLag" : self.RecoveryLag_entry.get()})

		return self.res_dict.copy()

	def destroy(self):
		self.frame.destroy()

class CTC_5m10m_Model(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()

		self.frame = Tkinter.LabelFrame(self,borderwidth = 2)
		self.frame.pack()

		self.set_up()

	def set_up(self):
		self.descrtion_label = Tkinter.Label(self.frame, text = u"信用模型参数录入")
		self.descrtion_label.grid(row = 0, column = 0,columnspan = 2)


		self.SEV_label = Tkinter.Label(self.frame, text = "SEV")
		self.SEV_label.grid(row = 1, column = 0)

		self.SEV_entry = Tkinter.Entry(self.frame, width=10)
		self.SEV_entry.grid(row = 1, column = 1)
		self.SEV_entry.insert(0,10)

		self.RecoveryLag_label = Tkinter.Label(self.frame, text = "Recovery Lag")
		self.RecoveryLag_label.grid(row = 2, column = 0)

		self.RecoveryLag_entry = Tkinter.Entry(self.frame, width=10)
		self.RecoveryLag_entry.grid(row = 2, column = 1)
		self.RecoveryLag_entry.insert(0,2)

		self.SMMMulti_label = Tkinter.Label(self.frame, text = "SMM Multi")
		self.SMMMulti_label.grid(row = 3, column = 0)

		self.SMMMulti_entry = Tkinter.Entry(self.frame, width=10)
		self.SMMMulti_entry.grid(row = 3, column = 1)
		self.SMMMulti_entry.insert(0,1)

		self.MDRMulti_label = Tkinter.Label(self.frame, text = "MDR Multi")
		self.MDRMulti_label.grid(row = 4, column = 0)

		self.MDRMulti_entry = Tkinter.Entry(self.frame, width=10)
		self.MDRMulti_entry.grid(row = 4, column = 1)
		self.MDRMulti_entry.insert(0,1)

	def get(self):
		self.res_dict = {}
		self.res_dict.update({"SEV" : self.SEV_entry.get()})
		self.res_dict.update({"RecoveryLag" : self.RecoveryLag_entry.get()})
		self.res_dict.update({"SMM Multi" : self.SMMMulti_entry.get()})
		self.res_dict.update({"MDR Multi" : self.MDRMulti_entry.get()})

		return self.res_dict.copy()

	def destroy(self):
		self.frame.destroy()




def main():
	print 1
if __name__ == "__main__":
	main()