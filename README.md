# OTR Score Calculation
($\sum_{}^{} tournamentComp$)  ÷ $(numTournaments * 10)$**, where a tournamentComp is:**

$\frac{OPwpm * numPrelimWins}{numPrelims}$ * ${breakBoost}$ * ${tournamentBoost}$ <br><br>
- **OPwpm** is independently recalculated as a *percentage value* (not all tournaments offer it) **with the following formula:**<br>
$\sum_{}^{} opponentWinCount$ ÷ (numPrelims * numOpponnents)<br>
*"The number of wins all of your opponents got divided by the amount of rounds they participated in"* <br><br>
- **breakBoost** is the largest factor that can affect a tournamentComp - it awards teams for advancing past the preliminary rounds. It *ranges from 1 to 2* (inclusive) and is determined by the following formula: <br>
    $1 + (roundPrestige ÷ numBreakRounds)$, **where roundPrestige is:**<br><br>
    - an integer value that starts at 1 for the very first breakround and enumerates by 1 for every additional breakround debated
    - a team's roundPrestige factor is the roundPrestige of the last round they debated
    - the first breakround will always have a `roundPrestige of 1`
    - the last round (finals) will always have a roundPrestige equaling the total number of breakRounds
    - there is **no** recognized difference between championing (winning finals) and being a finalist (2nd place)
    - preliminary rounds have a `roundPrestige of 0` (breakBoost becomes 1 + (0/numBreakRounds) = 1 [no boost given due to multiplying by 1])<br><br>
- **tournamentBoost** is a factor which *ranges from 1 to 2* (inclusive) that applies to *all entries* in a tournament that is determined by the difficulty of the tournament itself.
  - a tournament like the Glenbrooks, Harvard, Stanford, etc. (the most difficult ones) will get a score of 2
  - a tournament like Mount Vernon or SF Roosevelt (less difficult tournaments) will get a score of 1
  - we generally make this distinction using the University of Kentuck's bid level distinctions *for the gold level*:
    - Octafinals bid = `tournamentBoost of 2`
    - Quarterfinals bid = `tournamentBoost of 1.65`
    - Semifinals bid = `tournamentBoost of 1.35`
    - Finals bid = `tournamentBoost of 1`
  - even though these boosters are based off the amount of bids awarded, the score still applies to all competitors (including those who do not break) because it gauges the overall tournament difficulty
  - some tournaments are moved between these distinctions due to selective admittance of top teams or just an abnormally difficult competitor pool
    - you can see a tournament's specific boost factor in it's key under `tournament-info.json`