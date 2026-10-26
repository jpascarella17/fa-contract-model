# Projecting MLB Free Agent Contracts with Statcast and Traditional Statistics

**Author:** Joseph Pascarella
**Contact:** josephpascarella17@gmail.com / www.linkedin.com/in/
joseph-pascarella-aa58463a8

**Status:** Work in progress. Last updated 10-26-2026
**Repository:** [link]

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

The model's out-of-sample AAV predictions were compared to MLB Trade Rumors' annual Top 50 Free Agents With Predictions for the 2024, 2025, and 2026 classes. For each class the model trained only on earlier years. MLBTR's AAV is their predicted total divided by their predicted years. Only players with an MLB history and a market contract in the model's data are scored (120 of 150), so international signees, players who accepted a qualifying offer, and contracts under $5 million are excluded. One further player (Jakob Junis, 2024) was left unscored because MLBTR spells his first name differently from the contracts table.

| Class | Players scored | MLBTR MAE | Model MAE | MLBTR bias | Model bias |
|---|---|---|---|---|---|
| 2024 | 37 | $2.19M | $3.34M | +$0.55M | -$1.71M |
| 2025 | 44 | $3.44M | $4.21M | -$1.56M | -$2.22M |
| 2026 | 39 | $3.72M | $4.77M | -$2.10M | -$3.48M |
| All | 120 | $3.15M | $4.13M | -$1.09M | -$2.47M |

MAE is the average miss in millions of dollars per year of AAV; bias is predicted minus actual, so negative means too low. MLBTR's predictions were closer in every class, and the model's average miss was about 31% larger. Both sources underpredicted recent classes, and the gap widened: the model's bias grew from -$1.71M in 2024 to -$3.48M in 2026. This is likely partly because recent deals were shorter with higher annual values than predicted (for example, MLBTR projected Kyle Tucker at 11 years and $400 million, and he signed for 4 years and $240 million), which the model cannot capture because it does not yet predict contract length. MLBTR's own predictions missed contract length by 0.9 years and total value by about $20 million on average. A stats-only model landing within about $1 million per year of an expert panel that also weighs injuries, team needs, and market information is a reasonable result, but the model is behind.

The gap is concentrated at the top of the market. Grouping the 120 scored players by actual AAV:

| Actual AAV | Players | MLBTR MAE | Model MAE | MLBTR bias | Model bias |
|---|---|---|---|---|---|
| Under $10M | 21 | $2.36M | $2.60M | +$1.34M | +$2.20M |
| $10M-$20M | 69 | $2.58M | $2.84M | -$0.15M | -$1.43M |
| $20M and up | 30 | $5.02M | $8.16M | -$4.94M | -$8.14M |

MLBTR was closer on 73 of 120 players (61%). Roughly 80% of the model's extra error comes from the 30 contracts of $20 million or more; below that level the two are within about $0.3 million of each other. Grouping by actual contract size exaggerates underprediction for both sources, since the players with the largest deals are the ones both missed on the low side, but the comparison between the two is on the same players.

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

### 7.5 Contract length and total value

Contract length (guaranteed years, capped at 8) was modeled with a ridge regression on the same inputs as AAV (three-season weighted bWAR, age, age squared, qualifying offer status, a year trend, and position). For each test class from 2021 to 2026 the model trained only on earlier classes (433 contracts of $5 million or more). Total value is predicted AAV times predicted years.

| Actual contract size | Contracts | Actual years | Predicted years | Model MAE | Naive MAE |
|---|---|---|---|---|---|
| Under $10M AAV | 231 | 1.44 | 1.64 | 0.59 | 0.69 |
| $10M-$20M | 144 | 2.19 | 2.08 | 0.80 | 0.92 |
| Over $20M | 58 | 4.55 | 3.70 | 1.76 | 2.69 |
| All | 433 | | | 0.81 | 1.03 |

The naive model guesses the median training length (two years). The model's average error is about 21% lower than the naive guess, mostly from large contracts. It is within one year of the actual length 71% of the time, compared with 87% for the naive guess, so for typical short deals a flat two-year guess is almost as good. Large contracts are compressed, as with AAV: the model predicts 3.7 years where the average over-$20M deal ran 4.55. Deals worth $20 million a year or more were also shorter in 2024-2026 (about 4.0 years on average) than in 2015-2023 (about 5.3).

