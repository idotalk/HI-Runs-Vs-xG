import pandas as pd
import glob
import os
from datetime import datetime


def delete_unrealated_games(dir):
    games_csv = glob.glob(dir + "\\*.csv")
    for file in games_csv:
        if "RawDataExtended" in file:
            continue
        if "maccabi-haifa" not in file.lower():
            os.remove(file)


def delete_other_team_chances(dir):
    games_csv = glob.glob(dir + "\\*.csv")
    for file in games_csv:
        df = pd.read_csv(file)
        if "Team" in df.columns:
            df = df[df["Team"] == "Maccabi Haifa"]
            df.to_csv(file, index=False)


def delete_static_chances(dir, delete_set_pieces):
    games_csv = glob.glob(dir + "\\*.csv")
    for file in games_csv:
        df = pd.read_csv(file)
        if "ShotPlayStyle" in df.columns:
            if not delete_set_pieces:
                df = df[df["ShotPlayStyle"] != "Penalty"]
            else:
                df = df[df["ShotPlayStyle"] == "Open Play"]
            df.to_csv(file, index=False)


def rename_csv_files(dir):
    games_csv = glob.glob(dir + "\\*.csv")
    for file in games_csv:
        if "RawDataExtended" in file:
            continue
        basename = os.path.basename(file)
        date_part = basename.split("_")[0]
        date_obj = datetime.strptime(date_part, "%Y-%m-%d")
        new_name = f"{date_obj.strftime('%Y-%m-%d')}-{date_obj.strftime('%B')} {date_obj.day}, {date_obj.year}-RawDataExtended.csv"
        new_path = os.path.join(dir, new_name)
        os.rename(file, new_path)


def clean_OPTA_data(paths, delete_set_pieces=False):
    for path in paths:
        delete_unrealated_games(path)
        delete_other_team_chances(path)
        delete_static_chances(path, delete_set_pieces)
        rename_csv_files(path)


# Example usage:
# paths = [r"C:\path\to\game\files1", r"C:\path\to\game\files2"...]
# clean_OPTA_data(paths, delete_set_pieces=True)
