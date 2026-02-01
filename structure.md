This file contain all the software modules we used throughout our project, with a short description of what it does:

  /
  └── data_cleaning_and_features_extraction/
    └── clean_OPTA_data.py - Cleaning the OPTA data files, deletes any unrelated games, renaming the files names to match the GPS data file names,
                             deletes penalties and the other team chances.
    └── create_full_dataset.py - Create full games and halves datasets from higher frequency datasets (for modularity we started with 5 minutes frequency, which let you      
                                 choose the time ranges to analyze).
    └── data_clean.py - Cleaning all the unrelated GPS entries from all the data files you have.
    └── expected_points_simulator.py - The monte carlo simulator to calculate the xPts value.
    └── feature_extraction_from_clean_games_csv.py - Extracting the fetures for each game and labeling it with xG, there is also a function to add more features to the dataset in the future. 
    └── parse_sofa_hunt.py - Parsing the sofa hunt data files to easily clean substitutions.
    └── run_feature_extraction.py - The final pipeline to create the datasets from the data. 
  └── jupiter_notebook/
    └── halves_2_seasons_models.ipynb - Training models on the halves datasets (failed attempt, results were not good)
    └── models_analysis_full_dataset_with_shap_for_trees.ipynb - The finals models we trained on xG target value
    └── models_analysis_xPts.ipynb - Models we trained using the xPts target value (failed attempt, results were not good)
    └── relevance_analysis_9_10_2025_meeting.ipynb - Relevance analysis of the fetures based on xG
    └── relevance_analysis_xPts.ipynb - Relevance analysis of the fetures based on xPts
    └── Upper_Lower_playoff_teams_analysis_xPts.ipynb - Relevance Analysis we made splitting the games to upper/lower playoff teams
    └── datasets_features_target_histogram.ipynb  - The fetures histograms and distribution across the full games datasets 
    └── datasets_feature_target_histogram_upper_lower.ipynb - The fetures histograms and distribution splitted to upper/lower playoffs
  └── concat_frames.py - Aggregates multiple raw tracking CSV files (one per player) into a single unified dataset, handling time synchronization, filtering, and coordinate projection via stadium_projection.py
  └── constants.py - Static configuration data, including a dictionary mapping specific player positions to general roles (e.g., 'RB' to 'defender') and speed thresholds for sprint zones.
  └── data_analysis.py - Provides general utility functions for loading datasets and generating statistical visualizations, specifically Pearson correlation matrices/heatmaps.
  └── projection_animation.py - Visualizes the processed tracking data by drawing a scaled football pitch and generating an animation of player movements over time.
  └── libs.txt - All the packages needed for this project.
  └── run_vis.py - Serves as the main execution script that orchestrates the data pipeline, processing specific raw match data and triggering the player movement animation.
  └── stadium_projection.py - Contains GPS reference coordinates for various stadiums and provides mathematical functions to project global latitude/longitude data into local 2D Cartesian coordinates (X, Y) relative to the pitch center.
  └── time_range_stats.py - Calculates physical performance metrics, such as distance covered (using the Haversine formula) and average speed, and includes logic to algorithmically detect starting lineups and substitutions. (We created this file both didn't used it eventually, we decided to keep it here for future use)
