# TODO — Model Ready Checklist

## Angel (Data Pipeline)
- [ ] Fix `air_yards_share` in 03 — change `passing_air_yards` to `receiving_air_yards`
- [ ] Fix `dropna` in 02 — add `how='all'` so valid rows aren't deleted by position
- [ ] Pull 2020-2024 seasons for training, keep 2025 separate for real world testing
- [ ] Clone the repo properly and push latest edits before starting

## Aiden (ML Model)
- [ ] Wait for cleaned dataset from Angel
- [ ] Set up walk-forward validation with TimeSeriesSplit by season
- [ ] Train XGBoost model with `next_week_points` as target variable
- [ ] Tune hyperparameters
- [ ] Add SHAP for explainability
- [ ] Evaluate model — does it beat ECR as a predictor?

## Both
- [ ] Decide on final feature set before training
- [ ] Set up shared GitHub properly