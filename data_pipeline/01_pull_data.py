import nflreadpy as nfl
import pandas as pd
import os

os.makedirs("data", exist_ok=True)

weekly = nfl.load_player_stats([2020, 2021, 2022, 2023, 2024]).to_pandas()
snaps = nfl.load_snap_counts([2020, 2021, 2022, 2023, 2024]).to_pandas()
# schedules do NOT work as of 5/19 - wait until fix
# schedules = nfl.load_schedules([2021,2022,2023,2024]).to_pandas()

weekly.to_csv('data/raw_weekly.csv', index=False)
snaps.to_csv('data/raw_snaps.csv', index=False)

# schedules.to_csv('data_local/raw_schedules.csv', index=False)

# Pull 2025 separately for testing
weekly_2025 = nfl.load_player_stats([2025]).to_pandas()
snaps_2025 = nfl.load_snap_counts([2025]).to_pandas()
rankings = nfl.load_ff_rankings().to_pandas()
rankings.to_csv('data/raw_rankings_2025.csv', index=False)
weekly_2025.to_csv('data/raw_weekly_2025.csv', index=False)
snaps_2025.to_csv('data/raw_snaps_2025.csv', index=False)


# lets us get a preliminary look at our data_local
print(weekly.head())
print(weekly.columns.tolist())