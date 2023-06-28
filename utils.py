# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import click
import os
import pyperclip

def get_log_header_info(log_df):
    """
    Returns the header of the log dataframe.
    """
    # set the header df to be the first 3 rows
    df_header = log_df.iloc[:3]

    return df_header

def get_experiment_info_string(df_header):
    """
    Returns a string containing the experiment information from the log dataframe header.
    """
    # get the header information, the first column contains P, I, D, and the second column contains the values, the third column contains LPS, Size X, and Size Y, and the fourth column contains the values, the fifth column contains Z Set Point, Offset X, Offset Y, and the sixth column contains the values
    header_values = df_header.iloc[:,1].apply(pd.to_numeric).tolist()
    header2_values = df_header.iloc[:,3].apply(pd.to_numeric).tolist()
    header3_values = df_header.iloc[:,5].apply(pd.to_numeric).tolist()

    # create the experiment title string. It should include the P, I, D parameter values in scientific notation, the LPS, Size X, and Size Y values, and the Z Set Point, Offset X, and Offset Y values
    title_string = '$K_P$ = {:.1e}, $K_I$ = {:.1e}, $K_D$ = {:.1e}, $LPS$ = {:.2f}, $L_X$ = {:d}~$\\mu m$, $L_Y$ = {:d}~$\\mu m$, $r(t)$ = {:.2f} V, $\\delta_X$ = {:.1f}~$\\mu m$, $\\delta_Y$ = {:.1f}'.format(
        header_values[0], header_values[1], header_values[2],
        header2_values[0], int(header2_values[1]/1000), int(header2_values[2]/1000),
        header3_values[0], header3_values[1]/1000, header3_values[2]/1000
    )

    return title_string