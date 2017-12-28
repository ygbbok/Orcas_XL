# -*- coding: utf-8 -*-

import pandas as pd
import webbrowser
import random
import string
import pyodbc
from Config import Config
import os
import sys
sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas\\")

class IO_Util(object):
	def __init__(self):
		pass

	@staticmethod
	def read_csv(dir, sep = ","):
		return pd.read_csv(dir, header = "infer", sep = sep)

	@staticmethod
	def open_in_html(df_IN, prefix_IN = ''):
		html_page = prefix_IN + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		# html_dir = 'F:\Work\Bohai Huijin Asset Management\Investment\Orcas\Temp\\' + html_page + '.html'
		html_dir = Config.temp_html_dir + html_page + '.html'
		file_handler= open(html_dir,'w')
		file_handler.write(df_IN.to_html())
		file_handler.close()

		webbrowser.open(html_dir)

	@staticmethod
	def output_to_txt(df, dir, sep = '|'):
		df.to_csv(dir,index = False,sep = sep)

class SQL_Util(object):
	def __init__(self):
		pass

	@staticmethod
	def query_sql_procedure(sql_script_IN, table_res_IN = 1,database = Config.cracked_tables_prod_db):
		if table_res_IN > 0:
			sql_script = "set nocount on\n"
			con = pyodbc.connect(driver='{SQL Server Native Client 11.0}', host = Config.sql_server, database=database,trusted_connection='yes',autocommit=True)
			cursor = con.cursor()
			sql_script = sql_script + sql_script_IN
			cursor.execute(sql_script)
			# cursor.commit()

			res_list = []

			# cursor.commit()
			# cursor.nextset()
			# rows = cursor.fetchall()

			for i in range(1,table_res_IN+1):

				if i > 1: cursor.nextset()
				cursor.commit()
				rows = cursor.fetchall()
				col = [item[0] for item in cursor.description]
				df = pd.DataFrame(data = [tuple(row_item) for row_item in rows],columns = col)

				res_list.append(df)

			con.close()
			return res_list

		elif table_res_IN == 0:
			con = pyodbc.connect(driver='{SQL Server Native Client 11.0}', host = Config.sql_server, database=database,trusted_connection='yes')
			cursor = con.cursor()
			sql_script = sql_script_IN
			cursor.execute(sql_script)
			cursor.commit()
			con.close()

	@staticmethod
	def script_generator_engine_1(table_IN, condition_list_IN = []):
		# generator engine based on condition list
		script_res = ""
		select_clause = "select * from " + table_IN + "\n"
		condition_clause = ""
		if len(condition_list_IN) > 0 and len(condition_list_IN[0][u'表头'])>0:
			condition_clause = condition_clause + "where \n"
			i = 0
			for condition_item in condition_list_IN:
				if condition_item[u"数据类型"].lower() == 'str':
					condition_clause = condition_clause + ((condition_item[u"逻辑"] + " ") if i!=0 else "") + "[" + condition_item[u"表头"] + "]" + " " + condition_item[u"运算符"] + "'" + condition_item[u"参数"] + "'"
				else:

					condition_clause = condition_clause + ((condition_item[u"逻辑"] + " ") if i!=0 else "") + "[" + condition_item[u"表头"] + "]" + " " + condition_item[u"运算符"] + condition_item[u"参数"]

				# if i!=0: condition_clause = condition_item["Logic"] + " " + condition_clause
				condition_clause = condition_clause + '\n'
				i += 1

		script_res = select_clause + condition_clause
		return script_res


	@staticmethod
	def script_generator_engine_2(table_IN, orcas_user_IN):
		# generator engine based on orcas user
		script_res = '''
					select a.* from 
					''' + table_IN + '''
					 a,
					[dbo].[temp_marketplace_lending_BHHJ_loan_pool] b
					where
					a.[BHHJ_Loan_Number] = b.[BHHJ_Loan_Number]
					and
					b.[creator] = 
					''' + "'" + orcas_user_IN + "'"
		return script_res


	@staticmethod
	def delete_temp_pool_table():
		script = 'delete from [dbo].[temp_marketplace_lending_BHHJ_loan_pool]'
		SQL_Util.query_sql_procedure(script,0)

	@staticmethod
	def upload_temp_pool_table():
		script = 'delete from [dbo].[temp_marketplace_lending_BHHJ_loan_pool]'
		SQL_Util.query_sql_procedure(script,0)
				
		cmd_line = 'bcp [dbo].[temp_marketplace_lending_BHHJ_loan_pool] in "' + Config.BHHJ_static_temp_pool_txt+ '" -S "' + Config.sql_server + '" -d ' + Config.cracked_tables_prod_db + ' -T -c -t "|"'
		os.system(cmd_line)

	@staticmethod
	def upload_bhhj_forecast_cf():
		cmd_line = 'bcp [dbo].[BHHJ_Forecast_CF] in "' + Config.BHHJ_Forecast_temp_txt+ '" -S "' + Config.sql_server + '" -d ' + Config.cracked_tables_prod_db + ' -T -c -t "|"'
		os.system(cmd_line)

	@staticmethod
	def delete_orcas_operation_strats_records(strats_idx_to_be_deleted):
		script = 'delete from [dbo].[Strats_Idx_Name] WHERE [Strats_Idx] = ' + str(strats_idx_to_be_deleted)
		SQL_Util.query_sql_procedure(script,database = Config.orcas_operation_db,table_res_IN = 0)

		script = 'delete from [dbo].[Strats_Measures] WHERE Strats_Idx = ' + str(strats_idx_to_be_deleted)
		SQL_Util.query_sql_procedure(script,database = Config.orcas_operation_db,table_res_IN = 0)

		script = 'delete from [dbo].[Strats_Dimensions] WHERE Strats_Idx = ' + str(strats_idx_to_be_deleted)
		SQL_Util.query_sql_procedure(script,database = Config.orcas_operation_db,table_res_IN = 0)

	@staticmethod
	def upload_orcas_operation_strats_tables():
		cmd_line = 'bcp [dbo].[Strats_Idx_Name] in "' + Config.strats_idx_name_temp_txt+ '" -S "' + Config.sql_server + '" -d ' + Config.orcas_operation_db + ' -T -c -t "|"'
		os.system(cmd_line)

		cmd_line = 'bcp [dbo].[Strats_Dimensions] in "' + Config.strats_dimension_settings_temp_txt+ '" -S "' + Config.sql_server + '" -d ' + Config.orcas_operation_db + ' -T -c -t "|"'
		os.system(cmd_line)

		cmd_line = 'bcp [dbo].[Strats_Measures] in "' + Config.strats_measures_settings_temp_txt+ '" -S "' + Config.sql_server + '" -d ' + Config.orcas_operation_db + ' -T -c -t "|"'
		os.system(cmd_line)		