import numpy as np
import pandas as pd
import glob
import os
import feature_extraction_from_clean_games_csv as fe
def expected_points(team, home_team, p_home_win, p_draw, p_away_win):
    """Calculate expected points for given team given win/draw/loss probabilities."""
    if team == home_team:
        return 3 * p_home_win + 1 * p_draw
    else:
        return 3 * p_away_win + 1 * p_draw


def simulate_expected_points(game_opta_csv_path: str, team_of_interest: str, n_sim: int = 10_000):
    """Simulate expected points (binomial & Poisson) for one team in one match."""
    df = pd.read_csv(game_opta_csv_path)
    df['xG'] = df['xG'].fillna(0)

    # Aggregate goal probability per possession
    poss_goal_probs = (
        df.groupby(['PossNum', 'Team'])['xG']
        .apply(lambda x: 1 - np.prod(1 - x))
        .reset_index(name='p_goal')
    )

    home_team = df['homeTeam'].iloc[0]
    away_team = df['awayTeam'].iloc[0]

    p_home = poss_goal_probs.loc[poss_goal_probs['Team'] == home_team, 'p_goal'].values
    p_away = poss_goal_probs.loc[poss_goal_probs['Team'] == away_team, 'p_goal'].values

    rng = np.random.default_rng(42)

    #  Binomial (per possession) 
    home_goals_b = rng.binomial(1, p_home, size=(n_sim, len(p_home))).sum(axis=1)
    away_goals_b = rng.binomial(1, p_away, size=(n_sim, len(p_away))).sum(axis=1)
    home_win_b = (home_goals_b > away_goals_b).mean()
    away_win_b = (away_goals_b > home_goals_b).mean()
    draw_b = (home_goals_b == away_goals_b).mean()

    #  Poisson (total xG) 
    home_goals_p = rng.poisson(p_home.sum(), size=n_sim)
    away_goals_p = rng.poisson(p_away.sum(), size=n_sim)
    home_win_p = (home_goals_p > away_goals_p).mean()
    away_win_p = (away_goals_p > home_goals_p).mean()
    draw_p = (home_goals_p == away_goals_p).mean()

    # Compute expected points
    exp_b = expected_points(team_of_interest, home_team, home_win_b, draw_b, away_win_b)
    exp_p = expected_points(team_of_interest, home_team, home_win_p, draw_p, away_win_p)

    return exp_b, exp_p



def season_simulation_all_teams(season_path_csv: str, actual_points_dict, actual_positions_dict):
    """Compute expected points for all teams across the season, output separate tables for Binomial and Poisson."""
    games_csv = glob.glob(os.path.join(season_path_csv, "*.csv"))

    results = []

    for file in games_csv:
        df = pd.read_csv(file)
        home_team = df['homeTeam'].iloc[0]
        away_team = df['awayTeam'].iloc[0]

        b_home, p_home = simulate_expected_points(file, home_team)
        b_away, p_away = simulate_expected_points(file, away_team)

        results.append({'Team': home_team, 'Model': 'Binomial', 'xPts': b_home})
        results.append({'Team': away_team, 'Model': 'Binomial', 'xPts': b_away})
        results.append({'Team': home_team, 'Model': 'Poisson', 'xPts': p_home})
        results.append({'Team': away_team, 'Model': 'Poisson', 'xPts': p_away})

    df_res = pd.DataFrame(results)

    # Aggregate per team per model
    table = (
        df_res.groupby(['Team', 'Model'], as_index=False)
        .agg(Games=('xPts', 'count'), Total_xPts=('xPts', 'sum'))
    )
    table['xPts_per_Game'] = table['Total_xPts'] / table['Games']

    # Split tables
    binomial_table = table[table['Model'] == 'Binomial'].copy().reset_index(drop=True)
    poisson_table = table[table['Model'] == 'Poisson'].copy().reset_index(drop=True)

    # Add actual points and position columns
    if actual_points_dict is not None:
        binomial_table['Actual_Pts'] = binomial_table['Team'].map(actual_points_dict)
        poisson_table['Actual_Pts'] = poisson_table['Team'].map(actual_points_dict)
        binomial_table['Pts_Diff'] = binomial_table['Actual_Pts'] - binomial_table['Total_xPts']
        poisson_table['Pts_Diff'] = poisson_table['Actual_Pts'] - poisson_table['Total_xPts']
    if actual_positions_dict is not None:
        binomial_table['Actual_Pos'] = binomial_table['Team'].map(actual_positions_dict)
        poisson_table['Actual_Pos'] = poisson_table['Team'].map(actual_positions_dict)
        # Predicted position: rank by Total_xPts (lower is better)
        binomial_table['Pred_Pos'] = binomial_table['Total_xPts'].rank(ascending=False, method='min').astype(int)
        poisson_table['Pred_Pos'] = poisson_table['Total_xPts'].rank(ascending=False, method='min').astype(int)
        binomial_table['Pos_Diff'] = binomial_table['Actual_Pos'] - binomial_table['Pred_Pos']
        poisson_table['Pos_Diff'] = poisson_table['Actual_Pos'] - poisson_table['Pred_Pos']

    binomial_table = binomial_table.sort_values(by='Actual_Pos', ascending=True).reset_index(drop=True)
    poisson_table = poisson_table.sort_values(by='Actual_Pos', ascending=True).reset_index(drop=True)

    print("\n Binomial Expected Points Table \n")
    print(binomial_table.to_string(index=False))
    print("\n Poisson Expected Points Table \n")
    print(poisson_table.to_string(index=False))

    return binomial_table, poisson_table

