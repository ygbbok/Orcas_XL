# -*- coding: utf-8 -*-

import pandas as pd
import locale
import sys
import getpass


Formatter_pct2 = lambda x: "{:.2%}".format(x)
Formatter_pct1 = lambda x: "{:.1%}".format(x)
Formatter_pct0 = lambda x: "{:.0%}".format(x)

Formatter_dec2 = lambda x: '{0:,.2f}'.format(x)
Formatter_dec1 = lambda x: '{0:,.1f}'.format(x)
Formatter_dec0 = lambda x: '{0:,.0f}'.format(x)

import os
Orcas_dir = os.path.dirname(os.path.dirname(__file__))
filename = os.path.join(Orcas_dir, 'Static_Pool\Mgmt_Static_Pool.pickle')


Mgmt_Static_Pool_File = os.path.join(Orcas_dir, 'Static_Pool\Mgmt_Static_Pool.pickle')

Static_Pool_Folder = os.path.join(Orcas_dir, 'Static_Pool\\')

Unlevered_Economics_Run_Folder = os.path.join(Orcas_dir, 'Unlevered_Economics_Run\\')

Mgmt_Unlevered_Economics_Run_File = os.path.join(Orcas_dir, 'Unlevered_Economics_Run\Mgmt_Unlevered_Economics_Run.pickle')
Mgmt_Levered_Economics_Run_File = os.path.join(Orcas_dir, 'Levered_Economics_Run\Mgmt_Levered_Economics_Run.pickle')

ORCAS_ICON = os.path.join(Orcas_dir, 'LOGO_TITLE\ORCAS_ICON.ico')

Formatter_pct2 = lambda x: "{:.2%}".format(x)

temp_html_dir = os.path.join(Orcas_dir, 'Temp\\')

# ********************** Database **********************
user_sql_dict = {"Hong Fan":{"sql_server":'(localdb)\MSSQLLocalDB'},
	"liuxiao":{"sql_server":"liuxiao-PC"}}

sql_server = user_sql_dict[getpass.getuser()]['sql_server']
staging_tables_db = "marketplace_lending_staging_tables"
cracked_tables_dev_db = "marketplace_lending_cracked_dev_tables"
cracked_tables_prod_db = "marketplace_lending_cracked_prod_tables"

orcas_operation_db = "orcas_operation"

production_table_list = ['Consumer']

BHHJ_static_temp_pool_txt = os.path.join(Orcas_dir, 'Static_Pool\\to_be_loaded_pool.txt')

BHHJ_Forecast_temp_txt = os.path.join(Orcas_dir, 'Unlevered_Economics_Run\\BHHJ_Forecast.txt')
# ********************** Database **********************

# ********************** Color **********************
Orcas_green = '#%02x%02x%02x' % (52, 204, 153)
Orcas_blue = '#%02x%02x%02x' % (64, 204, 208)
Orcas_grey = '#%02x%02x%02x' % (238,233,233)
Orcas_snow = '#%02x%02x%02x' % (255,250,250)
# ********************** Color **********************

# ********************** Credit Model **********************
creditmodel_list = ['CPR/CDR','SMM/MDR','CTC CASHLOAN(5m10m BASE)']
# ********************** Credit Model **********************

# ********************** Struct Model **********************
structmodel_list = [u'整体买断', u'结构化信托(建仓)', u'证券化']
structmodel_list = [u'结构化信托(建仓)', u'证券化']
# ********************** Struct Model **********************


# ********************** Strats **********************
temp_rtd_txt = os.path.join(Orcas_dir, 'Strats_Analytics\\temp_rtd.txt')
ctc_loan_tape = "F:\Work\Bohai Huijin Asset Management\Investment\ABS Investment\Opportunities\\5.RawTape\chinatopcredit.CashLoan.15m.loantape.csv"

default_dimension_settings_file = os.path.join(Orcas_dir, 'Strats_Analytics\dimensions_settings.txt')
default_measure_settings_file = os.path.join(Orcas_dir, 'Strats_Analytics\measures_settings.txt')
default_rules_mapping_file = os.path.join(Orcas_dir, 'Strats_Analytics\\rules_mapping.txt')

temp_strats_txt = os.path.join(Orcas_dir, '\\txt_temp\\temp_strats')
delimiter = "|"

dimension_settings_columns_gui = [u'字段',u'组合规则',u'分层标签']
dimension_settings_columns_txt = [u'column',u'group_rule',u'strats_label']

measures_settings_columns_gui = [u'字段',u'运算符',u'运算辅助列',u'度量名称',u'格式']
measures_settings_columns_txt = [u'column',u'calc_method',u'calc_helper','col_name','format']

mappingrule_settings_columns_gui = [u'分组编号',u'下限',u'上限',u'分组标签']
mappingrule_settings_columns_db = [u'Rule_Idx',u'Lower_Bound',u'Upper_Bound','Label']
mappingrule_settings_columns_txt = [u'Rule_Name',u'Lower_Bound',u'Upper_Bound','Label']

strats_idx_name_temp_txt = os.path.join(Orcas_dir, 'Orcas_Operation_temp_txt\Strats_Idx_temp.txt')
strats_dimension_settings_temp_txt = os.path.join(Orcas_dir, 'Orcas_Operation_temp_txt\Strats_Dimension_Settings_temp.txt')
strats_measures_settings_temp_txt = os.path.join(Orcas_dir, 'Orcas_Operation_temp_txt\Strats_Measures_Settings_temp.txt')

strats_idx_name_db_table_columns = ['Strats_Idx','Strats_Name','RT_Dir','Sort_by','Display_Top_N']
strats_dimension_db_table_columns = ['Dime_Idx','Dime_Ori_Label','Dime_Std_Label','Rule_Idx','Strats_Idx']
strats_measures_db_table_columns = ['Meas_Idx','Meas_Ori_Label','Meas_Std_Label','Calc_Method','Calc_Helper','Strats_Idx','format']

format_list = ['Dec 2','Dec 1','Dec 0','Pct 2','Pct 1','Pct 0']
format_mapping = {
	'':Formatter_dec2,
	'Dec 2':Formatter_dec2,
	'Dec 1':Formatter_dec1,
	'Dec 0':Formatter_dec0,
	'Pct 2':Formatter_pct2,
	'Pct 1':Formatter_pct1,
	'Pct 0':Formatter_pct0
}

struct_info_pkl = os.path.join(Orcas_dir, 'Struct_Specifics\\', '1.Struct_Info', '.pkl')

# ********************** Strats **********************
