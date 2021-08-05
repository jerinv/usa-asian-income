# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 18:55:39 2020

@author: jerin
"""

import numpy as np
import pandas as pd

import import_func


rows = import_func.row_generator(datapath = "usa_00013.dat", ddipath = "usa_00013.xml")
df = pd.DataFrame(rows)

for year in range(df.YEAR.min(), df.YEAR.max()+1):
    test = df.query(f'YEAR == {year}')
    test.to_feather(f'ACS_{year}.feather')
