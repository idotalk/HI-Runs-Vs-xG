import os
import pandas as pd
from datetime import datetime, timedelta
import json

"""
Use this module in order to pass raw data into a cleaner pipeline.
This module assumes the following folders structure:
Data
|- GPS
|   |- Season 1
|   |   |- Game 1 folder
|   |   |   |- Player 1 GPS csv
|   |   |   |- Player 2 GPS csv
|   |   |   |- ...
|   |   |- Game 2 folder
|   |   |   |- Player 1 GPS csv
|   |   |   |- Player 2 GPS csv
|   |   |   |- ...
|   |   |- ...
|   |- Season 2
|   |...
|- OPTA
|   |- Season 1
|   |   |- OPTA data Files
|   |- Season 2
|   |- ...
|- Lineups & Subs
|   |- Season 1
|   |   |- data files
|   |- Season 2
|   |- ...
|- Metadata.csv


In addition, the module assumes GPS data folders holds the same name as the OPTA file for that match.
Lineups and Subs files hold the same name with the addition of "-lineup" | "-subtitutes" at the end of the file name.
GPS game folder's name pattern assumed: "year-month-day-monthString day, year-RawDataExtended.csv"
Players GPS data file's name pattern assumed: "year-month-day-player_name-Entire-Session.csv"
"""


# Change these paths accordingly to your data paths
metadata_path = r"C:\Users\idota\AIproject\data\games_metadata.csv"
base_OPTA_folder_path = r"C:\Users\idota\AIproject\data\OPTA"
base_lineups_and_subs_folder_path = r"C:\Users\idota\AIproject\data\linups&subs"
base_GPS_folder_path = r"C:\Users\idota\AIproject\data\GPS"

metadata_df = pd.read_csv(metadata_path)
game_metadata = None
subs_df = None

def minute_to_time(minute, first_half_start, second_half_start):
    if minute > 45:
        minute = minute - 45
        time = datetime.strptime(second_half_start, "%H:%M:%S") + timedelta(minutes=minute)
        return time.strftime("%H:%M:%S")
    else:
        time = datetime.strptime(first_half_start, "%H:%M:%S") + timedelta(minutes=minute)
        return time.strftime("%H:%M:%S")
    
