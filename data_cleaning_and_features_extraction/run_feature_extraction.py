from feature_extraction_from_clean_games_csv import *
import os
import glob

game_folder_path = r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\clean_data\GPS\ipl2425\2025-03-16-March 16, 2025-RawDataExtended"
game_features_df = get_game_features_csv(
    metadata_file_path=r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\games_metadata.csv",
    game_folder_path=game_folder_path,
opta_folder_path = r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\clean_data\OPTA"
)


base_dir_path = r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\clean_data\GPS\ipl2425\feature extraction done"
for game_folder_name in os.listdir(base_dir_path):
    game_folder_path = os.path.join(base_dir_path, game_folder_name)
    if os.path.isdir(game_folder_path):  # Ensure it's a directory
        try:
            game_features_df = get_game_features_csv(
                metadata_file_path=r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\games_metadata.csv"
                , game_folder_path=game_folder_path
            , opta_folder_path=r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\clean_data\OPTA"
            )
        except Exception as e:
            print(f"Error processing {game_folder_name}: {e}")
            continue
        print(f"Created CSV for game: {game_folder_name}")
        print(game_features_df.head())
        print(game_features_df.describe())
