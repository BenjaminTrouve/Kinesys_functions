#!/usr/bin/env python
# coding: utf-8

# In[4]:


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import pandas as pd
from collections import Counter
import re

### path to import .vde file to import the commodity sets
# folder1 = 'C:/Users/trouvebe/Desktop/Thesis/Chapter 1/Output/VDE file/nze~0004_1406/'
# filename1 = 'nze~0004_1406'
# folder2 = 'C:/Users/trouvebe/Desktop/Thesis/Chapter 1/Output/VDE file/nze~0004_2805/'
# filename2 = 'nze~0004_2805'

## Function to filter the commodity sets
def commodity(folder,filename):
    com_set = pd.read_csv(folder + 'Commodity_' + filename + '.csv', sep = ',')
    list_com = com_set.iloc[:,2].unique()
    filtered_strings = [s for s in list_com if s.isupper()]

    com = ['AGR','COM','ELC','IND','RES','TRA','SUP']
    filtered_com = [s for s in filtered_strings if any(sub in s for sub in com)]

    not_com = ['IEA','CO2','CCS']
    filtered_com = [s for s in filtered_com if not any(sub in s for sub in not_com)]
    filtered_com = [s for s in filtered_com if not len(s) < 4]
    # print(filtered_com)

    counts = Counter(filtered_com)
    com_filt = [item for item in filtered_com if counts[item] == 1]
    com_filt.sort()
    return com_filt

