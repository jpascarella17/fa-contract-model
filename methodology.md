# Projecting MLB Free Agent Contracts with Statcast and Traditional Statistics

**Author:** [Your name]
**Contact:** [Email / LinkedIn]
**Status:** Work in progress. Last updated [date]
**Repository:** [link]

> Items in `[brackets]` are placeholders to fill in as the project progresses. Delete this note when finished.

---

## 1. Abstract

[Write this last. 4 to 6 sentences covering: the problem, the approach, the headline result versus the baseline, and the main limitation.]

Draft structure:
- Teams value free agents by projecting future performance, then pricing it.
- This project builds a two-stage model: (1) forecast future WAR from underlying skill metrics and age, (2) convert projected value into contract terms.
- Result: [model error versus baseline and versus public projections].
- Key finding: [what Statcast features added beyond traditional stats, if anything].

## 2. Motivation and Research Questions

Free agent contracts are among the largest financial decisions a club makes. Public projections exist, but it is less clear how much underlying-skill data (batted ball quality, pitch shape, plate discipline, bat speed) improves them over traditional stats.

Research questions:
1. How well can a player's next-contract value be predicted from pre-free-agency performance, age, and position?
2. Do Statcast and pitch-shape features improve predictions over a baseline built on WAR and age alone?
3. How do model-implied values compare with what the market actually paid, and where are the largest gaps?

## 3. Scope and Definitions

- **Free agent class:** Players who sign a major league contract in the offseason following season *N* are labeled the class of *N*+1 [confirm convention]. This project's target is the **2027 offseason**, meaning players who become free agents after the 2026 season.
- **Contract value:** Average annual value (AAV) and total guaranteed dollars. Years are modeled separately.
- **Included:** Major league free agent contracts for hitters and pitchers.
- **Excluded or handled separately:** Minor league deals, extensions signed before free agency, international signings from Japan/Korea [decide], and outliers such as Shohei Ohtani (see Section 9).

## 4. Data

| Source | What it provides | Access |
|---|---|---|
| Baseball Savant / Statcast | Exit velocity, barrel rate, xwOBA, sprint speed, pitch movement, spin, release point, bat speed (2023 onward) | `pybaseball` |
| FanGraphs | WAR, plate discipline, Stuff+/Location+/Pitching+, projections | `pybaseball` / exports |
| Spotrac, Cot's Contracts, MLB Trade Rumors | Contract terms, free agent lists, public predictions | [scraping / manual export] |

### 4.1 Data collection
[Describe how you pulled each source, date ranges, and how you handled rate limits and caching.]

### 4.2 Data cleaning
[Name matching across sources (player IDs, e.g. MLBAM/FanGraphs crosswalk), handling of mid-season trades, partial seasons, players with multiple positions.]

### 4.3 Dataset summary
[Table: number of free agent contracts per year, split by hitters and pitchers, AAV distribution.]

## 5. Methodology

### 5.1 Overview
The model has two stages.

**Stage 1: Value projection.** Estimate each player's expected WAR over the contract window using recent performance, underlying skill metrics, and an aging adjustment.

**Stage 2: Market conversion.** Map projected value, age, position, and market context to AAV and contract length.

### 5.2 Baseline model
The baseline uses only traditional inputs: weighted average WAR over the last three seasons, age, and position. Every later model is judged against it.

**Model:** Ridge regression (regularized linear regression)

**Inputs:**
- 3-season weighted bWAR (weights 5-4-3, most recent season counts most)
- Age at signing, plus age squared to capture the aging curve
- Position
- Qualifying offer status

**Data split:**
- Train: 2015-2023 classes
- Test: 2024-2026 classes
- Shohei Ohtani is excluded because his deferred contract and two-way role make him an outlier

**Results:** See Section 7.1.

### 5.3 Feature engineering

**Hitters:** [xwOBA, barrel rate, hard-hit rate, chase rate, whiff rate, sprint speed, bat speed and swing length where available, defensive value, plate appearances]