def clean_player_file(player_data: str , lineup: list):
    player_name = player_data.split("-")[-3]
    day = int(player_data.split("-")[-4])
    month = int(player_data.split("-")[-5])
    year = int(player_data.split('\\')[-1].split('-')[0])

    player_df = pd.read_csv(player_data)
    if str(year) in player_df['Time'].values[0]:
        print(f"File {player_data} already cleaned. Skipping...")
        return
    player_df['Time'] = player_df['Time'].apply(lambda t: datetime.strptime(t, "%H:%M:%S.%f").replace(year=year, month=month, day=day))

    starter = True if player_name in lineup else False 
    if not starter:
        if player_name not in subs_df['In Player'].unique():
            # player didn't play
            os.remove(player_data)
            return
        else:
            # player subbed in
            sub_in_minute = int(subs_df.loc[subs_df['In Player'] == player_name, 'Minute'].values[0])
            sub_out_minute = None
            if player_name in subs_df['Out Player'].unique():
                sub_out_minute = int(subs_df.loc[subs_df['Out Player'] == player_name, 'Minute'].values[0])
            sub_in_time = minute_to_time(sub_in_minute,game_metadata['start_csv_time'].values[0],game_metadata['second_half_start_csv_time'].values[0])
            start_hour, start_minute, start_second = map(int, sub_in_time.split(':'))
            sub_out_time = game_metadata['second_half_finish_csv_time'].values[0]
            end_hour, end_minute, end_second = map(int, sub_out_time.split(':'))
            if sub_out_minute != None:
                sub_out_time = minute_to_time(sub_out_minute,game_metadata['start_csv_time'].values[0],game_metadata['second_half_start_csv_time'].values[0])
                end_hour, end_minute, end_second = map(int, sub_out_time.split(':'))
            
            player_df = player_df[(player_df['Time'] >= datetime(year,month,day, int(start_hour),int(start_minute),int(start_second)))]
            player_df = player_df[(player_df['Time'] <= datetime(year,month,day, int(end_hour),int(end_minute),int(end_second)))]
    else:
        if player_name in subs_df['Out Player'].unique():
            # player subbed out
            sub_out_minute = int(subs_df.loc[subs_df['Out Player'] == player_name, 'Minute'].values[0])
            sub_out_time = minute_to_time(sub_out_minute,game_metadata['start_csv_time'].values[0],game_metadata['second_half_start_csv_time'].values[0])
            start_hour, start_minute, start_second = map(int, game_metadata['start_csv_time'].values[0].split(':'))
            end_hour, end_minute, end_second = map(int, sub_out_time.split(':'))
            
            player_df = player_df[ 
            (player_df['Time'] >= datetime(year,month,day, int(start_hour),int(start_minute),int(start_second))) &
            (player_df['Time'] < datetime(year,month,day, int(end_hour), int(end_minute), int(end_second))) 
            ]
        else:
            # played all game
            start_hour, start_minute, start_second = map(int, game_metadata['start_csv_time'].values[0].split(':'))
            end_hour, end_minute, end_second = map(int, game_metadata['second_half_finish_csv_time'].values[0].split(':'))
            player_df = player_df[ 
            (player_df['Time'] >= datetime(year,month,day, int(start_hour),int(start_minute),int(start_second))) &
            (player_df['Time'] <= datetime(year,month,day, int(end_hour), int(end_minute), int(end_second))) 
            ]
    
    # clean half time
    first_half_end_hour, first_half_end_minute, first_half_end_second = map(int, game_metadata['first_half_finish_csv_time'].values[0].split(':'))
    second_half_start_hour, second_half_start_minute, second_half_start_second = map(int, game_metadata['second_half_start_csv_time'].values[0].split(':'))
    player_df = player_df[ 
        (player_df['Time'] >= datetime(year,month,day, int(second_half_start_hour),int(second_half_start_minute),int(second_half_start_second))) |
        (player_df['Time'] <= datetime(year,month,day, int(first_half_end_hour), int(first_half_end_minute), int(first_half_end_second))) 
    ]
    player_df.to_csv(player_data, index=False)

def clean_game_folder(game_folder_path: str, season: str):
    lineup_path = os.path.join(base_lineups_and_subs_folder_path, season)
    subs_path = os.path.join(base_lineups_and_subs_folder_path, season)
    game_folder_name = os.path.basename(game_folder_path)
    lineup_file = os.path.join(lineup_path, f"{game_folder_name}-lineup.json")
    subs_file = os.path.join(subs_path, f"{game_folder_name}-substitutes.csv")
    if not os.path.exists(lineup_file) or not os.path.exists(subs_file):
        print(f"Lineup or subs file missing for game {game_folder_name}. Skipping...")
        return
    with open(lineup_file, 'r') as f:
        lineup = json.load(f)
    day = int(game_folder_path.split('\\')[-1].split('-')[2])
    month = int(game_folder_path.split('\\')[-1].split('-')[1])
    year = int(game_folder_path.split('\\')[-1].split('-')[0])
    date_string = f"{year}-{month:02d}-{day:02d}-"
    global subs_df
    subs_df = pd.read_csv(subs_file)
    global game_metadata
    game_metadata = metadata_df[metadata_df['game_folder_name'].str.contains(date_string)]
    for player_file in os.listdir(game_folder_path):
        if player_file.endswith("-Entire-Session.csv"):
            player_file_path = os.path.join(game_folder_path, player_file)
            clean_player_file(player_file_path, lineup)

