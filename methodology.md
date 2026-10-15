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

[Report baseline results here.]

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

- **Split:** Train on classes [2015 to 2023]. Test on [2024 and 2025]. No future data is used in any training step.
- **Metrics:** MAE and RMSE for AAV and total value; interval coverage.
- **External benchmark:** MLB Trade Rumors' predicted contracts for the same classes.
- **Dollar adjustment:** [Describe how contract values were adjusted for market inflation across years.]

## 7. Results

### 7.1 Model comparison
[Table: model, MAE, RMSE for AAV and total value.]

### 7.2 Does underlying data help?
[Compare baseline versus baseline plus Statcast/pitch-shape features. This is the core finding. Include a feature importance or SHAP plot.]

### 7.3 Benchmark against public predictions
[Compare to MLB Trade Rumors. Be honest about where the model is better, worse, or about equal.]

### 7.4 Largest misses
[Examine the biggest errors. What did the model not know? Injuries, team context, a surprise team, a unique skill set?]

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
- **Outliers:** [Describe how players like Ohtani were handled.]
- **Market change:** Spending patterns shift over time, and the model may lag a changing market.

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

Keep a dated running log of decisions. This is what shows a reader how you think.

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

## Appendix B: Data Dictionary

| Field | Description | Source |
|---|---|---|
| [field] | [description] | [source] |