**Pitchers:** [Stuff+, fastball velocity, pitch movement and spin, release point consistency, strikeout and walk rates, innings pitched, injury history]

**Contextual:** [age at signing, position, qualifying offer, free agent class year, injury days]

Decisions to document:
- How seasons are weighted (recency weighting, regression to the mean for small samples).
- How missing data is handled, especially bat speed for years before 2023.
- How features were selected and why.

### 5.4 Aging curves
[Describe the approach: delta method, positional adjustment, comparison to published curves.]

### 5.5 Models compared
1. Baseline linear regression
2. Regularized regression (ridge / elastic net)
3. Gradient boosting (e.g. XGBoost / LightGBM)
4. [Any additional model]

Because the number of contracts is limited, simpler regularized models are expected to compete with more complex ones. [Report whether that held up.]

### 5.6 Uncertainty
[Describe how prediction intervals are produced: quantile regression, bootstrapping, or residual-based intervals.]

## 6. Validation

- **Split:** Train on classes [2015 to 2023]. Test on [2024 through 2026]. No future data is used in any training step.
- **Metrics:** MAE and RMSE for AAV and total value; interval coverage.
- **External benchmark:** MLB Trade Rumors' predicted contracts for the same classes.
- **Dollar adjustment:** [Describe how contract values were adjusted for market inflation across years.]

## 7. Results

### 7.1 Model comparison

| Model | Contracts | Train / Test | MAE (AAV) | Naive MAE (AAV) |
|---|---|---|---|---|
| Baseline ridge | All | 1,103 / 448 | $3.53M | $5.62M |
| Baseline ridge | $5M+ only | 561 / 213 | $4.38M | $6.57M |
| Baseline + year trend | All | 1,103 / 448 | $3.74M | $5.62M |
| Baseline + year trend | $5M+ only | 561 / 213 | $4.00M | $6.57M |

MAE is the average miss in dollars per year of AAV. The naive model guesses the median training contract for every player. The baseline beats it by about 37% on all contracts and 33% on $5M+ contracts. Each group should be compared only against its own naive number.

Adding a linear year trend removed the underprediction in the test years: the average error on $5M+ contracts moved from -$2.65M to -$0.16M, and MAE on those contracts dropped from $4.38M to $4.00M. On all contracts the average error moved near zero ($-1.28M to +$0.34M), but MAE rose slightly, from $3.53M to $3.74M. A log-transformed target and a peak-WAR feature were also tested and did not help (see the process log in Appendix A).

### 7.2 Does underlying data help?

Savant percentile ranks (expected and actual contact quality, barrel rate, exit velocity, plate discipline, sprint speed for hitters; xERA, fastball velocity, strikeout, walk, whiff, and chase rates for pitchers) were added to the WAR-based model and graded on the same contracts. Only $5M+ contracts with Savant data are included, and each Savant feature is a 3-season weighted average of percentile ranks, matching the WAR weighting.

| Group | Model | Pooled MAE | Years better than WAR-only |
|---|---|---|---|
| Hitters | WAR + age + year trend | $3.93M | n/a |
| Hitters | + Savant percentiles | $3.67M | 3 of 6 |
| Pitchers | WAR + age + year trend | $3.46M | n/a |
| Pitchers | + Savant percentiles | $3.28M | 6 of 6 |

Results come from a rolling-year check: for each year from 2021 to 2026, the models trained on all earlier classes and predicted that class. Savant improved pitcher predictions in every year, by a small margin. For hitters the improvement appeared only in 2024 to 2026 and was slightly negative in 2021 to 2023, possibly because early training sets are small and Savant history is sparse for the oldest classes. On the fixed 2024-2026 test split, a Savant-only model (no WAR) matched the WAR model for hitters ($4.94M vs $4.93M) and was slightly worse for pitchers ($3.87M vs $3.69M).

### 7.3 Benchmark against public predictions
[Compare to MLB Trade Rumors. Be honest about where the model is better, worse, or about equal.]

### 7.4 Largest misses

Errors were checked by weighted WAR band using the WAR-only hitter model, retrained on all earlier classes for each test year from 2021 to 2026. Bias is predicted minus actual AAV, in millions of dollars.

