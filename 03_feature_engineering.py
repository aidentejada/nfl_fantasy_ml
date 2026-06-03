import pandas as pd

skill = pd.read_csv('data/clean_weekly.csv')

# sort so rolling calculations go in the right direction
skill = skill.sort_values(['player_id', 'season', 'week'])

# target share — what % of team targets is this player getting
team_targets = skill.groupby(['season', 'week', 'team'])['targets'].transform('sum')
skill['target_share'] = skill['targets'] / team_targets

# snap share — how much is this player playing on offense
# we already have offense_pct from snaps so you can use that directly

skill['snap_share'] = skill['offense_pct']

# air yards share — reveals players who are deeply targeted but might
# lack high catch totals due to low completion rates or poor quarterback play.
team_air = skill.groupby(['season', 'week', 'team'])['receiving_air_yards'].transform('sum')
skill['air_yards_share'] = skill['receiving_air_yards'] / team_air


# rolling 4 week averages - we dont want one - offs
# a player whose target share is TRENDING UP is more valuable than their raw stats show (aka getting more chances even if stats dont change)
skill['rolling_target_share'] = (
    skill.groupby('player_id')['target_share']
    .transform(lambda x: x.rolling(4, min_periods=1).mean())
)

skill['rolling_snap_share'] = (
    skill.groupby('player_id')['snap_share']
    .transform(lambda x: x.rolling(4, min_periods=1).mean())
)

skill['rolling_air_yards_share'] = (
    skill.groupby('player_id')['air_yards_share']
    .transform(lambda x: x.rolling(4, min_periods=1).mean())
)

skill.to_csv('data/features.csv', index=False)
print("Features saved!")
print(skill.shape)