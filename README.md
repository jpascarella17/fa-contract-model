# MLB Free Agent Contract Projections

Projecting what MLB free agents will sign for (average annual value, contract length, and total value) from performance and age, then applying the models to the 2027 free agent class.

**Status:** work in progress. The 2027 projections are preliminary as of October 25, 2026, and will be refreshed after the World Series, when qualifying offers and option decisions are known.

The full process, with every decision logged, is in [methodology.md](methodology.md).

## What it does

1. Builds a table of 1,600 free agent contracts from the 2015 to 2026 classes (Spotrac), with each player's prior three seasons of Baseball Reference WAR, age at signing, position, and qualifying offer status.
2. Fits ridge regression models that predict AAV and contract length separately for hitters and pitchers. Total value is predicted AAV times predicted years.
3. Adds Baseball Savant percentile ranks (expected and actual contact quality, plate discipline, sprint speed for hitters; xERA, fastball velocity, strikeout, walk, whiff, and chase rates for pitchers) and tests whether they improve on WAR, age, and position alone.
4. Grades every model on classes it never trained on, and compares it to MLB Trade Rumors' published Top 50 predictions.
5. Projects 253 of the 257 players on MLB Trade Rumors' projected 2026-27 free agent list, and makes exercise or decline calls on the 61 players with contract options or opt-outs.

## Results

| Question | Result |
|---|---|
| Does the baseline beat a naive guess? | Yes. On the 2024-2026 test classes, average AAV miss was $3.53M against $5.62M for guessing the median contract (all contracts). |
| Do Savant percentiles help? | A little. In a rolling check (train on all earlier classes, test each year 2021-2026), pitcher error fell from $3.46M to $3.28M and Savant was better in all six years. Hitter error fell from $3.93M to $3.67M, but Savant was better in only three of six years, all recent. |
| How does it compare with experts? | It is behind. On 120 players in MLB Trade Rumors' Top 50 for the 2024-2026 classes, their average AAV miss was $3.15M and the model's was $4.13M. The gap is concentrated in contracts of $20M a year or more ($8.16M vs $5.02M); below that the two are within about $0.3M. |
| Can it predict contract length? | Partly. Average miss of 0.81 years against 1.03 for a flat two-year guess, but long deals for stars are compressed. Total value is further behind MLB Trade Rumors ($24.8M vs $19.9M average miss). |

The main weakness is the top of the market. The models underpredict stars (about $6M a year for hitters above 3.5 weighted WAR), so projected totals for the highest-value players should be read as lower bounds. Tarik Skubal is flagged as an outlier and shown next to precedent contracts instead of being adjusted.

## Outputs

- `outputs/fa_2027_contract_projections.csv`: projected AAV, years, total value, and notes for each player
- `outputs/fa_2027_option_calls.csv`: option and opt-out calls with the reasoning for each
- `outputs/benchmark_mlbtr_vs_model.csv`: the player-by-player comparison with MLB Trade Rumors

## Repository layout

```
data/processed/   cleaned contracts, season stats, Savant data, 2027 free agent list
notebooks/        01_contracts_check.ipynb, 02_pull_stats.ipynb
src/              clean_contracts.py (cleans one Spotrac class table)
outputs/          projections, option calls, benchmark
methodology.md    full write-up and process log
```

## Data and how it was built

- **Contracts:** Spotrac free agent tables for each class, copied into spreadsheets by hand and saved as CSV, then cleaned by `src/clean_contracts.py`. Rows with no contract value were dropped; 18 one-year qualifying offer acceptances were removed because their salaries are set by formula.
- **Performance:** Baseball Reference WAR and Baseball Savant percentile ranks through the `pybaseball` library; birth dates from the MLB Stats API.
- **2027 class and benchmark:** MLB Trade Rumors' projected 2026-27 free agent list and its annual Top 50 predictions, saved by hand. The raw article text is not included in this repository.

## Limitations

- Only players who reached free agency appear in the data, and the top of the market has few examples.
- The model sees recent statistics, not injuries, postseason performance, team payroll, or what an agent is asking. For example, it cannot explain Walker Buehler's 2025 contract.
- Contract length counts guaranteed years only, so opt-outs and options are not reflected.
- The source contract tables are not complete: an audit found real contracts listed at $0 or missing (for example Jason Heyward's 2024 deal).
- The model's design choices were made while looking at the same 2024-2026 results used for grading, so the reported accuracy is probably optimistic.
- The collective bargaining agreement expires after the 2026 season, which could change the 2027 market in ways past data cannot show.

## Setup

```bash
git clone https://github.com/jpascarella17/fa-contract-model.git
cd fa-contract-model
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

The processed data files are included, so the notebooks can be read and the models re-run without repeating the manual data collection.

## Credits

Spotrac, Baseball Reference, Baseball Savant, the MLB Stats API, MLB Trade Rumors, and the `pybaseball` library.
