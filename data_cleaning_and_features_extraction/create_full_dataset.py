from feature_extraction_from_clean_games_csv import *
import os
import glob


base_dir_path = r"data\GPS" # Change this to your base GPS directory path
all_feature_csvs = []
metadata_file_path = r"metadata.csv" # Path to your metadata CSV file


# Recursively search for CSV files starting with 'features'
def get_all_feature_csvs(base_dir_path):
    for root, dirs, files in os.walk(base_dir_path):
        for file in files:
            if file.startswith("features") and file.endswith(".csv"):
                all_feature_csvs.append(os.path.join(root, file))

# Concatenate all CSVs along the row axis
def concatenate_csv_files(csv_file_paths):
    if csv_file_paths:
        concatenated_df = pd.concat([pd.read_csv(csv) for csv in csv_file_paths], ignore_index=True)
        print("Concatenated DataFrame:")
        print(concatenated_df.head())
        print(concatenated_df.describe())
        # Save the concatenated DataFrame to a new CSV file
        concatenated_df.to_csv(os.path.join(base_dir_path, "full_features_dataset.csv"), index=False)
    else:
        print("No CSV files starting with 'features' were found.")

def create_half_time_dataset():
    get_all_feature_csvs(base_dir_path)
    halves_df = None
    full_games_df = None
    for file in all_feature_csvs:
        file_name = os.path.basename(file)
        year = int(file_name.split('_')[1].split('-')[0])
        month = int(file_name.split('_')[1].split('-')[1])
        day = int(file_name.split('_')[1].split('-')[2])
        game_date = f"{year}-{month:02d}-{day:02d}"
        start_time, first_half_end, second_half_start_time, _ = get_half_times(
        metadata_file_path=metadata_file_path, game_folder_name=file_name.split('_')[1].split('.')[0])
        first_half_end = pd.to_datetime(first_half_end).replace(year=year, month=month, day=day)
        df = pd.read_csv(file)
        df['interval_start'] = pd.to_datetime(df['interval_start'])
        first_half_df = df[df['interval_start'] < first_half_end]
        second_half_df = df[df['interval_start'] >= first_half_end]
        
        first_half_sum = pd.DataFrame([{
            'interval_start': game_date + " " + str(start_time),  
            'half': 1,
            **first_half_df.iloc[:, 1:].sum() 
        }])
        second_half_sum = pd.DataFrame([{
            'interval_start': game_date + " " + str(second_half_start_time),  
            'half': 2,
            **second_half_df.iloc[:, 1:].sum() 
        }])

        both_halves_df = pd.concat([first_half_sum, second_half_sum], ignore_index=True)
        full_game_df = pd.DataFrame([{
            'game_date': game_date + " " + str(start_time),
            **both_halves_df.iloc[:, 1:].sum() 
        }])
        full_game_df.drop(columns=['half'], inplace=True)

        if halves_df is None:
            halves_df = both_halves_df
        else:
            halves_df = pd.concat([halves_df, both_halves_df], ignore_index=True)

        if full_games_df is None:
            full_games_df = full_game_df
        else:
            full_games_df = pd.concat([full_games_df, full_game_df], ignore_index=True)

    numeric_cols = halves_df.select_dtypes(include=['float64', 'float32']).columns
    for col in numeric_cols:
        if col == 'TotalxG':
            halves_df[col] = halves_df[col].round(3)
        else:
            halves_df[col] = halves_df[col].round(4)
            
    numeric_cols = full_games_df.select_dtypes(include=['float64', 'float32']).columns
    for col in numeric_cols:
        if col == 'TotalxG':
            full_games_df[col] = full_games_df[col].round(3)
        else:
            full_games_df[col] = full_games_df[col].round(4)

    halves_df.to_csv("halves_features_dataset.csv", index=False)
    full_games_df.to_csv("full_games_features_dataset.csv", index=False)
