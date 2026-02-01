from concat_frames import *
from projection_animation import animate_players
from stadium_projection import *

#concat_frames(r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\2023-12-24-December 24, 2023-RawDataExtended\2023-12-24-December 24, 2023-RawDataExtended\*.csv",
#                 Netanya_stadium, time_begin="18:30:00", time_end="18:36:00")
#animate_players(file_path='output.csv', interval=200)

concat_frames(r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\2023-12-20-December 20, 2023-RawDataExtended\2023-12-20-December 20, 2023-RawDataExtended\*.csv",
              Sammy_Ofer_stadium_before_Nov, time_begin="19:02:00", time_end="19:07:00")
animate_players(file_path='output.csv', interval=200)

# concat_frames(r"C:\Users\Afek\Documents\Technion studies\semester 6\bina_project_utils\2023-12-10-December 10, 2023-RawDataExtended\2023-12-10-December 10, 2023-RawDataExtended\*.csv",
#               Netanya_stadium, 250000, "17:31:00")
# animate_players(file_path='output.csv', interval=100)

# concat_frames(r"C:\Users\Afek\Documents\Technion studies\semester 6\games_data\games_data_unzipped\away\moshava\2024-11-30-November 30, 2024-RawDataExtended\*.csv",
#               Moshava_stadium, 250000, "13:00:20")
# animate_players(file_path='output.csv', interval=100)

