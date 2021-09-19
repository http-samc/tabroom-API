# The OTR Score
[tournaments.tech](http://tournaments.tech) uses a metric of ranking debaters, developed by Adithya Vaidyanathan, known as the OTR Score. It awards points based on tournament attendance, high performance (including deep elimination round runs), and success against difficult opponents. Every system has its flaws, but the OTR Score is currently the only scaled metric on the national circuit.

## Calculations
Here are several components that go into determining the compensation for any given tournament.
| Term | Description |
| --- | --- |
| `breakBoost` | an integer that starts at 0 and increases by 1 for every elimination round debated; max is the total number of break rounds. designed to benefit teams who do well in outrounds. | 
| `tournamentBoost` | an integer ranging from 1 to 2 that corresponds to the tournament of difficulty. initially, this is calculated by the bid level of the tournament. at the end of the season, it is recalculated based off the number of bids in the competitor pool. designed to benefit teams who do harder tournaments. |
| `OPwpm` | a decimal ranging from 0 to the total number of prelim rounds. represents the average amount of wins of your prelim opponents. recalculated by the API (tab's values are inconsistently published). designed to benefit teams who performed against dificult opponents in prelims. |
| `OTR Tournament Comp` | the total compensation recieved from a tournament that goes towards your overall OTR Score. |

With these components being defined, we can express our tournament compensation as:<br><br>
`OTR Tournament Comp` ${=}$ $\frac{numPrelimWins}{numPrelims}$ ${*}$ ${OPwpm}$ ${*}$ ${tournamentBoost}$ ${*}$ ${breakBoost}$ <br><br>
And, our overall OTR Score as:<br><br>
`OTR Score` ${=}$ $\sum$ `OTR Tournament Comp` ÷ 20<br><br>

## Notes
- Even though we collect and process speaker points with IQR, we've decided to leave these out of our rankings due to the systemic inequalities and general inconsistencies surrounding the manner in which judges award speaks. 
- Due to the sheer amount of tournaments co-championing, we don't award the champion (1st place) and finalist (2nd place) different boost factors. If we gave them both the champion factor, that would be unfair to teams who had to win finals to get the boost. If we gave them the finalist factor, that would be unfair to one of them that would've won the matchup and gotten the champion factor. So, `breakBoost` was designed to even out at the final round.
- We divide the sum of the `OTR Tournament Comp`s by 20 in order to keep the numbers manageable when calculating `OTR Score`s.
- Any algorithmic/methodological queries about the OTR score can be directed to the creator of the metric, [Adithya Vaidyanathan](mailto:adithya679@gmail.com).
- Any implementation/frontend/backend/api/programatic/quality-of-life queries can be directed to the developer of the [Tabroom API](https://github.com/http-samc/tabroom-api) and [tournaments.tech](http://tournaments.tech), [Samarth Chitgopekar](mailto:sam@chitgopekar.tech)