Compared with MLB Trade Rumors on the same 120 players in the 2024-2026 benchmark:

| Group | Players | Years MAE (MLBTR / model) | Total value MAE (MLBTR / model) | Total value bias (MLBTR / model) |
|---|---|---|---|---|
| All scored | 120 | 0.9 / 1.0 | $19.9M / $24.8M | +$7.6M / -$10.9M |
| $20M+ AAV | 35 | 1.7 / 1.7 | $42.2M / $57.1M | +$12.6M / -$40.6M |

The model's contract length is close to MLBTR's, but its total value is further behind because errors in AAV and years compound for the largest contracts, where both run low. MLBTR's totals tended to run high because it projected longer deals than players signed. Total value predictions for the highest-value players should be read as lower bounds.

## 8. 2027 Free Agent Projections

Preliminary projections for 253 of the 257 players on MLB Trade Rumors' projected 2026-27 free agent list (as of October 19, 2026); four had no 2024-2026 MLB season in the data. AAV projections were generated October 19, 2026, and contract length and total value on October 25, 2026 (total is AAV times whole predicted years). Full results are in `outputs/fa_2027_contract_projections.csv`, with a range of plus or minus one year on length. A comparison with MLBTR's own 2027 predictions will be added when they publish their Top 50 after the World Series.

| Player | Pos | Age | AAV | Years | Total | Note |
|---|---|---|---|---|---|---|
| Tarik Skubal | SP | 30.0 | $32.2M | 5 | $161M | Outlier; lower bound |
| Seiya Suzuki | RF | 32.3 | $24.0M | 3 | $72M | |
| Drew Rasmussen | SP | 31.3 | $22.9M | 3 | $69M | $20MM club option |
| Randy Arozarena | LF | 31.8 | $21.3M | 3 | $64M | |
| Ronald Acuña Jr. | RF | 29.0 | $20.8M | 3 | $62M | $17MM club option |
| Freddy Peralta | SP | 30.5 | $19.3M | 3 | $58M | |
| Ian Happ | LF | 32.3 | $19.2M | 3 | $58M | |
| Michael King | SP | 31.5 | $19.1M | 3 | $57M | Opt-out |
| Trevor Rogers | SP | 29.0 | $18.2M | 3 | $55M | |
| Ryan Jeffers | C | 29.5 | $18.1M | 3 | $54M | |

Notes:
- The free agent list is projected. Option decisions, extensions, and retirements will change it, and it will be refreshed after the season.
- Projections are model outputs, not predictions of what any specific team will do.
- Tarik Skubal is an outlier: no past contract resembles what he is expected to receive, so the model's projection ($32.2M a year, 5 years, $161M) is a floor. The closest precedent by age and weighted WAR is Gerrit Cole in 2020 (age 29.2, 5.2 weighted WAR; 9 years and $324M, or $36M a year). The largest pitcher contracts of three or more years in the data, excluding Shohei Ohtani, ran from about $34 million to $43 million a year, and the longest for pitchers in their early thirties ran 7 to 9 years ($245 million to $324 million). Dollar figures are nominal and do not adjust for inflation or deferred money. MLB Trade Rumors has written that he should become the first $400 million pitcher if he stays healthy. These reference figures are not model output.
- Players with club, mutual, or player options (for example Ronald Acuña Jr. and Drew Rasmussen) may never reach free agency, so their rows are not forecasts of a market contract.
- The length model predicts one year for 156 of 253 players, two years for 81, three for 15, and five for one (Skubal). It produces no four-year deals, so long contracts for the top of the class are not captured, and total values for the largest contracts should be read as lower bounds.
- Predictions under $5 million only mean "a small deal", since the models were trained on contracts of $5 million or more.
- Qualifying offers are not yet known and are set to zero for all players, so players likely to receive one may be projected slightly low.

### Option and opt-out calls

For the 61 players with an option or opt-out noted by MLB Trade Rumors (Kyle Freeland is excluded because his player option did not vest), each projected AAV was compared with what the option costs. Club and mutual options use the option salary minus any buyout; player options use the option salary; opt-outs compare the projected AAV (plus the buyout spread over the remaining years) with the remaining guaranteed money per year. Gaps within $4 million, about the model's average AAV miss, are labeled toss-ups; larger gaps are labeled lean (up to $8 million) or strong. A mutual option needs both sides to agree, so it is labeled by which side would want it. Full results are in `outputs/fa_2027_option_calls.csv`.

