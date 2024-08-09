#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap


def func_H2_new_cap_process(file_path_scen,file_path_ref, run_name_scen,run_name_ref, output_folder, called = False):
    cap_new = pd.read_csv(file_path_ref + 'Cap_New_' + run_name_ref + '.csv', sep = ',')
    new_cap_ref = cap_new[(cap_new['7'].str.contains('INSTCAP')) & (cap_new['2'].str.contains('H2prd'))]
    new_cap_ref['group'] = new_cap_ref['3'].astype(str).str.cat(new_cap_ref['2'].astype(str), sep='_')
    new_cap_ref = new_cap_ref.sort_values(by='3', ascending=True)
    new_cap_ref['sum'] = new_cap_ref.groupby('group')['8'].transform('sum')
    new_cap_ref = new_cap_ref[~new_cap_ref['group'].duplicated()]
    new_cap_ref['new_capacity'] = new_cap_ref.groupby('2')['sum'].transform('cumsum')
    
    cap_new = pd.read_csv(file_path_scen + 'Cap_New_' + run_name_scen + '.csv', sep = ',')
    new_cap_scen = cap_new[(cap_new['7'].str.contains('INSTCAP')) & (cap_new['2'].str.contains('H2prd'))]
    new_cap_scen['group'] = new_cap_scen['3'].astype(str).str.cat(new_cap_scen['2'].astype(str), sep='_')
    new_cap_scen = new_cap_scen.sort_values(by='3', ascending=True)
    new_cap_scen['sum'] = new_cap_scen.groupby('group')['8'].transform('sum')
    new_cap_scen = new_cap_scen[~new_cap_scen['group'].duplicated()]
    new_cap_scen['new_capacity'] = new_cap_scen.groupby('2')['sum'].transform('cumsum')

    substring_color_map = {
        'Elc': 'yellowgreen',  
        ('Gas','CCS'): 'royalblue',
        'Gas':'grey'
    }

    def get_color(value):
        for substrings, color in substring_color_map.items():
            if all(substring in value for substring in substrings):
                return color
        return 'grey'

    new_cap_ref = new_cap_ref.sort_values(by='new_capacity',ascending=False)
    new_cap_scen = new_cap_scen.sort_values(by='new_capacity',ascending=False)

    new_cap_ref['color'] = new_cap_ref['2'].apply(get_color)
    new_cap_scen['color'] = new_cap_scen['2'].apply(get_color)
    

    pivot_df = new_cap_ref.pivot(index='3', columns='2', values='new_capacity')
    column_sums = pivot_df.sum(skipna=True)
    sorted_columns1 = column_sums.sort_values(ascending=False)
    sorted_df1 = pivot_df.reindex(sorted_columns1.index, axis=1).fillna(0)

    pivot_df = new_cap_scen.pivot(index='3', columns='2', values='new_capacity')
    column_sums = pivot_df.sum(skipna=True)
    sorted_columns2 = column_sums.sort_values(ascending=False)
    sorted_df2 = pivot_df.reindex(sorted_columns2.index, axis=1).fillna(0)

    cmap1 = [get_color(val) for val in sorted_columns1.index]
    cmap2 = [get_color(val) for val in sorted_columns2.index]

    def plot_stacked_bars_with_differentiation(df1, df2):
        fig, ax = plt.subplots(figsize=(12, 8))
        
        n_years1 = len(df1.index)
        n_years2 = len(df2.index)
        
        diff_index = abs(n_years1 - n_years2)

        if n_years1 > n_years2:
            indices1 = np.arange(n_years1)
            indices2 = np.arange(diff_index,n_years2+diff_index)
            plt_indices = indices1
        else:
            indices1 = np.arange(diff_index,n_years1+diff_index)
            indices2 = np.arange(n_years2)
            plt_indices = indices2

        bar_width = 0.35

        bottom_df1 = np.zeros(n_years1)
        for i, process in enumerate(df1.columns):
            ax.bar(indices1 - bar_width/2, df1[process], bar_width, bottom=bottom_df1, color=cmap1[i],edgecolor='black', label=process)
            bottom_df1 += df1[process]
        
        bottom_df2 = np.zeros(n_years2)
        for i, process in enumerate(df2.columns):
            ax.bar(indices2 + bar_width/2, df2[process], bar_width, bottom=bottom_df2, color=cmap2[i], hatch='/', edgecolor='black')
            bottom_df2 += df2[process]
        
        ax.set_xlabel('Year', fontsize=22)
        ax.set_ylabel('GW', fontsize=22)
        ax.set_title('Capacity installed by process', fontsize=22)
        ax.set_xticks(plt_indices)
        ax.set_xticklabels(df2.index, fontsize=18)
        ax.tick_params(axis='y', labelsize=18)
        first_legend = ax.legend(fontsize=14, fancybox=True, shadow=True, ncol=1,loc='upper left')
        ax.add_artist(first_legend)

        empty_patch = Patch(facecolor='white', edgecolor='black', label='Reference')
        hashed_patch = Patch(facecolor='white', edgecolor='black', hatch='//', label='Scenario')
        second_legend = ax.legend(handles=[empty_patch, hashed_patch], labels=['Reference', 'Scenario'],
                                fontsize=14, fancybox=True, shadow=True, bbox_to_anchor = (0.7, 1))
        ax.add_artist(second_legend)
        ax.grid(True)
        ax.set_axisbelow(True)
        return plt
        # plt.savefig(output_folder + 'H2new_capcity_by_process.pdf'
        #         , format ='pdf'
        #         ,  bbox_inches='tight')
        return fig
    f = plot_stacked_bars_with_differentiation(sorted_df1, sorted_df2)
    return f
