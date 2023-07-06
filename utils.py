# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import librosa as lb
import os
from scipy.io.wavfile import write

def read_afm_log_csv(filename):
    """
    Reads the log CSV file and returns a pandas dataframe.
    """
    # specify the max column length
    max_cols = get_max_column_length(filename)

    # read the data from the CSV file
    df = pd.read_csv(filename,header=None,names=range(max_cols))

    # get the header of the log dataframe
    df_header = get_log_header_info(df)

    # set the column names to be the fourth row
    df.columns = df.iloc[3,:]

    # drop the first 4 rows
    df = df.iloc[4:]

    # reset the index
    df = df.reset_index(drop=True)

    # convert the data to numeric
    df = df.apply(pd.to_numeric)

    return df, df_header

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

def get_max_column_length(log_csv_file_path):
    # read the fourth row of the csv file, which contains the column names
    with open(log_csv_file_path, 'r') as f:
        # read the fourth row
        row = f.readlines()[3]
    
    # split the row by commas
    row_split = row.split(',')

    # get the length of the row
    row_length = len(row_split)

    return row_length

def plot_spectrogram(log_csv_file_path, signal_type, save_audio_flag, sampling_rate, f_max, spectrogram_type, window_size, n_mels):
    # read the afm log csv file
    log_df, df_header = read_afm_log_csv(log_csv_file_path)

    # get the experiment information string
    title_string = get_experiment_info_string(df_header)

    # print the column names
    print(f'\n\n Column names: {log_df.columns}\n\n')

    # Find the column index corresponding to the signal type from the column names
    signal_type_index = log_df.columns.get_loc(signal_type)

    # get the signal data according to the signal type
    signal_data = log_df.iloc[:,signal_type_index]

    # get the signal data as a numpy array
    signal_data_np = signal_data.to_numpy()

    # if length of signal is less than the sample rate, repeat the signal until it is equal to the sample rate
    if len(signal_data_np) < sampling_rate:
        # get the number of times to repeat the signal
        num_repeats = int(sampling_rate/len(signal_data_np))

        # repeat the signal
        signal_data_np = np.tile(signal_data_np, num_repeats)

        # get the length of the signal
        signal_length = len(signal_data_np)

        # chop the signal
        signal_data_np = signal_data_np[:sampling_rate]
    
    # if save audio flag is true, save the audio file
    if save_audio_flag:
        # specify the name of the audio file by getting the base name of the log csv file and appending .wav and incorporating the signal type into the name by using the signal type index value
        audio_file_name = os.path.basename(log_csv_file_path).split('.')[0] + '-' + f'[signalColumn-{signal_type_index}]' + '.wav'

        # get the directory of the log csv file
        directory = os.path.dirname(log_csv_file_path)

        # specify the audio file path using the directory and the audio file name
        audio_file_path = os.path.join(directory, audio_file_name)

        # write the audio file
        write(audio_file_path, sampling_rate, signal_data_np)

        # print sucess message
        print(f'\n\n Audio file {audio_file_name} saved successfully at {directory}!\n\n')

    # plot the spectrogram
    spectrogram = signal2spec(signal_data_np,sampling_rate,plot_flag=True, n_mels=n_mels, f_max=f_max, spectrogram_type=spectrogram_type, window_size=window_size)


def signal2spec(signal: np.ndarray, sample_rate: int, plot_flag=False, window_size=2048, zero_padding_factor=1,
             window_type='hann', gain_db=0.0, range_db=80.0, high_boost_db=0.0, f_min=0, f_max=20000, n_mels=1024, spectrogram_type='mel'):
    """
    Convert a signal to a mel-scaled spectrogram.

    Args:
        signal (np.ndarray): The input signal as a NumPy array.
        sample_rate (int): The sample rate of the input signal.
        plot_flag (bool, optional): Whether to plot the mel-scaled spectrogram. Defaults to False.
        window_size (int, optional): The size of the FFT window to use. Defaults to 2048.
        zero_padding_factor (int, optional): The amount of zero-padding to use in the FFT. Defaults to 1.
        window_type (str, optional): The type of window function to use in the FFT. Defaults to 'hann'.
        gain_db (float, optional): The gain to apply to the audio signal in decibels. Defaults to 0.0.
        range_db (float, optional): The range of the mel-scaled spectrogram in decibels. Defaults to 80.0.
        high_boost_db (float, optional): The amount of high-frequency boost to apply to the mel-scaled spectrogram in decibels. Defaults to 0.0.
        f_min (int, optional): The minimum frequency to include in the spectrogram (Hz). Defaults to 0.
        f_max (int, optional): The maximum frequency to include in the spectrogram (Hz). Defaults to 20000.
        n_mels (int, optional): The number of mel frequency bins to include in the spectrogram. Defaults to 256.

    Returns:
        np.ndarray: The mel-scaled spectrogram.
    """

    # Apply gain to the audio signal
    signal = lb.util.normalize(signal) * lb.db_to_amplitude(gain_db)

    # Compute the mel-scaled spectrogram
    fft_size = window_size * zero_padding_factor
    hop_length = window_size // 2
    window = lb.filters.get_window(window_type, window_size, fftbins=True)
    spectrogram = np.abs(lb.stft(signal, n_fft=fft_size, hop_length=hop_length, window=window))**2

    if spectrogram_type == "mel":
        spectrogram = lb.feature.melspectrogram(S=spectrogram, sr=sample_rate, n_mels=n_mels,
                                                    fmax=f_max, htk=True, norm=None)
    spectrogram = lb.power_to_db(spectrogram, ref=np.max)

    # Apply range and high boost to the mel-scaled spectrogram
    spectrogram = np.clip(spectrogram, a_min=-range_db, a_max=None)
    spectrogram = spectrogram + high_boost_db

    # Plot the mel-scaled spectrogram if plot_flag is True
    if plot_flag:
        # create a 2 x 1 subplot with top subplot for the signal and bottom subplot for the spectrogram
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # plot the signal
        ax1.plot(signal)
        ax1.set_title('Signal')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Amplitude')

        # plot the spectrogram
        specshow = lb.display.specshow(spectrogram, x_axis='time', y_axis='mel', sr=sample_rate, fmin=f_min, fmax=f_max, hop_length=hop_length, cmap='jet', ax=ax2, vmin=-range_db, vmax=spectrogram.max() + high_boost_db)
        
        fig.colorbar(specshow, ax=ax2, format='%+2.0f dB')
        ax2.set_title('Spectrogram (dB)')

        plt.tight_layout()
        plt.show()

    return spectrogram