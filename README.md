# Monte Carlo Portfolio Simulation

A Python tool that simulates thousands of possible futures for an investment, so you can see the range of outcomes instead of a single number.

You give it a starting amount, a time period, an expected yearly return and a yearly volatility. It runs thousands of random scenarios and reports how the portfolio could end up. Instead of typing the return and volatility, you can let it estimate them from a real stock's price history.

## How it works

1. For every simulation and every year, it draws a random return from a normal distribution with your chosen average return and volatility.
2. It grows the portfolio by that return each year. A portfolio can fall to zero but never below it.
3. After all the simulations, it works out the percentiles of the final values, the average, and the chance of making or losing money.

If you choose the stock option, it downloads daily prices from Yahoo Finance and turns them into an annual return (average daily return times 252) and an annual volatility (standard deviation of daily returns times the square root of 252).

## How to run

Install the libraries:

```
pip install yfinance pandas numpy matplotlib
```

Run the script:

```
python portfolio_monte_carlo.py
```

It asks for the starting investment, the number of years and the number of simulations. Then it asks whether to estimate return and volatility from a real stock. Answer `y` and give a ticker and a number of years of history, or answer `n` and type the return and volatility yourself.

The random seed is fixed at 42, so the same inputs always give the same results.

## Example run

Inputs: 1,000 euros, 12 years, 10,000 simulations, return and volatility estimated from AAPL over the last 10 years (29.82% return, 29.14% volatility).

| Result | Value (euros) |
| --- | --- |
| 5th percentile | 3,952 |
| 10th percentile | 5,558 |
| Median | 17,102 |
| 90th percentile | 47,550 |
| 95th percentile | 61,198 |
| Average | 23,091 |
| Chance of profit | 99.8% |
| Chance of loss | 0.2% |

The median is lower than the average because a few very good runs pull the average up. This is why the distribution below has a long tail on the right.

## Output files

The script saves these in the folder it is run from:

- `simulation_summary.csv`: percentiles and average for every year
- `simulation_paths.png`: 200 sample paths with the 10th, 50th and 90th percentile lines
- `final_distribution.png`: histogram of the final portfolio values
- `percentile_bands.png`: how the range of outcomes widens over time

![Simulation paths](simulation_paths.png)

![Distribution of final values](final_distribution.png)

![Percentile bands](percentile_bands.png)

## Limitations

- The example uses Apple's last 10 years, which were unusually strong, and assumes that return continues for 12 more years. That is why the chance of loss is so low. A broad index or a more modest return gives a much wider spread.
- Returns are assumed to follow a normal distribution with the same average and volatility every year. Real markets have more extreme crashes and gains than this.
- It does not include fees, taxes, inflation or regular deposits.
- Returns are simulated once per year, not day by day.
- The results are estimates from a model, not predictions.

## Libraries

Python, NumPy, pandas, matplotlib and yfinance (only needed for the stock option).
