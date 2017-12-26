# -*- coding: utf-8 -*-

import sys
import os
import shutil
reload(sys)
sys.setdefaultencoding( "gb2312" )

# sys.path.append("F:\Work\Bohai Huijin Asset Management\Investment\Orcas_Killer\Strats_Analytics\\")
sys.path.append("E:\BHHJ\Code\Orcas\Strats_Analytics\\")


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

reload(sys)
sys.setdefaultencoding("gb2312")

orcas_user = 'HFan'
