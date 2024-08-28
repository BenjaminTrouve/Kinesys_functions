#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from matplotlib.colors import ListedColormap
from matplotlib.colorbar import ColorbarBase
import seaborn as sns
import pandas as pd
from matplotlib.patches import Patch

disc_rate = 0.07
t0 = 2019

def discount_rate(t0, disc_rate):
    discount_rate_1 = []
    discount_rate_05 = []
    for date in range(t0,2051):
        t = (date - t0)
        t1 = t
        t05 = t/2
        rate1 = 1 / ((1 + disc_rate) ** t1)
        rate2 = 1 / ((1 + disc_rate) ** t05)

        discount_rate_1.append({'date': date, 'rate': rate1})
        discount_rate_05.append({'date': date, 'rate': rate2})
     
    return pd.DataFrame(discount_rate_1),pd.DataFrame(discount_rate_05)

def decompose_LCOH(file_path, run_name):
    disc_rate = 0.07
    t0 = 2019
    
    attribute = ['Cost_Inv','Cost_Fom','VAR_FIn','VAR_FOut']

    lcoh_res = pd.DataFrame()
    for att in attribute:
        print(att)
        att_df = pd.read_csv(file_path + att +'_' + run_name + '.csv', sep = ',')
        if att == 'VAR_Ncap':
            att_df = att_df[att_df['2'].str.contains('H2prd')]
            att_df['group'] = att_df['3'].astype(str).str.cat(att_df['2'].astype(str), sep='_').str.cat(att_df['4'].astype(str), sep='_')
            att_df[att] = att_df['8']
            att_df = att_df[~att_df['group'].duplicated()]
            att_df = att_df[['group','3',att]]
            years_att_df = pd.DataFrame()
            for years in att_df['3'].unique():
                years_lcoh = att_df[att_df['3'] == years]
                time_d_rate1 = d_rate1[(d_rate1['date'] >= int(years) - 5) & (d_rate1['date'] < int(years) + 1)]
                time_npv1 = time_d_rate1['rate'].sum()
                
                years_lcoh[att] = years_lcoh[att]*time_npv1
                years_att_df =  pd.concat([years_att_df,years_lcoh], axis = 0)

            if lcoh_res.empty:
                lcoh_res = pd.concat([lcoh_res,years_att_df],axis=0)
                lcoh_res.drop(columns=['3'],inplace=True)

            else:
                lcoh_res = pd.merge(lcoh_res,years_att_df, how='outer',on='group')
                lcoh_res.drop(columns=['3'],inplace=True)
        
        if att == 'Cost_Inv':
            att_df = att_df[(att_df['7'].str.contains('INV')) & (att_df['2'].str.contains('H2prd'))]

            if att_df.empty:
                pass
            else:
                att_df['group'] = att_df['5'].astype(str).str.cat(att_df['2'].astype(str), sep='_').str.cat(att_df['4'].astype(str), sep='_')
                att_df[att] = att_df['8']
                att_df = att_df[~att_df['group'].duplicated()]
                att_df = att_df[['group','3','4','2',att]]

            if lcoh_res.empty:
                lcoh_res = pd.concat([lcoh_res,att_df],axis=0)

            else:
                lcoh_res = pd.merge(lcoh_res,att_df, how='outer',on='group') 
            
        if att == 'Cost_Fom':
            att_df = att_df[att_df['2'].str.contains('H2prd')]
            att_df['group'] = att_df['5'].astype(str).str.cat(att_df['2'].astype(str), sep='_').str.cat(att_df['4'].astype(str), sep='_')
            att_df[att] = att_df['8']
            att_df = att_df[~att_df['group'].duplicated()]
            att_df = att_df[['group',att]]
            if lcoh_res.empty:
                lcoh_res = pd.concat([lcoh_res,att_df],axis=0)

            else:
                lcoh_res = pd.merge(lcoh_res,att_df, how='outer',on='group') 

       
            

        if att == 'VAR_FIn':
            att_df = att_df[att_df['2'].str.contains('H2prd')]
            att_df['grp_proc'] = att_df['5'].astype(str).str.cat(att_df['2'].astype(str), sep='_').str.cat(att_df['4'].astype(str), sep='_')
            
            eq_comn_df = pd.DataFrame()
            for process in att_df['grp_proc'].unique():
                process_df = att_df[att_df['grp_proc'] == process]
                list_input = list(process_df['1'].unique())
                
                att_eq_comb = pd.read_csv(file_path + 'EQ_CombalM' +'_' + run_name + '.csv', sep = ',')
                att_eq_comb = att_eq_comb[att_eq_comb['1'].isin(list_input)]
                att_eq_comb['grp'] = att_eq_comb['3'].astype(str).str.cat(att_eq_comb['1'].astype(str), sep='_').str.cat(att_eq_comb['6'].astype(str), sep='_').str.cat(att_eq_comb['4'].astype(str), sep='_')
                att_eq_comb.rename(columns={'8': 'eq_combal'}, inplace=True)
                att_eq_comb = att_eq_comb[['grp','eq_combal']]

                process_df['grp'] = process_df['5'].astype(str).str.cat(process_df['1'].astype(str), sep='_').str.cat(process_df['6'].astype(str), sep='_').str.cat(process_df['4'].astype(str), sep='_')
                process_df.rename(columns={'8': 'var_fin'}, inplace=True)
                process_df = process_df[['grp','var_fin','2','4','5']]
                

                cost_df = pd.merge(att_eq_comb,process_df, how='outer',on='grp').dropna()
                
                cost_df['cost_flow'] = cost_df['eq_combal']*cost_df['var_fin']
               
                cost_df['5'] = cost_df['5'].astype(int)
                cost_df['group'] = cost_df['5'].astype(str).str.cat(cost_df['2'].astype(str), sep='_').str.cat(cost_df['4'].astype(str), sep='_')
                cost_df['flow_cost_grp'] = cost_df.groupby('group')['cost_flow'].transform('sum')
                cost_df = cost_df[~cost_df['group'].duplicated()]
                cost_df = cost_df[['group','flow_cost_grp']].reset_index(drop=True)
                
 
                eq_comn_df = pd.concat([eq_comn_df,cost_df], axis = 0)

            lcoh_res = pd.merge(lcoh_res,eq_comn_df, how='outer',on='group')

        if att == 'VAR_FOut':
            att_df = att_df[att_df['2'].str.contains('H2prd')]
            att_df = att_df[(att_df['6'] != 'ANNUAL')]
            att_df['group'] = att_df['5'].astype(str).str.cat(att_df['2'].astype(str), sep='_').str.cat(att_df['4'].astype(str), sep='_')
            att_df[att] = att_df['8']
            att_df = att_df[~att_df['group'].duplicated()]
            att_df = att_df[['group',att]]
            if lcoh_res.empty:
                lcoh_res = pd.concat([lcoh_res,att_df],axis=0)

            else:
                lcoh_res = pd.merge(lcoh_res,att_df, how='outer',on='group') 
    lcoh_res = lcoh_res.dropna()


    d_rate1,d_rate05  = discount_rate(t0,disc_rate)

    lcoh_res['years'] = lcoh_res['group'].str.split('_').str[0]
    final_lcoh = pd.DataFrame()
    for years in lcoh_res['years'].unique():
        years_lcoh = lcoh_res[lcoh_res['years'] == years]
        time_d_rate1 = d_rate1[(d_rate1['date'] >= int(years) - 5) & (d_rate1['date'] < int(years) + 1)]
        time_d_rate1 = d_rate1[(d_rate1['date'] == int(years))]

        time_npv1 = time_d_rate1['rate'].sum()

        years_lcoh['lcoh'] = ( pd.to_numeric(years_lcoh['Cost_Inv'])*time_npv1  + pd.to_numeric(years_lcoh['Cost_Fom'])*time_npv1 + pd.to_numeric(years_lcoh['flow_cost_grp'])*time_npv1) / pd.to_numeric(years_lcoh['VAR_FOut'])*time_npv1
        final_lcoh = pd.concat([final_lcoh,years_lcoh],axis=0)
    
    final_lcoh['total_costs'] = final_lcoh['Cost_Inv']+final_lcoh['Cost_Fom']+final_lcoh['flow_cost_grp']
    final_lcoh[['Cost_Inv%','Cost_Fom%','flow_cost_grp%']] = final_lcoh[['Cost_Inv','Cost_Fom','flow_cost_grp']].div(final_lcoh['total_costs'], axis=0)
    final_lcoh['lcoh_final'] = final_lcoh.groupby('group')['lcoh'].transform('sum')
    return final_lcoh
    

