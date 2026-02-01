import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np
import re


def parse_coords(coord_str):
    """Parse coordinates from string format "(x,y)" to tuple (x, y)"""
    match = re.search(r'\(([^)]+)\)', coord_str)
    if match:
        x, y = map(float, match.group(1).split(','))
        return x, y
    return None, None

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['x'], df['y'] = zip(*df['xyCoords'].apply(parse_coords))
    return df

def draw_pitch(ax):
    """ Pitch dimensions: 68m x 105m, centered at (0,0) """
    # Draw the outline of the pitch
    pitch = Rectangle((-34, -52.5), 68, 105, fill=False, color='green', linewidth=2)
    ax.add_patch(pitch)
    
    # Draw the center line
    plt.plot([-34, 34], [0, 0], 'green', linewidth=2)
    
    # Draw the center circle
    center_circle = plt.Circle((0, 0), 9.15, fill=False, color='green', linewidth=2)
    ax.add_patch(center_circle)
    
    # Draw the penalty areas
    penalty_top = Rectangle((-20.16, -52.5), 40.32, 16.5, fill=False, color='green', linewidth=2)
    ax.add_patch(penalty_top)
    penalty_bottom = Rectangle((-20.16, 52.5 - 16.5), 40.32, 16.5, fill=False, color='green', linewidth=2)
    ax.add_patch(penalty_bottom)
    
    # Draw the goals areas
    goal_top = Rectangle((-9.16, -52.5), 18.32, 5.5, fill=False, color='green', linewidth=2)
    ax.add_patch(goal_top)
    goal_bottom = Rectangle((-9.16, 52.5 - 5.5), 18.32, 5.5, fill=False, color='green', linewidth=2)
    ax.add_patch(goal_bottom)
    
    # Draw the goals
    plt.plot([-7.32/2, 7.32/2], [-52.5, -52.5], 'black', linewidth=5)  # Top goal
    plt.plot([-7.32/2, 7.32/2], [52.5, 52.5], 'black', linewidth=5)  # Bottom goal
    
    # Set the limits of the plot
    ax.set_xlim(-39, 39)
    ax.set_ylim(-57.5, 57.5)    
    return ax    # Pitch dimensions: 68m x 105m

def draw_pitch_around_corner(ax):
    """ Pitch dimensions: 68m x 105m, upper left corner at (0,0) """
    # Draw the outline of the pitch
    pitch = Rectangle((0, 0), 68, 105, fill=False, color='green', linewidth=2)
    ax.add_patch(pitch)
    
    # Draw the center line
    plt.plot([0, 68], [105/2, 105/2], 'green', linewidth=2)
    
    # Draw the center circle
    center_circle = plt.Circle((68/2, 105/2), 9.15, fill=False, color='green', linewidth=2)
    ax.add_patch(center_circle)
    
    # Draw the penalty areas
    penalty_top = Rectangle((68/2 - 20.16, 0), 40.32, 16.5, fill=False, color='green', linewidth=2)
    ax.add_patch(penalty_top)
    penalty_bottom = Rectangle((68/2 - 20.16, 105 - 16.5), 40.32, 16.5, fill=False, color='green', linewidth=2)
    ax.add_patch(penalty_bottom)
    
    # Draw the goals areas
    goal_top = Rectangle((68/2 - 9.16, 0), 18.32, 5.5, fill=False, color='green', linewidth=2)
    ax.add_patch(goal_top)
    goal_bottom = Rectangle((68/2 - 9.16, 105 - 5.5), 18.32, 5.5, fill=False, color='green', linewidth=2)
    ax.add_patch(goal_bottom)
    
    # Draw the goals
    plt.plot([68/2 - 7.32/2, 68/2 + 7.32/2], [0, 0], 'black', linewidth=5)  # Top goal
    plt.plot([68/2 - 7.32/2, 68/2 + 7.32/2], [105, 105], 'black', linewidth=5)  # Bottom goal
    
    # Set the limits of the plot
    ax.set_xlim(-5, 73)
    ax.set_ylim(-5, 110)    
    return ax

def assign_colors(names):
    """Assign colors to players based on their position, defenders in blue, midfielders in green, and forwards in red. If position is unknown, default to black."""
    position_colors = {
        'CB': 'blue',
        'RB':'blue',
        'LB': 'blue',
        'LWB': 'blue',
        'RWB': 'blue',
        'SW' : 'blue',
        'DM': 'green',
        'CM': 'green',
        'AM': 'green',
        'RM': 'green',
        'LM': 'green',
        'SS': 'red',
        'RW': 'red',
        'LW': 'red',
        'ST': 'red',
        'CF': 'red',
    }
    player_colors = {}
    for name in names:
        position = name.split('_')[0]
        color = position_colors.get(position, 'black')  # default to black if unknown
        player_colors[name] = color
    return player_colors

def animate_players(file_path, interval=200):
    """
    Animate player movements on a football pitch based on tracking data from a CSV file.
    
    :param file_path: Path to the CSV file containing player tracking data.
        
    :param interval: Time interval between frames in milliseconds.
    
    return
    ----------
    Animation object."""
    df = load_data(file_path)
    # Get unique players and time points
    players = df['Player'].unique()
    time_points = sorted(df['RoundedTime'].unique())
    
    # Set up color mapping for players
    player_colors = assign_colors(players)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 15))
    draw_pitch(ax)
    plt.title('Football Player Movements')
    
    
    scatter_plots = {}
    player_labels = {}
    # Initialize scatter plots for each player
    for player in players:
        player_data = df[df['Player'] == player]
        first_pos = player_data.iloc[0]
        scatter = ax.scatter(first_pos['x'], first_pos['y'], color=player_colors[player], s=100, label=player)
        scatter_plots[player] = scatter
        label = ax.text(first_pos['x'] + 0.5, first_pos['y'] + 0.5, player, color=player_colors[player], fontsize=10, weight='bold')
        player_labels[player] = label
    
    # Time display
    time_text = ax.text(0.02, 0.95, f'Time: {time_points[0]}s', transform=ax.transAxes)

    
    def update(frame):
        current_time = time_points[frame]
        time_text.set_text(f'Time: {current_time}s')
        
        # Update position for each player
        for player in players:
            player_at_time = df[(df['Player'] == player) & (df['RoundedTime'] == current_time)]
            if not player_at_time.empty:
                x = player_at_time['x'].values[0]
                y = player_at_time['y'].values[0]
                scatter_plots[player].set_offsets([(x, y)])
                player_labels[player].set_position((x + 0.5, y + 0.5))
        return list(scatter_plots.values()) + list(player_labels.values()) + [time_text]
    
    ani = animation.FuncAnimation(fig, update, frames=len(time_points), interval=interval, blit=True)
    plt.tight_layout()
    plt.show()
    
    return ani
