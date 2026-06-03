import pandas as pd
# shoutout claude for assistance
# for reference - ecr is Expert Consensus Rankings - so less interpreting needed compared to ADP
skill = pd.read_csv('data_local/features.csv')

rankings = pd.read_csv('data_local/raw_rankings_2025.csv')

# standardize names so we can merge
skill['player_display_name'] = skill['player_display_name'].str.strip().str.lower()
rankings['player_name'] = rankings['player'].str.strip().str.lower()

# filter to redraft overall only and drop duplicates immediately (we can expand to dynasty later)
rankings = rankings[rankings['page_type'] == 'redraft-overall']
rankings = rankings.drop_duplicates(subset=['player_name'])

# merge ECR in b4 filtering so the column actually exists in the skill dataframe

skill = skill.merge(
    rankings[['player_name', 'ecr']],
    left_on='player_display_name',
    right_on='player_name',
    how='left'
)

# filter using ecr since the column exists
# this removes first round stars and bench shitters, keep anyone unranked (likely low owned/injured - unlikely to be a sleeper tho)
skill = skill[(skill['ecr'] > 20) | (skill['ecr'].isna())]
skill = skill[(skill['ecr'] <= 175) | (skill['ecr'].isna())]

# sort before any rolling calculations
skill = skill.sort_values(['player_id', 'season', 'week'])

# determine next weeks points
skill['next_week_points'] = (
    skill.groupby('player_id')['fantasy_points_ppr']
    .shift(-1)
)

# determine points jump from week to week
skill['points_jump'] = skill['next_week_points'] - skill['fantasy_points_ppr']

# rolling average of points over last 3 weeks (this is a consistency check like are they actually consistent in performance)
skill['rolling_points'] = (
    skill.groupby('player_id')['fantasy_points_ppr']
    .transform(lambda x: x.rolling(3, min_periods=2).mean())
)

# determines certain trends
skill['points_trend'] = (
    skill.groupby('player_id')['rolling_points']
    .transform(lambda x: x.diff())
)
skill['target_share_trend'] = (
    skill.groupby('player_id')['rolling_target_share']
    .transform(lambda x: x.diff())
)
skill['snap_share_trend'] = (
    skill.groupby('player_id')['rolling_snap_share']
    .transform(lambda x: x.diff())
)

# score players on a point system (i tried using requirements
# but it ended up only returned bench players or first round picks)
skill['score_points_jump'] = (skill['points_jump'] >= skill['points_jump'].quantile(0.80)).astype(int)
skill['score_points_trend'] = (skill['points_trend'] > 0).astype(int)
skill['score_target_trend'] = (skill['target_share_trend'] > 0).astype(int)
skill['score_snap_trend'] = (skill['snap_share_trend'] > 0).astype(int)
skill['score_floor'] = (skill['fantasy_points_ppr'] >= 8).astype(int)

skill['sleeper_score'] = (
    skill['score_points_jump'] +
    skill['score_points_trend'] +
    skill['score_target_trend'] +
    skill['score_snap_trend'] +
    skill['score_floor']
)

skill['is_sleeper'] = (skill['sleeper_score'] >= 4).astype(int)

skill = skill.dropna(subset=['next_week_points'])

# save before display
skill.to_csv('data_local/final_dataset.csv', index=False)
print("\n to aiden's master slave we go!")

# sanity check
points_threshold = skill['points_jump'].quantile(0.80)
print(f"Total players labeled: {len(skill)}")
print(f"Sleepers (1): {skill['is_sleeper'].sum()}")
print(f"Non-sleepers (0): {(skill['is_sleeper'] == 0).sum()}")
print(f"Sleeper threshold was: {points_threshold:.2f} fantasy points jump")
print(f"Players removed by ECR filter: {len(skill[skill['ecr'] <= 20])}")




train = skill[skill['season'] <= 2024].copy()
test = skill[skill['season'] == 2025].copy()

# NOTE FOR AIDEN: ECR column is NaN for 2020-2024 since rankings are
# current season only. ECR filter is applied to 2025 test data only.

test = test[(test['ecr'] > 20) | (test['ecr'].isna())]
test = test[(test['ecr'] <= 150) | (test['ecr'].isna())]



# Reorder columns so next_week_points is last as Aiden requested
# First grab all columns except the ones we want at the end
front_cols = [col for col in train.columns
              if col not in ['is_sleeper', 'next_week_points']]

# Build final column order
final_cols = front_cols + ['is_sleeper', 'next_week_points']

train = train[final_cols]
test = test[final_cols]

# Save separately
train.to_csv('data_local/final_dataset_train.csv', index=False)
test.to_csv('data_local/final_dataset_test.csv', index=False)

print(f"Training set saved: {len(train)} rows ({train['season'].min()}-{train['season'].max()})")
print(f"Test set saved: {len(test)} rows (2025 only)")
print(f"Total features: {len(final_cols)} columns")
print(f"Training sleepers: {train['is_sleeper'].sum()}")
print(f"Test sleepers: {test['is_sleeper'].sum()}")