def func_LCOH(file_path,run_name,output_folder):
    lcoh_df = decompose_LCOH(file_path, run_name)
    pivot_df = lcoh_df.pivot_table(index=['4', '2'], columns='3', values='lcoh_final').reset_index()

    # Melt the DataFrame back to long format for seaborn
    melted_df = pivot_df.melt(id_vars=['4', '2'], value_vars=[2035, 2040, 2045, 2050], 
                            var_name='3', value_name='lcoh_final')

    # Plotting
    # sns.set(style="whitegrid")

    # Initialize the matplotlib figure
    pivot_df = lcoh_df.pivot_table(index=['4', '2'], columns='3', values='lcoh_final').reset_index()

    # Melt the DataFrame back to long format for seaborn
    melted_df = pivot_df.melt(id_vars=['4', '2'], value_vars=[2035, 2040, 2045, 2050], 
                            var_name='3', value_name='lcoh_final')
    melted_df = melted_df.dropna()
    melted_df.head(30)

    # Plotting
    sns.set(style="whitegrid")

    # Initialize the matplotlib figure
    processes = melted_df['2'].unique()
    num_processes = len(processes)

    # Initialize the matplotlib figure
    nrows = (num_processes + 1) // 2  # Calculate number of rows needed
    f, axes = plt.subplots(nrows=nrows, ncols=2, figsize=(12, 5 * nrows))

    # If there's only one subplot, axes will be a single Axes object
    if num_processes == 1:
        axes = [axes]

    # Flatten axes array for easier iteration if needed
    axes = axes.flatten()

    # Plotting
    sns.set(style="whitegrid")

    for ax, process in zip(axes, processes):
        process_data = melted_df[melted_df['2'] == process]
        sns.barplot(x="lcoh_final", y="4", hue="3", data=process_data, ax=ax, dodge=True, errorbar=None)
        ax.set_title(process)
        ax.set_xlabel("$/kgH2")
        ax.set_ylabel("")
        ax.legend(title='Years')

    for ax in axes[::2]:  # First column of subplots
        ax.set_ylabel("Region")

    # Hide any unused subplots
    for ax in axes[num_processes:]:
        ax.axis('off')

    # Adjust layout
    plt.tight_layout()
    plt.savefig(output_folder + 'lcoh_decomposed.pdf'
                    , format ='pdf',
                    bbox_inches='tight')