| Weighted WAR | Contracts | Actual AAV | Predicted AAV | Bias |
|---|---|---|---|---|
| Under 0.5 | 8 | 6.8 | 5.7 | -1.2 |
| 0.5 to 1.3 | 53 | 7.2 | 8.2 | +1.0 |
| 1.3 to 2.3 | 56 | 11.0 | 10.9 | -0.1 |
| 2.3 to 3.5 | 38 | 17.5 | 15.3 | -2.1 |
| 3.5 and up | 23 | 28.1 | 21.7 | -6.4 |

The model is well calibrated in the middle of the market but underpredicts stars. In the 2025 and 2026 classes the gap for 3.5+ WAR hitters was about -$9.9M (8 contracts), so the sample at the top is small. Predictions for the highest-value players in the 2027 class should be read as lower bounds. A squared WAR term was tested to capture a star premium and did not help (see Appendix A), so the linear model is kept and the underprediction is reported as a limitation.

## 8. 2027 Free Agent Projections

[Table: player, position, age, projected AAV, projected years, projected total, uncertainty range, MLBTR prediction for comparison.]

Notes:
- The free agent list is as of [date]. Option decisions, extensions, and retirements will change it.
- Projections are model outputs, not predictions of what any specific team will do.

## 9. Limitations

- **Selection bias:** Only players who reached free agency appear in training data, and they skew toward good performers.
- **Small sample:** Few contracts at the top of the market, so extreme values are poorly estimated.
- **New metrics have short histories:** Bat speed has been public only since 2023, which limits how much weight it can carry.
- **Unobserved factors:** Team payroll situation, clubhouse and makeup considerations, medical information, and agent dynamics are not captured.
- **Context a stats-only model can't see:** Teams pay for track record, postseason performance, and injury recoveries. For example, Walker Buehler's 2025 contract ($21M AAV) followed a season of negative WAR, but came after strong earlier seasons and a postseason run, so the model underpredicted it. Ronald Acuña Jr. (a former MVP) is a similar case in the 2027 class: he had 222, 412, and 469 plate appearances in 2024 to 2026, so his weighted WAR reflects reduced playing time and lower production than his 2023 season (8.4 WAR), which falls outside the model's three-season window. Notes like these are kept in a separate column of the predictions file instead of adjusting any model output.
- **Outliers:** Shohei Ohtani is excluded from training and evaluation. His contract is mostly deferred, so the headline AAV overstates what the team pays today, and his two-way role does not fit a single hitter or pitcher WAR.
- **International signees:** Players coming from Japan, Korea, or Cuba with no prior MLB season have no bWAR, so they are left out of the model.
- **Short 2020 season:** WAR from 2020 covers only 60 games and is not rescaled, which affects the 2021 to 2023 classes that look back at it.
- **Name matching:** Contracts are joined to stats by player name. Five contracts where one name matched two different players (Chris Young, Luis Garcia) were excluded rather than guessed.
- **Market change:** Spending patterns shift over time. The baseline underpredicts every class from 2022 on, and the gap widens in the test years, so a year adjustment is tested in Section 7. The collective bargaining agreement also expires after the 2026 season, which could change the 2027 market in ways past data cannot show.
- **Qualifying offers:** Players who accept a qualifying offer take a formula-set one-year price instead of a market contract, so their market value is unobserved. They are excluded from training, which may remove some below-market cases.

## 10. Future Work

- Add team-level context (payroll, competitive window, positional need).
- Model contract structure (opt-outs, deferrals, incentives) rather than only AAV and years.
- Extend to arbitration-eligible players and extensions.
- [Your ideas]

## 11. Reproducing This Work

