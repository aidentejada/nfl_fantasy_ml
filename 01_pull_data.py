import nflreadpy as nfl
import pandas as pd

# weekly player stats (very thick data frame btw!)
weekly = nfl.load_player_stats([2025]).to_pandas()
rankings = nfl.load_ff_rankings().to_pandas()
rankings.to_csv('data/raw_rankings.csv', index=False)

# snap counts
snaps = nfl.load_snap_counts([2025]).to_pandas()

# Schedules (for matchup/opponent data)
schedules = nfl.load_schedules([2025]).to_pandas()

# lets us get a preliminary look at our data
print(weekly.head())
print(weekly.columns.tolist())

# Save so you don't re-download every time
weekly.to_csv('data/raw_weekly.csv', index=False)
snaps.to_csv('data/raw_snaps.csv', index=False)
schedules.to_csv('data/raw_schedules.csv', index=False)