def xPts_feature_creation(opta_folder_path: str, full_games_df: pd.DataFrame):
    full_games_df['xPts'] = 0.000
    for idx, row in full_games_df.iterrows():
        game_date = row['game_date'].split(' ')[0]
        season = fe.get_season(game_date.split(' ')[0])
        opta_files = glob.glob(os.path.join(opta_folder_path, season, f"{game_date}-*.csv"))
        if not opta_files:
            print(f"No OPTA file found for date {game_date}")
            continue
        opta_file = opta_files[0]
        full_games_df.at[idx, 'xPts'] = simulate_expected_points(opta_file, 'Maccabi Haifa')[0].round(3)
    full_games_df.to_csv("full_games_features_dataset4.csv", index=False)


# # Fill these dicts with your actual data
# actual_points23 = {
#     'Maccabi Tel Aviv': 85,
#     'Maccabi Haifa': 74,
#     'Hapoel Be\'er Sheva': 61,
#     'Hapoel Haifa': 59,
#     'Maccabi Bney Reine': 44,
#     'Bnei Sakhnin': 44,
#     'Hapoel Jerusalem': 43,
#     'Maccabi Petach Tikva':40,
#     'Maccabi Netanya': 38,
#     'Beitar Jerusalem': 36, 
#     'Hapoel Petach Tikva' : 24, 
#     'Hapoel Hadera' : 36,
#     'Ashdod SC' : 37,
#     'Hapoel Tel Aviv' : 33
# }
# actual_positions23 = {
#     'Maccabi Tel Aviv': 1,
#     'Maccabi Haifa': 2,
#     'Hapoel Be\'er Sheva': 3,
#     'Hapoel Haifa': 4,
#     'Maccabi Bney Reine': 5,
#     'Bnei Sakhnin': 6,
#     'Hapoel Jerusalem': 7,
#     'Maccabi Petach Tikva':8,
#     'Maccabi Netanya': 9,
#     'Ashdod SC' : 10,
#     'Beitar Jerusalem': 11,
#     'Hapoel Hadera' : 12,
#     'Hapoel Tel Aviv' : 13,
#     'Hapoel Petach Tikva' : 14
# }

# season_simulation_all_teams(r"data\opta_2324\ipl2324", actual_points23, actual_positions23)

# actual_points24 = {
#     'Maccabi Tel Aviv': 80,
#     'Maccabi Haifa': 61,
#     'Hapoel Be\'er Sheva': 78,
#     'Hapoel Haifa': 52,
#     'Maccabi Bney Reine': 41,
#     'Bnei Sakhnin': 36,
#     'Hapoel Jerusalem': 44,
#     'Maccabi Petach Tikva':33,
#     'Maccabi Netanya': 45,
#     'Beitar Jerusalem': 53, 
#     'Hapoel Ironi Kiryat Shmona' : 37, 
#     'Hapoel Hadera' : 27,
#     'Ashdod SC' : 35,
#     'Ironi Tiberias' : 35
# }
# actual_positions24 = {
#     'Maccabi Tel Aviv': 1,
#     'Hapoel Be\'er Sheva': 2,
#     'Maccabi Haifa': 3,
#     'Beitar Jerusalem': 4,
#     'Hapoel Haifa': 5,
#     'Maccabi Netanya': 6,
#     'Hapoel Jerusalem': 7,
#     'Maccabi Bney Reine': 8,
#     'Hapoel Ironi Kiryat Shmona' : 9,
#     'Bnei Sakhnin': 10,
#     'Ashdod SC' : 11,
#     'Ironi Tiberias' : 12,
#     'Maccabi Petach Tikva':13,
#     'Hapoel Hadera' : 14
# }

# season_simulation_all_teams(r"data\opta_2324\ipl2425", actual_points24, actual_positions24)