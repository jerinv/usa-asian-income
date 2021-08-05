# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 12:33:16 2020

@author: jerin
"""
import numpy as np
import pandas as pd
import import_func as imp

def weighted_median(values, weights):
    ''' compute the weighted median of values list. The 
weighted median is computed as follows:
    1- sort both lists (values and weights) based on values.
    2- select the 0.5 point from the weights and return the corresponding values as results
    e.g. values = [1, 3, 0] and weights=[0.1, 0.3, 0.6] assuming weights are probabilities.
    sorted values = [0, 1, 3] and corresponding sorted weights = [0.6,     0.1, 0.3] the 0.5 point on
    weight corresponds to the first item which is 0. so the weighted     median is 0.'''

    #convert the weights into probabilities
    sum_weights = sum(weights)
    weights = np.array([(w*1.0)/sum_weights for w in weights])
    #sort values and weights based on values
    values = np.array(values)
    sorted_indices = np.argsort(values)
    values_sorted  = values[sorted_indices]
    weights_sorted = weights[sorted_indices]
    #select the median point
    it = np.nditer(weights_sorted, flags=['f_index'])
    accumulative_probability = 0
    median_index = -1
    while not it.finished:
        accumulative_probability += it[0]
        if accumulative_probability > 0.5:
            median_index = it.index
            return values_sorted[median_index]
        elif accumulative_probability == 0.5:
            median_index = it.index
            it.iternext()
            next_median_index = it.index
            return np.mean(values_sorted[[median_index, next_median_index]])
        it.iternext()

    return values_sorted[median_index]

rows = imp.row_generator(datapath = "usa_00012.dat", ddipath = "usa_00012.xml")
df = pd.DataFrame(rows)

df_num = df.apply(pd.to_numeric)
# Let first person of household represent the household
per1 = df_num.query('PERNUM == 1').copy()
# Drop all N/A values
per1 = per1[per1.HHINCOME != 9999999].copy()
# Drop negative values
per1 = per1[per1.HHINCOME >= 0].copy()
per1.HHINCOME.max()

#per1['WGTINCOME'] = per1.HHWT * per1.HHINCOME
my_bridge = pd.read_clipboard()
my_dict = my_bridge[['Value','MyValue']].set_index('Value').to_dict()['MyValue']

per1['MYANCESTR1'] = per1.ANCESTR1.replace(my_dict)
#per1['MYRACED'] = per1.RACED.replace(my_dict)
ancestry_income = per1.groupby('MYANCESTR1').agg({'HHWT':'sum', 'HHINCOME':lambda x: weighted_median(x, per1.loc[x.index, 'HHWT'])})
race_income = per1.groupby('MYRACED').agg({'HHWT':'sum', 'HHINCOME':lambda x: weighted_median(x, per1.loc[x.index, 'HHWT'])})
#ancestry_income['AVGINCOME'] = ancestry_income.WGTINCOME / ancestry_income.HHWT
weighted_median(per1[per1.HHINCOME >= 0].HHINCOME, per1[per1.HHINCOME >= 0].HHWT)

rich_race_by_state = per1.groupby(['STATEFIP','MYRACED']).agg({'HHWT':'sum', 'HHINCOME':lambda x: weighted_median(x, per1.loc[x.index, 'HHWT'])})
rich_race_by_state = rich_race_by_state.reset_index()
rich_race_by_state['STATESHARE'] = rich_race_by_state.groupby('STATEFIP')['HHWT'].transform(lambda x: x/x.sum())
#rich_race_by_state = rich_race_by_state[~rich_race_by_state.MYANCESTR1.isin([999,181,183,185,187,190,195,924,995,996])]
rich_race_by_state = rich_race_by_state[~rich_race_by_state.MYRACED.isin([812])]
rich_race_by_state = rich_race_by_state.query('STATESHARE >= 0.01')
idx = rich_race_by_state.groupby('STATEFIP')['HHINCOME'].transform(max) == rich_race_by_state['HHINCOME']
results = rich_race_by_state[idx]

rich_ancestry_by_state = per1.groupby(['STATEFIP','MYANCESTR1']).agg({'HHWT':'sum', 'HHINCOME':lambda x: weighted_median(x, per1.loc[x.index, 'HHWT'])})
rich_ancestry_by_state = rich_ancestry_by_state.reset_index()
rich_ancestry_by_state['STATESHARE'] = rich_ancestry_by_state.groupby('STATEFIP')['HHWT'].transform(lambda x: x/x.sum())
rich_ancestry_by_state = rich_ancestry_by_state[~rich_ancestry_by_state.MYANCESTR1.isin([999,181,183,185,187,190,195,924,995,996])]
rich_ancestry_by_state = rich_ancestry_by_state.query('STATESHARE >= 0.01')
idx = rich_ancestry_by_state.groupby('STATEFIP')['HHINCOME'].transform(max) == rich_ancestry_by_state['HHINCOME']
results = rich_ancestry_by_state[idx]


# =============================================================================
# Most popular indian jobs
# =============================================================================
india_jobs = df_num.copy()
india_jobs['MYANCESTR1'] = per1.ANCESTR1.replace(my_dict)
india_jobs = india_jobs.query('MYANCESTR1 == "615"').copy()
india_jobs = india_jobs.groupby('OCC').PERWT.sum()
