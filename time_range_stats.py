import pandas as pd
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

def time_range_stats(path,frequency):
    """
    Calculate KM-covered, average speed and average acceleration statistics for each player over time frequency.

    :param path: Path to the CSV file containing player tracking data after concat_frames.
    :param frequency: Frequency of the time intervals for statistics, use Datatime frequencies format (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases)
    
    :return: DataFrame with statistics for each player at each time interval.
    """
    df = pd.read_csv(path)
    df['Time'] = pd.to_datetime(df['Time'])
    players = df['Player'].unique()

    stats = []
    for time_chunk , group in df.groupby(pd.Grouper(key='Time', freq=frequency)):
        chunk_stats = []
        for player in players:
            player_data = group[group['Player'] == player]
            if len(player_data) < 2:
                continue
            
            # Calculate distance covered
            total_distance = 0
            for i in range(1, len(player_data)):
                lon1, lat1 = player_data.iloc[i-1]['Lon'], player_data.iloc[i-1]['Lat']
                lon2, lat2 = player_data.iloc[i]['Lon'], player_data.iloc[i]['Lat']
                total_distance += haversine(lon1, lat1, lon2, lat2)
            average_speed = total_distance / (len(player_data) - 1) * 3600 # KM/h
            #average_acceleration = average_speed / (len(player_data) - 1)
            chunk_stats.append({
                'Player': player,
                'DistanceKM': total_distance,
                'AverageSpeedKMh': average_speed
                #'AverageAcceleration': average_acceleration
            })
        print("--------------------------------------------------")
        print(f"Time Chunk: {time_chunk}")
        print(pd.DataFrame(chunk_stats).sort_values(by='DistanceKM', ascending=False)) # does distance covered is the best metric?
        print("--------------------------------------------------\n")    
        stats.append(chunk_stats)
    return stats

def find_lineup(path):
    """
    Calculate KM-covered, average speed and average acceleration statistics for each player over time frequency.

    :param path: Path to the CSV file containing player tracking data after concat_frames.
    :param frequency: Frequency of the time intervals for statistics, use Datatime frequencies format (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases)
    
    :return: DataFrame with statistics for each player at each time interval.
    """
    df = pd.read_csv(path)
    df['Time'] = pd.to_datetime(df['Time'])
    players = df['Player'].unique()

    first_chunk = True
    lineup = []
    for time_chunk , group in df.groupby(pd.Grouper(key='Time', freq='45min')):
        chunk_stats = []
        for player in players:
            player_data = group[group['Player'] == player]
            if len(player_data) < 2:
                continue
            
            # Calculate distance covered
            total_distance = 0
            for i in range(1, len(player_data)):
                lon1, lat1 = player_data.iloc[i-1]['Lon'], player_data.iloc[i-1]['Lat']
                lon2, lat2 = player_data.iloc[i]['Lon'], player_data.iloc[i]['Lat']
                total_distance += haversine(lon1, lat1, lon2, lat2)
            average_speed = total_distance / (len(player_data) - 1) * 3600 # KM/h
            chunk_stats.append({
                'Player': player,
                'DistanceKM': total_distance,
                'AverageSpeedKMh': average_speed
            })
        df_chunk = pd.DataFrame(chunk_stats).sort_values(by='DistanceKM', ascending=False)
        if first_chunk:
            lineup = sorted(df_chunk.head(10)['Player'].tolist())
            return lineup

def find_subs(path, lineup):
    """
    Find substitutions based on top 10 runners (distance covered).
    If a new player enters the top 10 and stays there for 3 consecutive minutes,
    replace the player who left the top 10 in the lineup.
    """
    df = pd.read_csv(path)
    df['Time'] = pd.to_datetime(df['Time'])
    players_names = df['Player'].unique()
    played = set(lineup)
    current_lineup = set(lineup)
    minute_groups = list(df.groupby(pd.Grouper(key='Time', freq='1min')))

    subs = []
    stats = []
    for i, (time_chunk, group) in enumerate(minute_groups):
        chunk_stats = []
        for player in players_names:
            player_data = group[group['Player'] == player]
            if len(player_data) < 2:
                continue
            total_distance = 0
            for j in range(1, len(player_data)):
                lon1, lat1 = player_data.iloc[j-1]['Lon'], player_data.iloc[j-1]['Lat']
                lon2, lat2 = player_data.iloc[j]['Lon'], player_data.iloc[j]['Lat']
                total_distance += haversine(lon1, lat1, lon2, lat2)
            chunk_stats.append({
                'Player': player,
                'DistanceKM': total_distance,
                'Time': time_chunk
            })
        df_chunk = pd.DataFrame(chunk_stats).sort_values(by='DistanceKM', ascending=False)
        stats.append(df_chunk)
    
    for i,chunk_data in enumerate(stats):
        top_players = set(chunk_data.head(10)['Player'].tolist())
        if current_lineup != top_players:
            for player in top_players:
                if player not in current_lineup and player not in played:                    
                    # Check if the player has been in the top 10 for 3 consecutive minutes
                    if i<len(stats)-3 and all(player in stats[j].head(10)['Player'].tolist() for j in range(i, min(i+3,len(stats)))):
                        # Find a player to replace
                        for old_player in current_lineup:
                            if old_player not in top_players:
                                subs.append((old_player, player, chunk_data['Time'].iloc[0]))                                
                                current_lineup.remove(old_player)
                                current_lineup.add(player)
                                played.add(old_player)
                                break
    print("Substitutions:")
    for old_player, new_player, time in subs:
        print(f"{old_player} replaced by {new_player} at {time}")


# ln = ["DM_16","AM_21","CB_3","CB_5","CF_34","CF_37","DM_15","RW_25","RB_8","LB_12"]
# find_subs("31.8.24.csv",ln)
time_range_stats("31.8.24.csv", "1min")