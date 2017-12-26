
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import webbrowser
import random
import string
import pyodbc


reload(sys)
sys.setdefaultencoding("gb2312")

class IO_Util(object):
	def __init__(self):
		pass

	@staticmethod
	def read_csv(dir, sep = ","):
		return pd.read_csv(dir, header = "infer", sep = sep,encoding='gb2312')

	@staticmethod
	def open_in_html(df_IN, prefix_IN = ''):
		html_page = prefix_IN + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		html_dir = 'F:\Work\Bohai Huijin Asset Management\Investment\Orcas_Killer\\txt_temp\\' + html_page + '.html'
		file_handler= open(html_dir,'w')
		file_handler.write(df_IN.to_html())
		file_handler.close()
		webbrowser.open(html_dir)

	@staticmethod
	def output_to_txt(df, dir, sep = '|'):
		df.to_csv(dir,index = False,sep = sep)

