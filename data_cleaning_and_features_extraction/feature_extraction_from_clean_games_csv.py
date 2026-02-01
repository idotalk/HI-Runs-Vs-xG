from datetime import timedelta
from concat_frames import *
from constants import ZONE_6_SPRINT_THRESHOLD, ZONE_5_SPRINT_THRESHOLD, POSITIONS_MAPPING
import glob
import pandas as pd
import os 
import math

acceleration_threshold = 3.0  # m/s² - acording to STATSports documentation

def get_season(game_folder_name: str):
    year = int(game_folder_name.split('-')[0])
    month = int(game_folder_name.split('-')[1])
    if year == 2025 or (year==2024 and month>=8):  
        return "ipl2425"
    else:
        return "ipl2324"

def get_half_times(metadata_file_path: str, game_folder_name: str):
    metadata_df = pd.read_csv(metadata_file_path)
    game_row = metadata_df[metadata_df['game_folder_name'] == game_folder_name].iloc[0]
    return (game_row['start_csv_time'], game_row['first_half_finish_csv_time'],
            game_row['second_half_start_csv_time'], game_row['second_half_finish_csv_time'])

def add_features_to_existing_csv(existing_csv_path: str, new_features_df: pd.DataFrame):
    existing_df = pd.read_csv(existing_csv_path, parse_dates=['interval_start'])
    existing_df.set_index('interval_start', inplace=True)
    combined_df = existing_df.join(new_features_df, how='left')
    xgCol = combined_df['TotalxG']
    combined_df = combined_df.drop(columns=['TotalxG'])
    combined_df['TotalxG'] = xgCol
    return combined_df

def get_game_features_csv(metadata_file_path: str, game_folder_path: str,opta_folder_path: str, summation_interval: int = 5):
    game_folder_name = game_folder_path.split('\\')[-1]
    year = int(game_folder_name.split('-')[0])
    month = int(game_folder_name.split('-')[1])
    day = int(game_folder_name.split('-')[2])
    first_half_start, first_half_end, second_half_start, second_half_end = get_half_times(
        metadata_file_path=metadata_file_path, game_folder_name=game_folder_name
    )
    csv_files = glob.glob(game_folder_path + r"\*.csv")
    role_features_dict = {role: [] for role in POSITIONS_MAPPING.values()}

    for file in csv_files:
        player_data = pd.read_csv(file)
        print(f"Processing file: {file}")
        position = file.split('\\')[-1].split('-')[3].split('_')[0]
        player_role = POSITIONS_MAPPING[position]
        player_data["Time"] = pd.to_datetime(player_data["Time"])
        player_data["TimeDiff"] = 0.01  # Time difference between rows in seconds

        # Process each half
        for half_start, half_end in [(first_half_start, first_half_end), (second_half_start, second_half_end)]:
            half_start = pd.to_datetime(half_start).replace(year=year,month=month,day=day)
            half_end = pd.to_datetime(half_end).replace(year=year,month=month,day=day)
            current_time = half_start

            while current_time < half_end:
                interval_end = current_time + timedelta(minutes=summation_interval)
                interval_end = min(interval_end, half_end)
                interval_index = player_data.index[(player_data["Time"] >= current_time) &
                                                   (player_data["Time"] < interval_end)]
                interval_data = player_data.loc[interval_index]

                # Sum features for the interval
                interval_features = {
                    "interval_start": current_time,
                    "interval_duration": (interval_end - current_time).total_seconds(),
                    "zone_5_distance_{}s".format(player_role): 0,
                    "zone_5_time_{}s".format(player_role): 0,
                    "zone_6_distance_{}s".format(player_role): 0,
                    "zone_6_time_{}s".format(player_role): 0,
                }

                for _, row in interval_data.iterrows():
                    speed = row["Speed (m/s)"]
                    if ZONE_5_SPRINT_THRESHOLD <= speed < ZONE_6_SPRINT_THRESHOLD:
                        interval_features["zone_5_distance_{}s".format(player_role)] += speed * row["TimeDiff"]
                        interval_features["zone_5_time_{}s".format(player_role)] += row["TimeDiff"]
                    elif speed >= ZONE_6_SPRINT_THRESHOLD:
                        interval_features["zone_6_distance_{}s".format(player_role)] += speed * row["TimeDiff"]
                        interval_features["zone_6_time_{}s".format(player_role)] += row["TimeDiff"]

                role_features_dict[player_role].append(interval_features)
                current_time = interval_end

    # Save the results to a Parquet file
    # Create a DataFrame for each role and concatenate them
    features_df = pd.concat(
        [pd.DataFrame(features) for features in role_features_dict.values()],
        ignore_index=True
    ).set_index("interval_start")

    # Sum features by interval_start
    features_df = features_df.groupby("interval_start").agg(
        lambda x: x.iloc[0] if x.name == "interval_duration" else x.sum(numeric_only=True)
    )

    features_df['total_zone_5_distance'] = features_df['zone_5_distance_defenders'] + features_df['zone_5_distance_midfielders'] + features_df['zone_5_distance_attackers']
    features_df['total_zone_5_time'] = features_df['zone_5_time_defenders'] + features_df['zone_5_time_midfielders'] + features_df['zone_5_time_attackers']
    features_df['total_zone_6_distance'] = features_df['zone_6_distance_defenders'] + features_df['zone_6_distance_midfielders'] + features_df['zone_6_distance_attackers']
    features_df['total_zone_6_time'] = features_df['zone_6_time_defenders'] + features_df['zone_6_time_midfielders'] + features_df['zone_6_time_attackers']

    # Label each row with OPTA data
    season = get_season(game_folder_name)
    opta_file_path = os.path.join(opta_folder_path,season, game_folder_name+".csv")
    opta_df = pd.read_csv(opta_file_path)
    opta_df['TimeStamp'] = pd.to_datetime(opta_df['TimeStamp'], format='%Y-%m-%d %H:%M:%S')
    for idx, row in features_df.iterrows():
        matching_opta = opta_df[(opta_df['TimeStamp'] >= idx) & (opta_df['TimeStamp'] < idx + timedelta(minutes=summation_interval))]
        if not matching_opta.empty:
            features_df.at[idx, 'TotalxG'] = round(matching_opta['xG'].sum(), 3)
        else:
            features_df.at[idx, 'TotalxG'] = 0.000

    # Save the results to a csv file
    output_path = os.path.join(game_folder_path, "features_{}.csv".format(game_folder_name))
    features_df.to_csv(output_path, index=True)
    return features_df