def drop_irelevant_columns():
    for dirpath, dirnames, filenames in os.walk(base_GPS_folder_path):
        for filename in filenames:
            if filename.endswith("-Entire-Session.csv"):
                file_path = os.path.join(dirpath, filename)
                df = pd.read_csv(file_path)
                if "Heart Rate (bpm)" in df.columns:
                    df = df.drop(columns=["Heart Rate (bpm)"])
                if "Hacc" in df.columns:
                    df = df.drop(columns=["Hacc"])
                if "Hdop" in df.columns:
                    df = df.drop(columns=["Hdop"])
                if "Quality of Signal" in df.columns:
                    df = df.drop(columns=["Quality of Signal"])
                if "No. of Satellites" in df.columns:
                    df = df.drop(columns=["No. of Satellites"])
                df.to_csv(file_path, index=False)

def clean_red_cards():
    game_metadata = pd.read_csv(metadata_path)
    for _, row in game_metadata.iterrows():
        if pd.isna(row['red cards']):  
            continue
        player, time = row['red cards'].split('|')
        game_name = row['game_folder_name']
        day = int(game_name.split('-')[2])
        month = int(game_name.split('-')[1])    
        year = int(game_name.split('-')[0])
        season = "ipl2324"
        if year >= 2024 and month > 5 or year == 2025:
            season = "ipl2425"
        
        game_folder_path = os.path.join(base_GPS_folder_path, season, game_name)
        if not os.path.exists(game_folder_path):
            print(f"Game folder {game_folder_path} does not exist. Skipping...")
            continue
        player_file = os.path.join(game_folder_path, f"{year}-{month:02d}-{day:02d}-{player}-Entire-Session.csv")
        if not os.path.exists(player_file):
            print(f"Player file {player_file} does not exist. Skipping...")
            continue    
        df = pd.read_csv(player_file)
        df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S.%f')
        time_hour, time_minute, time_second = map(int, time.split(':'))
        df = df[df['Time'] < datetime(year,month,day, int(time_hour),int(time_minute),int(time_second))]
        df.to_csv(player_file, index=False)

# Deprecated function, kept for reference
def clean_before_and_after():
    for dirpath, dirnames, filenames in os.walk(base_GPS_folder_path):
        for filename in filenames:
            if filename.endswith("-Entire-Session.csv"):
                file_path = os.path.join(dirpath, filename)
                df = pd.read_csv(file_path)
                day = int(file_path.split('\\')[-1].split('-')[2])
                month = int(file_path.split('\\')[-1].split('-')[1])
                year = int(file_path.split('\\')[-1].split('-')[0])
                date_string = f"{year}-{month:02d}-{day:02d}-"
                game_metadata = metadata_df[metadata_df['game_folder_name'].str.contains(date_string)]
                if game_metadata.empty:
                    print(f"No metadata found for file {file_path}. Skipping...")
                    continue
                start_time_str = game_metadata['start_csv_time'].values[0]
                finish_time_str = game_metadata['second_half_finish_csv_time'].values[0]
                start_hour, start_minute, start_second = map(int, start_time_str.split(':'))
                finish_hour, finish_minute, finish_second = map(int, finish_time_str.split(':'))
                df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S.%f')                
                df = df[ 
                    (df['Time'] >= datetime(year,month,day, int(start_hour),int(start_minute),int(start_second))) &
                    (df['Time'] <= datetime(year,month,day, int(finish_hour), int(finish_minute), int(finish_second))) 
                ]
                df.to_csv(file_path, index=False)

def clean_pipeline():
    for season in os.listdir(base_GPS_folder_path):
        print(f"Processing season: {season}")
        season_path = os.path.join(base_GPS_folder_path, season)
        if os.path.isdir(season_path):
            for game_folder in os.listdir(season_path):
                game_folder_path = os.path.join(season_path, game_folder)
                if os.path.isdir(game_folder_path):
                    print(f"Cleaning game folder: {game_folder_path}")
                    clean_game_folder(game_folder_path, season)
    drop_irelevant_columns()
    clean_red_cards()



