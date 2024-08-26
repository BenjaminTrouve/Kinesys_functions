#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

def func_H2_production_by_process(file_path_scen,file_path_ref, run_name_scen,run_name_ref, output_folder):

    var_Fout = pd.read_csv(file_path_ref + 'VAR_FOut_' + run_name_ref + '.csv', sep = ',')
    H2_prod_ref = var_Fout[(var_Fout['1'] == 'HH2') & (~var_Fout['2'].str.contains('TU_H2'))]
    H2_prod_ref = H2_prod_ref[H2_prod_ref['2'] != 'H2_STG']
    H2_prod_ref = H2_prod_ref[H2_prod_ref['2'] != 'GlbMarket_HH2']
    H2_prod_ref['group'] = H2_prod_ref['2'].astype(str).str.cat(H2_prod_ref['3'].astype(str), sep='_')
    H2_prod_ref['8'] = pd.to_numeric(H2_prod_ref['8'])
    H2_prod_ref['3'] = pd.to_numeric(H2_prod_ref['3'])
    H2_prod_ref['MtH2'] = H2_prod_ref.groupby('group')['8'].transform('sum')/120
    H2_prod_ref = H2_prod_ref[~H2_prod_ref['group'].duplicated()]


    var_Fout = pd.read_csv(file_path_scen + 'VAR_FOut_' + run_name_scen + '.csv', sep = ',')
    H2_prod_scen = var_Fout[(var_Fout['1'] == 'HH2') & (~var_Fout['2'].str.contains('TU_H2'))]
    H2_prod_scen = H2_prod_scen[H2_prod_scen['2'] != 'H2_STG']
    H2_prod_scen = H2_prod_scen[H2_prod_scen['2'] != 'GlbMarket_HH2']
    H2_prod_scen['group'] = H2_prod_scen['2'].astype(str).str.cat(H2_prod_scen['3'].astype(str), sep='_')
    H2_prod_scen['8'] = pd.to_numeric(H2_prod_scen['8'])
    H2_prod_scen['3'] = pd.to_numeric(H2_prod_scen['3'])
    H2_prod_scen['MtH2'] = H2_prod_scen.groupby('group')['8'].transform('sum')/120
    H2_prod_scen = H2_prod_scen[~H2_prod_scen['group'].duplicated()]


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
    
    H2_prod_ref = H2_prod_ref.sort_values(by='MtH2',ascending=False)
    H2_prod_scen = H2_prod_scen.sort_values(by='MtH2',ascending=False)

    H2_prod_ref['color'] = H2_prod_ref['2'].apply(get_color)
    H2_prod_scen['color'] = H2_prod_scen['2'].apply(get_color)

    pivot_df = H2_prod_ref.pivot(index='3', columns='2', values='MtH2')
    column_sums = pivot_df.sum(skipna=True)
    sorted_columns1 = column_sums.sort_values(ascending=False)
    sorted_df1 = pivot_df.reindex(sorted_columns1.index, axis=1).fillna(0)

    pivot_df = H2_prod_scen.pivot(index='3', columns='2', values='MtH2')
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
        ax.set_ylabel('MtH2/year', fontsize=22)
        ax.set_title('Production by process', fontsize=22)
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

        plt.savefig(output_folder + 'H2production_by_process.pdf'
                , format ='pdf'
                ,  bbox_inches='tight')
        return fig
    f = plot_stacked_bars_with_differentiation(sorted_df1, sorted_df2)
    return f
