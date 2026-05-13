import pandas as pd

# load from the raw data csv file (pulled from 01_pull_data)
weekly = pd.read_csv('data/raw_weekly.csv')
snaps = pd.read_csv('data/raw_snaps.csv')
# make all names match eachother since they are different across data files
weekly['player_display_name'] = weekly['player_display_name'].str.strip().str.lower()
snaps['player'] = snaps['player'].str.strip().str.lower()

# we ONLY want skill positions

skill = weekly[weekly['position'].isin(['WR', 'RB', 'TE', 'QB'])]
# must adjust the snaps csv file since when we merge it will just bring irrelevant bs in
snaps = snaps[snaps['position'].isin(['WR', 'RB', 'TE', 'QB'])]

# Merge on player name AND week AND season so you match the right game -
# left join means: keep all weekly rows, only bring in snap data where it matches
skill = skill.merge(
    snaps[['player', 'week', 'season', 'offense_snaps', 'offense_pct']],
    left_on=['player_display_name', 'week', 'season'],
    right_on=['player', 'week', 'season'],
    how='left'
)


# weed out shitty mfs who dont play
skill = skill[skill['offense_snaps'] > 0]
skill = skill.dropna(subset=['targets', 'carries', 'receptions'])

# save new refined data
skill.to_csv('data/clean_weekly.csv', index=False)
print("Cleaned data saved!")
print(skill.shape)
print(skill['position'].value_counts())
