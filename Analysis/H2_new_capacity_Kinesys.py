#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

def func_H2_new_cap(file_path_scen,file_path_ref, run_name_scen,run_name_ref, output_folder):

    cap_new = pd.read_csv(file_path_ref + 'Cap_New_' + run_name_ref + '.csv', sep = ',')
    new_cap_ref = cap_new[(cap_new['7'].str.contains('INSTCAP')) & (cap_new['2'].str.contains('H2prd'))]
    new_cap_ref['group'] = new_cap_ref['3'].astype(str).str.cat(new_cap_ref['4'].astype(str), sep='_')
    new_cap_ref = new_cap_ref.sort_values(by='3', ascending=True)
    new_cap_ref['sum'] = new_cap_ref.groupby('group')['8'].transform('sum')
    new_cap_ref = new_cap_ref[~new_cap_ref['group'].duplicated()]
    new_cap_ref['new_capacity'] = new_cap_ref.groupby('4')['sum'].transform('cumsum')

    cap_new = pd.read_csv(file_path_scen + 'Cap_New_' + run_name_scen + '.csv', sep = ',')
    new_cap_scen = cap_new[(cap_new['7'].str.contains('INSTCAP')) & (cap_new['2'].str.contains('H2prd'))]
    new_cap_scen['group'] = new_cap_scen['3'].astype(str).str.cat(new_cap_scen['4'].astype(str), sep='_')
    new_cap_scen = new_cap_scen.sort_values(by='3', ascending=True)
    new_cap_scen['sum'] = new_cap_scen.groupby('group')['8'].transform('sum')
    new_cap_scen = new_cap_scen[~new_cap_scen['group'].duplicated()]
    new_cap_scen['new_capacity'] = new_cap_scen.groupby('4')['sum'].transform('cumsum')

    pivot_df = new_cap_scen.pivot(index='3', columns='4', values='new_capacity')
    column_sums = pivot_df.sum(skipna=True)
    sorted_columns = column_sums.sort_values(ascending=False)
    sorted_df1 = pivot_df.reindex(sorted_columns.index, axis=1).fillna(0)

    pivot_df = new_cap_ref.pivot(index='3', columns='4', values='new_capacity')
    sorted_df2 = pivot_df.reindex(sorted_columns.index, axis=1).fillna(0)

    def plot_stacked_bars_with_differentiation(df1, df2):
        fig, ax = plt.subplots(figsize=(12, 8))
        
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
        values2 = np.linspace(0, 1, 9)

        cmap1 = plt.cm.tab20
        cmap2 = plt.cm.Set3


        colors1 = cmap1(values1)
        colors2 = cmap2(values2)

        combined_colors = np.vstack((colors1, colors2))

        bottom_df1 = np.zeros(n_years1)
        for i, country in enumerate(df1.columns):
            ax.bar(indices1 - bar_width/2, df1[country], bar_width, bottom=bottom_df1, color=combined_colors[i],edgecolor='black', label=country)
            bottom_df1 += df1[country]

        bottom_df2 = np.zeros(n_years2)
        for i, country in enumerate(df2.columns):
            ax.bar(indices2 + bar_width/2, df2[country], bar_width, bottom=bottom_df2, color=combined_colors[i], hatch='/', edgecolor='black')
            bottom_df2 += df2[country]
        
        ax.set_xlabel('Year', fontsize=22)
        ax.set_ylabel('GW', fontsize=22)
        ax.set_title('Capacity installed by region', fontsize=22)
        ax.set_xticks(plt_indices)
        ax.set_xticklabels(years, fontsize=18)
        ax.tick_params(axis='y', labelsize=18)
        first_legend = ax.legend(fontsize=14, fancybox=True, shadow=True, ncol=2,loc='upper left')
        ax.add_artist(first_legend)

        empty_patch = Patch(facecolor='white', edgecolor='black', label='Reference')
        hashed_patch = Patch(facecolor='white', edgecolor='black', hatch='//', label='Scenario')
        second_legend = ax.legend(handles=[empty_patch, hashed_patch], labels=['Reference', 'Scenario'],
                                fontsize=14, fancybox=True, shadow=True, bbox_to_anchor = (0.7, 1))
        ax.add_artist(second_legend)
        ax.grid(True)
        ax.set_axisbelow(True)
        plt.savefig(output_folder + 'H2new_capacity_by_region.pdf'
                , format ='pdf'
                ,  bbox_inches='tight')
        return fig
    f = plot_stacked_bars_with_differentiation(sorted_df2, sorted_df1)
    return f