def count_accelerations_decelerations(df):
    accelerations, decelerations = 0, 0
    aggregated_df = df.groupby('Time').agg(lambda x: x.mean() if x.dtype.kind in 'biufc' else x.iloc[0])

    # Calculate acceleration for aggregated values
    aggregated_df['acceleration'] = aggregated_df.apply(
        lambda row: math.sqrt(float(row['Accl X'])**2 + float(row['Accl Y'])**2 + float(row['Accl Z'])**2), 
        axis=1
    )
    speeds = aggregated_df["Speed (m/s)"].values

    for i, row in enumerate(aggregated_df.itertuples()):
        if row.acceleration >= acceleration_threshold:
            current_speed = row._4 if "Speed (m/s)" not in aggregated_df.columns else row._asdict().get("Speed (m/s)", None)
            # If column names are not preserved, _4 is likely "Speed (m/s)"
            if current_speed is None:
                current_speed = row._4

            next_speeds = speeds[i+1:i+6]
            if len(next_speeds) == 0:
                continue

            higher = sum(s > current_speed for s in next_speeds)
            lower = sum(s < current_speed for s in next_speeds)

            if higher > lower:
                accelerations += 1
            elif lower > higher:
                decelerations += 1
    return accelerations, decelerations

def get_game_accel_decel_csv(metadata_file_path:str, game_folder_path: str,summation_interval: int = 5):
    game_folder_name = game_folder_path.split('\\')[-1]
    year = int(game_folder_name.split('-')[0])
    month = int(game_folder_name.split('-')[1])
    day = int(game_folder_name.split('-')[2])
    first_half_start, first_half_end, second_half_start, second_half_end = get_half_times(
        metadata_file_path=metadata_file_path, game_folder_name=game_folder_name
    )
    csv_files = glob.glob(game_folder_path + r"\*.csv")
    role_features_dict = {role: [] for role in POSITIONS_MAPPING.values()}
    features_file = None
    for file in csv_files:
        if not file.endswith("Entire-Session.csv"):
            features_file = file    
            continue
        print(f"Processing file: {file}")
        player_data = pd.read_csv(file,parse_dates=['Time'])
        player_data['Time'] = player_data['Time'].dt.floor('ms')
        position = file.split('\\')[-1].split('-')[3].split('_')[0]
        player_role = POSITIONS_MAPPING[position]
        # Process each half
        for half_start, half_end in [(first_half_start, first_half_end), (second_half_start, second_half_end)]:
            half_start = pd.to_datetime(half_start).replace(year=year,month=month,day=day)
            half_end = pd.to_datetime(half_end).replace(year=year,month=month,day=day)
            current_time = half_start

            while current_time < half_end:
                interval_end = current_time + timedelta(minutes=summation_interval)
                interval_end = min(interval_end, half_end)
                interval_index = player_data.index[(player_data["Time"] >= current_time) &
                                                   (player_data["Time"] < interval_end)]
                interval_data = player_data.loc[interval_index]
                accelerations, decelerations = count_accelerations_decelerations(interval_data)
                interval_features = {
                    "interval_start": current_time,
                    "accelerations_{}s".format(player_role): accelerations,
                    "decelerations_{}s".format(player_role): decelerations
                    }
                role_features_dict[player_role].append(interval_features)
                current_time = interval_end

    
    features_df = pd.concat(
        [pd.DataFrame(features) for features in role_features_dict.values()],
        ignore_index=True
    ).set_index("interval_start")

    # Sum features by interval_start
    features_df = features_df.groupby("interval_start").agg(
        lambda x: x.iloc[0] if x.name == "interval_duration" else x.sum(numeric_only=True)
    )
    features_df = add_features_to_existing_csv(features_file, features_df)    
    output_path = os.path.join(game_folder_path, "features_{}.csv".format(game_folder_name))
    features_df.to_csv(output_path, index=True)


# done = []
# for dir in os.listdir(r"path\to\season"):
#     try:
#         if dir in done:
#             print(f"Skipping {dir}, already done.")
#             continue
#         get_game_accel_decel_csv(
#             metadata_file_path=r"path\to\games_metadata.csv",
#             game_folder_path=os.path.join(r"path\to\season", dir),
#             summation_interval=5
#         )
#         done.append(dir)
#     except Exception as e:
#         print(f"Error processing {dir}: {e}")   
#         continue
#     print(done)