| Option type | Players | Clear call | Toss-up | Other |
|---|---|---|---|---|
| Club | 25 | 7 exercise, 4 decline | 14 | |
| Mutual | 25 | 7 declined (3 where the club would keep the player, 4 where the player would take it) | 16 | 2 (Chapman guaranteed, Sanchez terms not listed) |
| Player | 3 | 1 exercise | 2 | |
| Opt-out | 8 | 5 stay, 0 opt out | 3 | |

The clearest calls are the club exercising Ronald Acuña Jr.'s option (net cost $7.0 million against a projected $20.8 million a year), the club declining Sandy Alcantara's and Luis Robert Jr.'s options, and Luis Severino exercising his $22 million player option against a projected $14.1 million. The share of toss-ups depends on the margin: 25 of 61 at $2.5 million, 36 at $4 million (35 after Chapman's option, which is guaranteed, is set aside), and 47 at $6 million. No player is called to opt out. This is largely because the model underpredicts stars, so the opt-out calls mean "the model sees no reason to leave".

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
- **Benchmark scope:** The comparison to MLB Trade Rumors covers only players in their top 50 with an MLB track record and a market contract of at least $5 million, which is the top of the market where the model is weakest. Some model design choices (a year trend, removing qualifying-offer acceptances) were made while looking at the same 2024-2026 results used for the comparison, so the reported accuracy is probably optimistic.
- **Gaps in the source contract table:** The Spotrac tables are not complete. An audit found 21 rows with no contract value (5 in 2023, 15 in 2024, 1 in 2026, none in the other nine classes), which were removed as minor league or non-guaranteed deals. At least one of them was a real major league contract listed at $0 in the source (Jason Heyward, 2024, one year and $9 million), and a player on MLB Trade Rumors' 2024 list (Brandon Belt) does not appear in the 2024 table at all. The effect on the model is likely small, since the affected classes are mostly test years, but it has not been quantified.
- **Guaranteed years only:** Contract length comes from the source table's guaranteed years and does not capture opt-outs, club or player options, or deferred money, so a four-year deal with opt-outs counts as four years. Total value is predicted AAV times predicted years, so errors in both compound, especially for the largest contracts.
- **Option calls:** Calls compare a one-year option salary with a projected AAV for multi-year deals, so they are approximate, and more than half of the options are toss-ups at the model's own error margin. Option terms come from MLB Trade Rumors' list and may change: Nick Pivetta's option type needs verification, Gary Sanchez's terms are not listed, and Aroldis Chapman's option is treated as guaranteed because its innings condition was met. Real decisions also weigh health, payroll, and roster fit, which the model cannot see.

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
| 2026-10-21 | Benchmarked out-of-sample AAV predictions against MLBTR's Top 50 predictions for 2024-2026 (120 players scored): pooled MAE $3.15M for MLBTR vs $4.13M for the model; MLBTR closer in every class; both underpredict recent classes and the model's bias grew from -$1.71M to -$3.48M | The model is behind the expert benchmark, mostly at the top of the market; contract length is not modeled, which likely contributes in recent classes when deals got shorter; the model's design choices were made while looking at the same test years, so true out-of-sample performance is probably no better than shown |
| 2026-10-21 | Broke the MLBTR benchmark down by contract size: model and MLBTR within about $0.3M MAE below $20M AAV, but $8.16M vs $5.02M MAE for the 30 contracts of $20M or more (about 80% of the model's extra error). Of 30 unscored MLBTR players: 13 international or Ohtani, 6 qualifying-offer acceptances, 8 under $5M, 2 missing from the source table (Heyward, listed at $0; Belt, absent), 1 name-spelling mismatch (Jakob vs. Jake Junis) | The model is competitive for most of the market and weakest for stars; the unscored players are mostly expected exclusions, and an audit of the source table found a few real contracts missing |
| 2026-10-21 | Audited the $0-value rows removed during cleaning: 21 across 12 classes (5 in 2023, 15 in 2024, 1 in 2026, none elsewhere); confirmed Jason Heyward's 2024 deal ($9M, one year) was among them; kept the rule and documented the gap instead of rebuilding the pipeline | The affected rows are few and mostly in test years; rebuilding for one confirmed contract would not change the results materially, but a corrections file will be added if more real $5M+ deals are found |
| 2026-10-21 | Examined contract length in the $5M+ training contracts (756): 40% one-year, 33% two-year, about 86% three years or fewer; average length falls with age (4.5 years under 28 to 1.3 at 36+) and rises with size (1.6 years under $10M AAV, 5.1 at $20M+); share of one-year deals rose from about 27% in 2015-16 to 47-54% in 2024-26 | Length is skewed and tied to AAV, so a straight-line model will miss long deals; plan to predict years from the same inputs as AAV, evaluate against MLBTR's years and total-value errors on the same players, and derive total value as predicted AAV times predicted years |
| 2026-10-22 | Modeled contract length with the same inputs as AAV and evaluated on rolling 2021-2026 classes (433 contracts): MAE 0.81 years vs 1.03 for a flat two-year guess, but within one year of actual only 71% of the time vs 87%; large contracts compressed (3.70 predicted vs 4.55 actual years for $20M+ deals); $20M+ deals averaged about 4.0 years in 2024-2026 vs about 5.3 in 2015-2023; against MLBTR on 120 players the model ties on years for $20M+ deals (1.7 vs 1.7) but trails on total value ($24.8M vs $19.9M MAE) | Length improves on a naive guess mainly for large contracts; total value compounds AAV and length errors, so star totals are lower bounds |
| 2026-10-25 | Generated 2027 contract length and total value projections (fa_2027_contract_projections.csv): final length model trained on all classes, predicted years rounded to whole years with a range of plus or minus one, total value = AAV x years. Verified that $20M+ deals averaged 5.34 years in 2015-2023 (58 deals) vs 3.97 in 2024-2026 (35). Predicted lengths: 156 one-year, 81 two-year, 15 three-year, 1 five-year | The model reproduces the common short deals but not the long tail of star contracts; top reliever projections ($44M-$49M over three years) are in line with 2026 relievers such as Robert Suarez (3 years, $45MM) and Devin Williams (3 years, $51MM) |
| 2026-10-25 | Parsed option and opt-out terms for the 2027 class from MLBTR's notes (fa_2027_options.csv): 62 players with predictions (25 club options, 25 mutual, 4 player, 8 opt-outs); checked about 17 rows against the source text; 3 flagged for manual review (Chapman: guaranteed once innings condition met; Freeland: vests only with 170 innings in 2026; Sanchez: no terms listed) and 1 type conflict to verify (Pivetta: club option in the current file, player option in an April copy of the list) | Option calls depend on correct terms; the parser was spot-checked against the source and conflicts are flagged instead of guessed |
| 2026-10-25 | Decided to keep model outputs mechanical and handle outliers separately: Tarik Skubal's model projection ($32.2M AAV) is labeled a lower bound and will be shown next to a reference range from precedent contracts in the data and MLBTR's own published prediction; a calibration correction for star players will be tested on out-of-sample years before being applied to anyone | A hand-edited number for one player would mean applying a different standard to him than to everyone else; no past contract resembles what he is expected to receive|
| 2026-10-25 | Looked up precedent for Tarik Skubal's projection in the contracts data: closest comparable by age and weighted WAR is Gerrit Cole (2020, 9 years, $324M); top pitcher AAVs excluding Ohtani are $34M-$43.3M; Skubal's model AAV ($32.2M) sits below most of them and the model's 5-year length is below the 7-9 years of the longest deals for pitchers in their early thirties | Shows how far below precedent the model's output is without editing it; reference figures are nominal and labeled as non-model |
| 2026-10-25 | Generated option and opt-out calls for 61 players (fa_2027_option_calls.csv): 35 of 61 are toss-ups at a $4M margin (25 at $2.5M, 47 at $6M); clearest calls are Acuña (club exercises), Alcantara and Robert (club declines), Severino (player exercises); no player is called to opt out; fixed the mutual-option label for options with no buyout | The margin reflects the model's uncertainty, so a large share of toss-ups is a result in itself; opt-out calls lean toward "stays" because the model underpredicts stars |

## Appendix B: Data Dictionary

| Field | Description | Source |
|---|---|---|
| [field] | [description] | [source] |
