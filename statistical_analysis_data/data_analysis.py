import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import os

def load_df(file_path):
    df = pd.read_csv(file_path, index_col=0)
    return df

def show_pearson_corr(df, target_column):
    corr_matrix = df.corr(method='pearson')
    plt.figure(figsize=(10, 8))
    plt.title('Pearson Correlation Matrix', fontsize=16)
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True)
    plt.show()

    if target_column in corr_matrix.columns:
        target_corr = corr_matrix[target_column].drop(target_column)
        print(f'Pearson correlation with {target_column}:\n{target_corr}')
    else:
        print(f'Target column {target_column} not found in DataFrame.')

