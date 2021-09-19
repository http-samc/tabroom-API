# The OTR Score
[tournaments.tech](http://tournaments.tech) uses a metric of ranking debaters, developed by Adithya Vaidyanathan, known as the OTR Score. It awards points based on tournament attendance, high performance (including deep elimination round runs), and success against difficult opponents. Every system has its flaws, but the OTR Score is currently the only scaled metric on the national circuit.

## Considered Factors
Here are several components that go into determining the compensation for any given tournament.
| Term | Description |
| --- | --- |
| `breakBoost` | an integer that starts at 0 and increases by 1 for every elimination round debated; max is the total number of break rounds. designed to benefit teams who do well in outrounds. | 
| `tournamentBoost` | an integer ranging from 1 to 2 that corresponds to the tournament of difficulty. initially, this is calculated by the bid level of the tournament. at the end of the season, it is recalculated based off the number of bids in the competitor pool. designed to benefit teams who do harder tournaments. |
| `OPwpm` | a decimal ranging from 0 to the total number of prelim rounds. represents the average amount of wins of your prelim opponents. recalculated by the API (tab's values are inconsistently published). designed to benefit teams who performed against dificult opponents in prelims. |
| `numPrelimWins` | the total number of prelim rounds won, byes included. designed to benefit teams who perform well in prelims. |
| `numPrelims` | the total number of prelim rounds in the division. used to contextualize numPrelimWins. |
| `OTR Tournament Comp` | the total compensation recieved from a tournament that goes towards your overall OTR Score. |
| `OTR Score` | the final composite score used to rank debaters. directly proportional to OTR Tournament Comp's. |

## Calculation
With these components being defined, we can express our tournament compensation as:<br><br>
![OTR Comp = (numPrelimWins)/(numPrelims) * OPwpm * tournamentBoost * breakBoost](https://render.githubusercontent.com/render/math?math=OTR_{comp}=\frac{numPrelimWins}{numPrelims}\cdot{OPwpm}\cdot{tournamentBoost}\cdot{breakBoost}) 

And, our overall OTR Score as:<br><br>
![OTR Score = (Sum of OTR Comp's)/(20)](https://render.githubusercontent.com/render/math?math=OTR_{score}=\frac{\sum{OTR_{comp}}}{20}) 

## Retroactive Difficulty Normalization Procedure
Because tournament difficulties vary from year to year, we determine the tournamentBoost factor as a function of the bid level of the tournament at the beginning of the year (finals = 1, semifinals = 1.25, quarterfinals = 1.55, octafinals = 2). Then, at the end of the year (definied as the day Gold TOC and Silver TOC are finished) we first scrape both TOC divisions and then we use a generated bid list to determine the true difficulty of the tournament. By determining the number of bids in the competitor pool retroactively (silver bid = 0.5, gold bid = 1), we can get a more accurate sense of the level of competition faced at each tournament. We standardize it so that the tournaments with the lowest amount of bids in the pool get a score of 1 and Gold TOC gets a score of 2. Then, we apply these new tournamentBoost factors to our whole dataset, which will update our leaderboard with the final rankings. We leave these rankings up until the start of the next season (we use the end of the UK Season Opener as our metric for this), and then we archive the data in the releases tab of our github repository.

## Notes
- Even though we collect and process speaker points with IQR, we've decided to leave these out of our rankings due to the systemic inequalities and general inconsistencies surrounding the manner in which judges award speaks. 
- Due to the sheer amount of tournaments co-championing, we don't award the champion (1st place) and finalist (2nd place) different boost factors. If we gave them both the champion factor, that would be unfair to teams who had to win finals to get the boost. If we gave them the finalist factor, that would be unfair to one of them that would've won the matchup and gotten the champion factor. So, `breakBoost` was designed to even out at the final round.
- We divide the sum of the `OTR Tournament Comp`s by 20 in order to keep the numbers manageable when calculating `OTR Score`s.
- Any algorithmic/methodological queries about the OTR score can be directed to the creator of the metric, [Adithya Vaidyanathan](mailto:adithya679@gmail.com).
- Any implementation/frontend/backend/api/programatic/quality-of-life queries can be directed to the developer of the [Tabroom API](https://github.com/http-samc/tabroom-api) and [tournaments.tech](http://tournaments.tech), [Samarth Chitgopekar](mailto:sam@chitgopekar.tech)