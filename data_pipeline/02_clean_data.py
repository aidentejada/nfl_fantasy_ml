import pandas as pd

# load and combine both training and 2025 data together into one
weekly_train = pd.read_csv('data/raw_weekly.csv', low_memory=False)
weekly_2025 = pd.read_csv('data/raw_weekly_2025.csv')
weekly = pd.concat([weekly_train, weekly_2025], ignore_index=True)

snaps_train = pd.read_csv('data/raw_snaps.csv')
snaps_2025 = pd.read_csv('data/raw_snaps_2025.csv')
snaps = pd.concat([snaps_train, snaps_2025], ignore_index=True)


# make all names match eachother since they are different across data_local files
weekly['player_display_name'] = weekly['player_display_name'].str.strip().str.lower()
snaps['player'] = snaps['player'].str.strip().str.lower()

# we ONLY want skill positions

skill = weekly[weekly['position'].isin(['WR', 'RB', 'TE', 'QB'])]
# must adjust the snaps csv file since when we merge it will just bring irrelevant bs in
snaps = snaps[snaps['position'].isin(['WR', 'RB', 'TE', 'QB'])]

# Merge on player name AND week AND season so you match the right game -
# left join means: keep all weekly rows, only bring in snap data_local where it matches
skill = skill.merge(
    snaps[['player', 'week', 'season', 'offense_snaps', 'offense_pct']],
    left_on=['player_display_name', 'week', 'season'],
    right_on=['player', 'week', 'season'],
    how='left'
)


# weed out shitty mfs who dont play
skill = skill[skill['offense_snaps'] > 0]
skill = skill.dropna(subset=['targets', 'carries', 'receptions'], how='all')

# save new refined data_local
skill.to_csv('data/clean_weekly.csv', index=False)
print("Cleaned data saved!")
print(skill.shape)
print(skill['position'].value_counts())