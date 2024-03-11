import pandas as pd 
import numpy as np
import os
case_file_pth = './config'
bus_file = os.path.join(case_file_pth, 'bus.csv')
branch_file = os.path.join(case_file_pth, 'branch.csv')
gen_file = os.path.join(case_file_pth, 'gen.csv')
gen_cost_file = os.path.join(case_file_pth, 'gencost.csv')

# add all buses to network