### function to plot the energy consumption mix 
def func_final_energy_consumption(file_path_scen,file_path_ref, run_name_scen,run_name_ref,output_folder):

    ## dictionary to assign each final energy demand to a commodity
    dict_nrg = {'ELC':['ELC','NUC','SPV','WIN','HYD','STH'],
                'BIO':['BIO','BDS','BGS','BSL','BJT','BFG','SNG'],
                'OIL':['GSL','DST','OIL','JTK','HFO','LPG','RFG','KER','RPP','CRD'],
                'HEAT':['HET'],
                'HH2':['HH2','GH2'],
                'COAL':['COB','OVC','COA','COG'],
                'NGA':['NGA'],
                'GEO':['GEO']}
    
    ## Calculate the final energy consumption for each commodity in Mtoe for the reference scenario
    var_Fin_ref = pd.read_csv(file_path_ref + 'VAR_FIn_' + run_name_ref + '.csv', sep = ',')
    var_Fin_ref = var_Fin_ref[var_Fin_ref['1'].isin(commodity(file_path_ref,run_name_ref))]
    var_Fin_ref['fuel'] = var_Fin_ref['1'].astype(str).str[-3:]
    reverse_mapping = {item: key for key, values in dict_nrg.items() for item in values}
    var_Fin_ref['fuel_grp'] = var_Fin_ref['fuel'].map(reverse_mapping)
    var_Fin_ref['group'] = var_Fin_ref['fuel_grp'].str.cat(var_Fin_ref['3'].astype(str), sep='_')
    var_Fin_ref['fuel_mtoe'] = var_Fin_ref.groupby('group')['8'].transform('sum')*0.023
    var_Fin_ref = var_Fin_ref[~var_Fin_ref['fuel_mtoe'].duplicated()]

    ## Calculate the final energy consumption for each commodity in Mtoe for the tested scenario
    var_Fin_scen = pd.read_csv(file_path_scen + 'VAR_FIn_' + run_name_scen + '.csv', sep = ',')
    var_Fin_scen = var_Fin_scen[var_Fin_scen['1'].isin(commodity(file_path_scen,run_name_scen))]
    var_Fin_scen['fuel'] = var_Fin_scen['1'].astype(str).str[-3:]
    reverse_mapping = {item: key for key, values in dict_nrg.items() for item in values}
    var_Fin_scen['fuel_grp'] = var_Fin_scen['fuel'].map(reverse_mapping)
    var_Fin_scen['group'] = var_Fin_scen['fuel_grp'].str.cat(var_Fin_scen['3'].astype(str), sep='_')
    var_Fin_scen['fuel_mtoe'] = var_Fin_scen.groupby('group')['8'].transform('sum')*0.023
    var_Fin_scen = var_Fin_scen[~var_Fin_scen['fuel_mtoe'].duplicated()]


    ## Operation on the dataframe to have a sorted cross table (reference scenario)
    pivot_df1 = var_Fin_ref.pivot(index='3', columns='fuel_grp', values='fuel_mtoe')
    column_sums = pivot_df1.sum(skipna=True)
    sorted_columns = column_sums.sort_values(ascending=False)
    sorted_df1 = pivot_df1.reindex(sorted_columns.index, axis=1).fillna(0)
    percentages1 = sorted_df1.div(sorted_df1.sum(axis=1), axis=0) * 100

    ## Operation on the datafrale to have a sorted cross table (tested scenario)
    pivot_df2 = var_Fin_scen.pivot(index='3', columns='fuel_grp', values='fuel_mtoe')
    sorted_df2 = pivot_df2.reindex(sorted_columns.index, axis=1).fillna(0)
    percentages2 = sorted_df2.div(sorted_df2.sum(axis=1), axis=0) * 100
    

    ## function to make a two bar plots: in value and in percentage
    def plot_stacked_bars_with_differentiation(df1, df2,df_perc1,df_perc2):
    
        n_years1 = len(df1.index)
        n_years2 = len(df2.index)
        
        diff_index = abs(n_years1 - n_years2)

        if n_years1 > n_years2:
            indices1 = np.arange(n_years1)
            indices2 = np.arange(diff_index,n_years2+diff_index)
            plt_indices = indices1
            years = df1.index
        else:

            indices1 = np.arange(diff_index,n_years1+diff_index)
            indices2 = np.arange(n_years2)
            plt_indices = indices2
            years = df2.index

        bar_width = 0.35

        values1 = np.linspace(0, 1, 20)
        values2 = np.linspace(0, 1, 12)
        cmap1 = plt.cm.tab20
        cmap2 = plt.cm.tab20b
        colors1 = cmap1(values1)
        colors2 = cmap2(values2)
        combined_colors = np.vstack((colors1, colors2))

        fig, ax = plt.subplots(1, 2, figsize=(24, 10))

        bottom_df1 = np.zeros(n_years1)
        for i, country in enumerate(df1.columns):
            ax[0].bar(indices1 - bar_width/2, df1[country], bar_width, bottom=bottom_df1, color=combined_colors[i], edgecolor='black',label=country)
            bottom_df1 += df1[country]

        bottom_df2 = np.zeros(n_years2)
        for i, country in enumerate(df2.columns):
            ax[0].bar(indices2 + bar_width/2, df2[country], bar_width, bottom=bottom_df2, color=combined_colors[i],hatch='/', edgecolor='black')
            bottom_df2 += df2[country]


        ax[0].set_xlabel('Year', fontsize=22)
        ax[0].set_ylabel('Mtoe', fontsize=22)
        ax[0].set_title(f'Gross Final Energy consumption', fontsize=22)
        ax[0].set_xticks(plt_indices)
        ax[0].set_xticklabels(years, fontsize=18) 
        ax[0].tick_params(axis='y', labelsize=18) 
        first_legend = ax[0].legend(fontsize=14, fancybox=True, shadow=True, ncol=2,loc='lower right')
        ax[0].add_artist(first_legend)

        empty_patch = Patch(facecolor='white', edgecolor='black', label='Reference')
        hashed_patch = Patch(facecolor='white', edgecolor='black', hatch='//', label='Scenario')
        second_legend = ax[0].legend(handles=[empty_patch, hashed_patch], labels=['Reference', 'Scenario'],
                                fontsize=14, fancybox=True, shadow=True, loc='lower center')
        ax[0].add_artist(second_legend)
        ax[0].grid(True)
        ax[0].set_axisbelow(True)


        bottom_df1 = np.zeros(n_years1)
        for i, country in enumerate(df_perc1.columns):
            ax[1].bar(indices1 - bar_width/2, df_perc1[country], bar_width, bottom=bottom_df1, color=combined_colors[i], edgecolor='black',label=country)
            bottom_df1 += df_perc1[country]

        bottom_df2 = np.zeros(n_years2)
        for i, country in enumerate(df_perc2.columns):
            ax[1].bar(indices2 + bar_width/2, df_perc2[country], bar_width, bottom=bottom_df2, color=combined_colors[i],hatch='/', edgecolor='black')
            bottom_df2 += df_perc2[country]

        ax[1].set_xlabel('Year', fontsize=22)
        ax[1].set_ylabel('%', fontsize=22)
        ax[1].set_title(f'Gross Final Energy consumption %', fontsize=22)
        ax[1].set_xticks(plt_indices)
        ax[1].set_xticklabels(years, fontsize=18) 
        ax[1].tick_params(axis='y', labelsize=18)
        first_legend = ax[1].legend(fontsize=14, fancybox=True, shadow=True, ncol=2,loc='lower right')
        ax[1].add_artist(first_legend) 

        empty_patch = Patch(facecolor='white', edgecolor='black', label='Reference')
        hashed_patch = Patch(facecolor='white', edgecolor='black', hatch='//', label='Scenario')
        second_legend = ax[1].legend(handles=[empty_patch, hashed_patch], labels=['Reference', 'Scenario'],
                                fontsize=14, fancybox=True, shadow=True, loc='lower center')
        ax[1].add_artist(second_legend)
        ax[1].grid(True)
        ax[1].set_axisbelow(True)
        plt.savefig(output_folder + f'final_energy_consumption.pdf'
                            , format ='pdf'
                            ,  bbox_inches='tight')
        return plt
    f= plot_stacked_bars_with_differentiation(sorted_df1,sorted_df2,percentages1,percentages2)
    return f