# this is all based on  the data_local (ts was good for debugging and allows me to see everything and determine if it makes sense)
sleepers = test[test['is_sleeper'] == 1].copy()
sleepers = sleepers.sort_values('points_jump', ascending=False)

print("\n🏈 TOP 10 SLEEPERS OVERALL:")
print(sleepers[['player_display_name', 'position', 'season', 'week',
                'fantasy_points_ppr', 'next_week_points', 'points_jump',
                'rolling_target_share', 'rolling_snap_share']].head(10).to_string())

print("\n📊 TOP 5 SLEEPERS BY POSITION:")
for pos in ['WR', 'RB', 'TE', 'QB']:
    pos_sleepers = sleepers[sleepers['position'] == pos].head(5)
    print(f"\n--- {pos} ---")
    print(pos_sleepers[['player_display_name', 'season', 'week',
                         'fantasy_points_ppr', 'next_week_points',
                         'points_jump', 'rolling_target_share']].to_string())

# single best sleeper
best = sleepers.iloc[0]
print(f"\n⭐ BEST SLEEPER IN THE DATASET:")
print(f"  Player:        {best['player_display_name']}")
print(f"  Position:      {best['position']}")
print(f"  ECR:           {best['ecr']:.0f}" if pd.notna(best['ecr']) else "  ECR: Unranked")
print(f"  Season/Week:   {int(best['season'])} Week {int(best['week'])}")
print(f"  Points that week:  {best['fantasy_points_ppr']:.1f}")
print(f"  Points next week:  {best['next_week_points']:.1f}")
print(f"  Jump:          +{best['points_jump']:.1f} pts")
print(f"  Rolling target share: {best['rolling_target_share']:.1%}")


# this just creates a reference list for all the stats and their meaning for clarity or confusion

dictionary = pd.DataFrame([
    # Raw identifiers
    {'column': 'player_id',             'description': 'Unique player identifier from nflverse'},
    {'column': 'player_display_name',   'description': 'Player full name (lowercased)'},
    {'column': 'position',              'description': 'Player position (WR, RB, TE, QB only)'},
    {'column': 'season',                'description': 'NFL season year'},
    {'column': 'week',                  'description': 'NFL week number'},
    {'column': 'recent_team',           'description': 'Team abbreviation the player was on that week'},

    # Raw stats
    {'column': 'fantasy_points_ppr',    'description': 'PPR fantasy points scored that week'},
    {'column': 'targets',               'description': 'Number of times targeted that week'},
    {'column': 'receptions',            'description': 'Number of catches that week'},
    {'column': 'carries',               'description': 'Number of rushing attempts that week'},
    {'column': 'air_yards',             'description': 'Total air yards on targets that week'},
    {'column': 'offense_snaps',         'description': 'Raw number of offensive snaps played'},
    {'column': 'offense_pct',           'description': 'Percentage of team offensive snaps played'},

    # Engineered features (created in 03_feature_engineering.py)
    {'column': 'target_share',          'description': 'Targets as % of total team targets that week'},
    {'column': 'snap_share',            'description': 'Snap % directly from snaps data_local (offense_pct)'},
    {'column': 'air_yards_share',       'description': 'Air yards as % of total team air yards that week'},
    {'column': 'rolling_target_share',  'description': '4 week rolling average of target share'},
    {'column': 'rolling_snap_share',    'description': '4 week rolling average of snap share'},
    {'column': 'rolling_air_yards_share', 'description': '4 week rolling average of air yards share'},

    # Label creation columns (created in 04_label_creation.py)
    {'column': 'next_week_points',      'description': 'PPR fantasy points scored the following week (what we are predicting)'},
    {'column': 'points_jump',           'description': 'Difference between next week points and this week points'},
    {'column': 'rolling_points',        'description': '3 week rolling average of fantasy points'},
    {'column': 'points_trend',          'description': 'Week over week change in rolling points average (positive = trending up)'},
    {'column': 'target_share_trend',    'description': 'Week over week change in rolling target share (positive = getting more targets)'},
    {'column': 'snap_share_trend',      'description': 'Week over week change in rolling snap share (positive = getting more snaps)'},

    # Scoring system
    {'column': 'score_points_jump',     'description': '1 if points jump is in top 20% of dataset, else 0'},
    {'column': 'score_points_trend',    'description': '1 if rolling points average is trending up, else 0'},
    {'column': 'score_target_trend',    'description': '1 if target share is trending up, else 0'},
    {'column': 'score_snap_trend',      'description': '1 if snap share is trending up, else 0'},
    {'column': 'score_floor',           'description': '1 if player scored at least 8 PPR points that week, else 0'},
    {'column': 'sleeper_score',         'description': 'Sum of all score columns above (0-5)'},

    # Target variable
    {'column': 'is_sleeper',            'description': 'TARGET VARIABLE — 1 if sleeper_score >= 4, else 0. This is what the model predicts'},

    # ECR
    {'column': 'ecr',                   'description': 'Expert Consensus Ranking (redraft overall) — lower is more valuable. Filtered to ECR 21-150 only'},
])

dictionary.to_csv('data_local/data_dictionary.csv', index=False)