```bash
git clone [repo-url]
cd [repo-name]
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run order:
1. `notebooks/01_data_collection.ipynb`
2. `notebooks/02_cleaning.ipynb`
3. `notebooks/03_baseline.ipynb`
4. `notebooks/04_feature_models.ipynb`
5. `notebooks/05_validation.ipynb`
6. `notebooks/06_2027_projections.ipynb`

## 12. References and Data Credits

- Baseball Savant / Statcast, MLB Advanced Media
- FanGraphs
- Spotrac, Cot's Baseball Contracts
- MLB Trade Rumors
- `pybaseball` library
- [Papers or articles on aging curves and contract valuation that you read]

---

## Appendix A: Process Log

| Date | Decision or finding | Why |
|---|---|---|
| 2026-10-14 | Built the 2024 free agent class from Spotrac (copied into a spreadsheet, saved as CSV) | Hand-copying ~150 contracts per year is manageable and avoids scraping a site against its terms of use |
| 2026-10-14 | Dropped rows with $0 value or 0 years | These were non-guaranteed or minor league deals, not real major league contracts |
| 2026-10-14 | Created a qualifying_offer flag from the "QO" tag in player names, then removed the tag | Qualifying offers affect market value, and the tag was baked into the name field |
| 2026-10-14 | Simplified positions to the first listed one (e.g. SP/SP2 becomes SP) | Spotrac adds role notes that would create dozens of tiny categories |
| 2026-10-14 | Added player_type (pitcher or hitter) based on position | The model will treat hitters and pitchers separately |
| 2026-10-14 | Recalculated AAV as total value divided by years | Avoids trusting rounded values from the source |
| 2026-10-14 | For players listed twice, kept the larger contract | The duplicates were $740K league-minimum deals signed after release, not the free agent contract |
| 2026-10-14 | Left small contracts (under about $5M) in for now | Will test the model with and without them before deciding |
| 2026-10-14 | Flagged Shohei Ohtani's $700M deal as an outlier | Most of it is deferred, so the headline value overstates what the team pays today |
| 2026-10-15 | Added 2026 class as a third test year; final model will be retrained on all years before predicting 2027 | More test contracts give a more reliable accuracy estimate, and the final predictions should use the newest market data |
| 2026-10-15 | Collected free agent classes from 2015 to 2026 | Statcast-based features are only reliable for later classes, so the baseline model uses all years and the advanced model uses the years with Statcast data |
| 2026-10-16 | Noted market inflation as a modeling issue; plan to test year-as-feature vs. contracts scaled to a league-wide benchmark | Raw dollars across 2015 to 2026 would let market drift look like differences in player quality |
| 2026-10-16 | Plan to compare models trained on all contracts vs. $5M+ only; full table kept in contracts.csv | Small deals are present in every class, but they are noisier and may not matter for the 2027 predictions; the effect will be tested, not assumed |
| 2026-10-17 | Using Baseball Reference WAR (bWAR) via pybaseball as the value metric; FanGraphs blocked automated downloads (HTTP 403) | bWAR is available in one bulk file with MLBAM player IDs; Savant percentile data will supply the advanced features later |
| 2026-10-17 | Joined contracts to bWAR by normalized name and prior season; excluded 5 contracts where a name matched two different players (Chris Young, Luis Garcia); flagged international signees | A wrong match would attach another player's stats to a contract, so ambiguous cases are dropped rather than guessed |
| 2026-10-19 | Built 3-season weighted bWAR (weights 5-4-3, most recent highest); missing seasons for known MLB players count as 0; international signees left blank | A multi-season average is less noisy than one year and correlates better with AAV (0.74 vs 0.70); the 2020 short season is not rescaled, which is a known limitation |
| 2026-10-19 | Pulled birth dates from the MLB Stats API using MLBAM player IDs; age at signing measured on Dec 1 after the final season | The Baseball Reference and Chadwick files contain no birth dates; age is a key driver of contract length and value |
| 2026-10-19 | Built ridge regression baseline (3-season weighted bWAR, age, age squared, position, qualifying offer); train 2015-2023, test 2024-2026; Ohtani excluded | Establishes the benchmark that Statcast features and the inflation adjustment must beat |
| 2026-10-19 | Checked baseline errors by year: the model underpredicts every class from 2022 on, and the gap widens in the test years (-0.84M in 2024 to -1.86M in 2026); largest misses are star contracts at roughly half of actual AAV | Confirms market inflation and a star premium that a straight-line model can't capture; next step is testing a year trend and a log target |
| 2026-10-19 | Tested year trend and log target: the year trend removes the underprediction in test years and lowers MAE on $5M+ contracts ($4.38M to $4.00M) but slightly raises it on all contracts; the log target did not help | Market inflation is real for larger contracts; plan to model $5M+ contracts with a linear year trend |
| 2026-10-19 | Tested peak single-season WAR over the prior 5 years as an added feature; MAE changed by less than 1% ($3.74M to $3.71M all contracts, $4.00M to $3.99M for $5M+) | A longer track record does not add measurable information beyond the 3-season weighted WAR; feature dropped to keep the model simple |
| 2026-10-19 | Chose Baseball Savant percentile ranks (via pybaseball) as the source of advanced features for a second model, to be compared against the WAR-based baseline on the same contracts | Percentiles are ranked within each season, so they are comparable across years; a side-by-side comparison measures how much underlying skill adds beyond WAR and age |
| 2026-10-19 | Downloaded Savant percentile ranks for hitters and pitchers, 2015-2026 (savant_hitters.csv, savant_pitchers.csv); bat speed is available only from 2023; about 35-42% of listed players per season have batted-ball metrics | Savant history starts in 2015, so the 2015 class has none and the 2016-2017 classes have fewer than three seasons; players without the main quality metric are excluded from the Savant comparison, and both models are graded on the same contracts |
| 2026-10-19 | Compared WAR-only (A), WAR + Savant percentiles (B), and Savant-only (C) on $5M+ contracts with Savant data; train 2015-2023, test 2024-2026. Hitters (214 train / 77 test): A $4.93M, B $4.18M, C $4.94M. Pitchers (271 / 127): A $3.69M, B $3.43M, C $3.87M | Savant features lowered error by about 15% for hitters and 7% for pitchers; Savant alone matched WAR for hitters; test sets are small and from a single split, so a rolling-year check follows |
| 2026-10-19 | Rolling-year check (train on all prior years, test on each of 2021-2026) of WAR-only vs WAR + Savant. Hitters: pooled MAE $3.93M vs $3.67M, Savant better in 3 of 6 years (gains only in 2024-2026). Pitchers: $3.46M vs $3.28M, Savant better in 6 of 6 years | The single-split hitter gain (15%) was overstated; the pooled gain is about 7% for hitters and 5% for pitchers; using the WAR + Savant model for both in the 2027 predictions |
| 2026-10-19 | Built the 2027 free agent list from MLB Trade Rumors' projected 2026-27 class (fa_2027_list.csv), keeping option and opt-out notes | The list is projected, so options, extensions, and the expiring CBA may change who reaches free agency; it will be re-checked after the season |
| 2026-10-19 | Planned an option-decision analysis for 2027 free agents with options: compare projected AAV to option salary minus buyout; call club options exercise or decline, player options exercise or decline, mutual options likely declined; label close calls (within about one MAE) as toss-ups | Turns the projections into an actionable decision; option salary is a one-year price while the model predicts AAV on contracts of mixed length, so the results are approximate |
| 2026-10-19 | Parsed MLB Trade Rumors' 2026-27 list into fa_2027_list.csv; players listed at multiple positions collapsed to one row with all positions kept; option, opt-out, and buyout text preserved | Position labels will be resolved when features are built; option notes feed the option-decision analysis, which also covers opt-outs |
| 2026-10-19 | Built 2027 free agent features (fa_2027_features.csv): matched players to MLB IDs by normalized name for 2024-2026, using MLBTR's listed age to separate same-name players; 3-season weighted bWAR and Savant averages with the same 5-4-3 weights as training; age measured on Dec 1, 2026; qualifying offer set to 0 as a placeholder | Keeps the 2027 inputs defined exactly as the training inputs were; qualifying offers are not known until after the World Series |
| 2026-10-19 | Generated first 2027 AAV predictions (outputs/fa_2027_predictions.csv): final ridge models retrained on all $5M+ contracts from 2015 to 2026, separate for hitters and pitchers; WAR + Savant model where Savant data exists, WAR-only otherwise; ranges from the 10th and 90th percentile of rolling out-of-sample errors (2021-2026); Skubal flagged as an outlier; qualifying offers set to 0 as a placeholder | Final models use all available contracts; ranges reflect real out-of-sample error but are the same width for every player, so they understate uncertainty for stars; predictions below $5M mean a small deal because training was limited to $5M+ |
| 2026-10-19 | Sanity-checked the 2027 predictions against hitters in the 2025-26 classes with similar weighted WAR (1.3 to 2.3): 18 contracts, median AAV $10.1M, middle half $7.0M to $14.4M. Several predictions (Grisham $18.9M, Acuña $20.8M, Crawford $17.6M) sit above that range | The model may overshoot mid-tier hitters; one possible cause is one-year qualifying-offer acceptances in the training data (for example a $22.0M one-year deal that matches the qualifying offer amount), which are set by formula rather than by the market; being checked |
| 2026-10-19 | Found that one-year qualifying-offer acceptances (for example five 2026 deals at exactly $22.02M and Martinez at $21.05M in 2025) were in the training data; removed them into contracts_model.csv and re-ran the 2027 predictions | Accepted qualifying offers are priced by a league-wide formula, not by the market, so they mislabel market value; their true market price is unobserved, so they are dropped instead of relabeled |
| 2026-10-20 | Removed qualifying-offer acceptances from training and re-ran the 2027 predictions: changes were at most $0.4M for the top 15 players (average -$0.1M) | These were not the cause of the mid-tier overshoot suspected earlier; the exclusion is kept because those salaries are set by formula, not the market; the sanity check against comparable hitters was matched on WAR alone, so it is being replaced by a calibration check on past out-of-sample errors |
| 2026-10-20 | Checked calibration by weighted WAR band on out-of-sample errors (2021-2026, WAR-only hitter model): bias is near zero for 1.3-2.3 WAR (-$0.1M, 56 contracts) but -$2.1M for 2.3-3.5 WAR and -$6.4M for 3.5+ WAR (about -$9.9M in 2025-26); testing a squared WAR term | The model compresses toward the middle: mid-tier predictions are reasonable, star predictions are too low; this replaced the earlier crude comparable-hitters check |
| 2026-10-21 | Tested adding a squared WAR term to capture a star premium: hitter MAE $3.83M to $3.88M, bias for 3.5+ WAR hitters -$6.4M to -$6.0M; pitcher MAE $3.47M to $3.44M, bias for 3.5+ WAR -$5.2M to -$5.0M | The squared term did not meaningfully reduce the underprediction of stars and worsened the 2.3-3.5 WAR band; kept the linear WAR model and treat star predictions as likely lower bounds |
| 2026-10-21 | Verified the qualifying-offer cleanup: 18 acceptances dropped (1,618 to 1,600 contracts); within each class they share one exact salary ($15.80M in 2016 through $22.02M in 2026) | Confirms the dropped deals are formula-priced; 11 other one-year deals with a QO flag were kept because their salaries were negotiated |
| 2026-10-21 | Chose MLB Trade Rumors' annual Top 50 Free Agents With Predictions for the 2024, 2025, and 2026 classes as an external benchmark; their predicted AAV (total divided by years) will be compared to the model's out-of-sample predictions for the same players | A respected public projection is the standard to measure against; international signees and players outside the top 50 are excluded, so the comparison covers the high end of the market only |
| 2026-10-21 | Parsed MLBTR's Top 50 Free Agents With Predictions for the 2024, 2025, and 2026 classes into mlbtr_predictions.csv (150 predictions; MLBTR's heading format changes by year, so the parser handles three styles); raw article text is kept out of the repo | Provides the external benchmark; only the extracted numbers (years, total, AAV) are published |


## Appendix B: Data Dictionary

| Field | Description | Source |
|---|---|---|
| [field] | [description] | [source] |
