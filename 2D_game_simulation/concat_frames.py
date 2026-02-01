import pandas as pd
import glob
from datetime import datetime
import stadium_projection


def concat_frames(csvs_files_path : str , stadium= None ,rows_to_load: int=None, time_begin: str=None, time_end: str=None,
                  output_path: str ='output.csv'):
    """
    Concatenate multiple CSV files containing player tracking data into a single DataFrame.
    
    :param csvs_files_path (str): The path to the directory containing the CSV files formatted as raw string "path/to/game/files\*.csv".
    
    :param rows_to_load (int): The number of rows to load from each CSV file. Default is all the rows.

    :param time_begin (str): A time range string to filter the data from the time onward, If provided. the format is "HH:MM:SS".

    :param time_end (str): A time range string to filter the data from the time vackward, If provided. the format is "HH:MM:SS".

    :param output_path (str): The path where the concatenated DataFrame will be saved as a CSV file. Default is 'output.csv'.
    
    :param stadium (tuple): A tuple (check stadiumProjection.py for known stadiums) containing the GPS coordinates of the stadium's center (latitude, longitude).

    return: 
    ----------
    A DataFrame containing the concatenated data with additional columns for player names ,rounded time and projected coordinates.
    
    """
    csv_files = glob.glob(csvs_files_path)
    df_list = []

    for file in csv_files:
        temp = load_player_csv_by_time(file, rows_to_load, time_begin, time_end)
        df_list.append(temp)

    df = pd.concat(df_list)
    df.sort_values(by=['RoundedTime', 'Player'], inplace=True)
    if stadium:
        df['xyCoords'] = df.apply(lambda row: stadium_projection.project_around_pitch_center(float(row['Lat']),float(row['Lon']),stadium),axis=1)
    df.to_csv(output_path)
    return df


def load_player_csv_by_time(file, rows_to_load, time_begin, time_end):
    playerName = file.split("-")[-3]
    day = int(file.split("-")[-4])
    month = int(file.split("-")[-5])
    year = int(file.split('\\')[-1].split('-')[0])
    temp = pd.read_csv(file, nrows=rows_to_load)
    temp['Player'] = playerName
    temp['Time'] = temp['Time'].apply(
        lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").replace(year=year, month=month, day=day))
    temp = temp[temp['Lat'] != 0]
    if time_begin is not None:
        start_hour, start_minute, start_second = map(int, time_begin.split(':'))
        temp = temp[(temp['Time'] > datetime(year, month, day, int(start_hour), int(start_minute), int(start_second)))]
    if time_end is not None:
        end_hour, end_minute, end_second = map(int, time_end.split(':'))
        temp = temp[(temp['Time'] < datetime(year, month, day, int(end_hour), int(end_minute), int(end_second)))]
    temp['RoundedTime'] = temp['Time'].dt.floor('s')
    temp = temp.sort_values('Time').drop_duplicates(subset='RoundedTime', keep='first')
    return temp

