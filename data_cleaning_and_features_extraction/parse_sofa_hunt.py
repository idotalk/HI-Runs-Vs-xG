import pandas as py
import os
import glob
from datetime import datetime
import json

csv_paths = [
    r"C:\Users\idota\AIproject\data\linups&subs\lineups_2324",
    r"C:\Users\idota\AIproject\data\linups&subs\lineups_2425",
]

players_codes = {
    "Show": "DM_42",
    "M. Kandil": "RB_11",
    "G. Kinda": "AM_20",
    "D. Saba": "AM_21",
    "T. Hemed": "CF_48",
    "E. Azoulay": "DM_16",
    "F. Pierrot": "CF_37",
    "T. Chery": "AM_45",
    "M. Jaber": "CM_18",
    "Ali Mohamed": "DM_15",
    "S. Podgoreanu": "UNK_39",
    "H. Shibli": "LW_31",
    "Pedrão": "CB_6",
    "V. Nsimba": "LB_12",
    "S. Goldberg": "CB_2",
    "L. Refaelov": "AM_22",
    "O. Syrota": "CB_5",
    "E. Shuranov": "CF_38",
    "I. Khalaili": "RW_25",
    "P. Cornud": "LB_13",
    "X. Severina": "RW_24",
    "L. Kasa": "DM_43",
    "Ricardinho": "CF_33",
    "A. Seck": "CB_3",
    "D. Haziza": "LW_29",
    "O. D. Dahan": "CF_35",
    "I. Hajaj": "RM_23",
    "R. Elimelech": "RB_10",
    "R. Gershon": "CB_7",
    "G. Naor": "DM_14",
    "L. Šimić": "CB_41",
    "K. Saief": "LM_28",
    "M. Nahuel": "LW_30",
    "A. Khalaili": "RW_46",
    "L. Hermesh": "DM_17",
    "I. Feingold": "RB_8",
    "D. Sundgren": "RB_9",
    "D. David": "CF_34",
    "G. Melamed": "CF_36",
    "Ziv Ben Shimol": "AM_44",
    "D. Lesovoy": "LW_47",
    "T. Lannes": "CB_4",
}

special_names = ["Ziv Ben Shimol", "Ali Mohamed", "Show", "Pedrão", "Ricardinho"]
goalKeepers = ["S. Kaiuf", "I. Nitzan"]


# Parsing functions
def delete_captain_tag_and_other_team_lineups(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "lineup" in os.path.basename(file):
            df = py.read_csv(file)
            df["Player"] = df["Player"].str.replace("(c) ", "", regex=False)
            df["Player"] = df["Player"].str.lstrip()
            df = df[df["Team"] == "M. Haifa"]
            df.to_csv(file, index=False)


def encode_lineups_players_names(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "lineup" in os.path.basename(file):
            df = py.read_csv(file)
            df["Player"] = df["Player"].apply(
                lambda name: players_codes[name] if name in players_codes else name
            )
            df.to_csv(file, index=False)


def create_json_lineup(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "lineup" in os.path.basename(file):
            df = py.read_csv(file)
            lineup_dict = [
                row["Player"]
                for _, row in df.iterrows()
                if row["Player"] in players_codes.values()
            ]
            if len(lineup_dict) < 10:
                print(f"Warning: Lineup in file {file} has less than 10 players.")
            json_path = file.replace(".csv", ".json")
            with open(json_path, "w") as json_file:
                json.dump(lineup_dict, json_file, indent=4)


def delete_other_team_subs(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "substitutes" in os.path.basename(file):
            df = py.read_csv(file)
            df = df[df["Out Player"].isin(players_codes.keys()) & df["In Player"].isin(players_codes.keys())]
            df.to_csv(file, index=False)


def convert_in_players_names(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "substitutes" in os.path.basename(file):
            df = py.read_csv(file)
            df["In Player"] = df["In Player"].apply(
                lambda name: short_name(name) if name not in special_names else name
            )
            df.to_csv(file, index=False)


def encode_subs_players_names(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "substitutes" in os.path.basename(file):
            df = py.read_csv(file)
            df["In Player"] = df["In Player"].apply(
                lambda name: players_codes[name] if name in players_codes else name
            )
            df["Out Player"] = df["Out Player"].apply(
                lambda name: players_codes[name] if name in players_codes else name
            )
            df.to_csv(file, index=False)


def drop_team_column(csvs_files_path: str):
    csv_files = glob.glob(csvs_files_path)
    for file in csv_files:
        if "substitutes" in os.path.basename(file) or "lineup" in os.path.basename(
            file
        ):
            df = py.read_csv(file)
            if "Team" in df.columns:
                df = df.drop(columns=["Team"])
                df.to_csv(file, index=False)


def rename_csv_files(dir):
    games_csv = glob.glob(dir)
    for file in games_csv:
        if "RawDataExtended" in file:
            continue
        basename = os.path.basename(file)
        date_part = basename.split("_")[0]
        date_obj = datetime.strptime(date_part, "%d-%m-%Y")
        file_type = (
            "lineup"
            if "lineup" in basename
            else "substitutes" if "substitutes" in basename else "other"
        )
        new_name = f"{date_obj.strftime('%Y-%m-%d')}-{date_obj.strftime('%B')} {date_obj.day}, {date_obj.year}-RawDataExtended-{file_type}.{basename.split('.')[-1]}"
        new_path = os.path.join(dir.split("\\*.")[0], new_name)
        os.rename(file, new_path)


def delete_csv_linups_files(dir):
    games_csv = glob.glob(dir + "\\*.csv")
    for file in games_csv:
        if "lineup" in os.path.basename(file):
            os.remove(file)


# Utils functions
def list_players(csv_files_paths: list):
    players = set()
    for csv in csv_files_paths:
        csv_files = glob.glob(csv)
        for file in csv_files:
            if "lineup" in os.path.basename(file):
                df = py.read_csv(file)
                players.update(df["Player"].unique())
    return list(players)


def print_list_as_dict_format(lst):
    print("{")
    for elem in lst:
        print(f'"{elem}":"",')
    print("}")


def find_missing_players(path):
    missing = set()
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            print(filename)
            playerName = filename.split("-")[3]
            if playerName not in players_codes.values():
                missing.add(playerName)
    print_list_as_dict_format(missing)


def short_name(name):
    if name == "O. David Dahan":
        return "O. D. Dahan"
    name_parts = name.split(" ")
    return f"{name_parts[0][0]}. {' '.join(name_parts[1:])}"


# Main parser function - pass a list of paths to the folders containing the sofa hunt csv files
def parse_sofa_hunt_data(csvs_files_paths: str):
    for path in csvs_files_paths:
        delete_captain_tag_and_other_team_lineups(path + "\\*.csv")
        encode_lineups_players_names(path + "\\*.csv")
        create_json_lineup(path + "\\*.csv")
        convert_in_players_names(path + "\\*.csv")
        delete_other_team_subs(path + "\\*.csv")
        encode_subs_players_names(path + "\\*.csv")
        drop_team_column(path + "\\*.csv")
        rename_csv_files(path + "\\*.csv")
        rename_csv_files(path + "\\*.json")
        delete_csv_linups_files(path)


# Example usage:
# paths = [r"C:\path\to\game\files1", r"C:\path\to\game\files2"...]
# parse_sofa_hunt_data(paths)