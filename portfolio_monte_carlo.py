# Monte Carlo Portfolio Simulation
# Simulates different possible portfolio outcomes using random returns.
# Return and volatility can be typed in, or estimated from a real stock.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TRADING_DAYS = 252


def estimate_from_prices(prices):
    # Annualised return and volatility (in %) from daily closing prices
    daily = prices.pct_change().dropna()
    annual_return = daily.mean() * TRADING_DAYS * 100
    annual_volatility = daily.std() * np.sqrt(TRADING_DAYS) * 100
    return float(annual_return), float(annual_volatility)


def get_stock_estimates(ticker, history_years):
    # Download history from Yahoo Finance and estimate return and volatility
    import yfinance as yf

    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=history_years)

    data = yf.download(ticker, start=start, end=end,
                       auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError("No stock data found. Check the ticker.")

    # yfinance can sometimes return multi-level columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    prices = data["Close"].dropna()

    if len(prices) < 60:
        raise ValueError("Not enough price history for this ticker.")

    return estimate_from_prices(prices)


def run_simulation(initial_investment, annual_return, annual_volatility,
                   years, simulations):
    # Change percentages into decimals
    average_return = annual_return / 100
    volatility = annual_volatility / 100

    # One random return for every year of every simulation
    random_returns = np.random.normal(
        average_return, volatility, (years, simulations)
    )

    # Growth factor each year. A factor of 0 means the portfolio is wiped
    # out, and it stays at 0 afterwards (it can never go negative)
    growth = np.maximum(1 + random_returns, 0)

    results = initial_investment * np.cumprod(growth, axis=0)
    return results


def get_summary(results, initial_investment):
    final_values = results[-1]

    return {
        "Starting Investment": initial_investment,
        "Simulations": results.shape[1],
        "Worst Case (5%)": round(np.percentile(final_values, 5), 2),
        "10th Percentile": round(np.percentile(final_values, 10), 2),
        "Median": round(np.percentile(final_values, 50), 2),
        "90th Percentile": round(np.percentile(final_values, 90), 2),
        "Best Case (95%)": round(np.percentile(final_values, 95), 2),
        "Average": round(np.mean(final_values), 2),
        "Chance of Profit (%)": round(
            np.mean(final_values > initial_investment) * 100, 1
        ),
        "Chance of Loss (%)": round(
            np.mean(final_values < initial_investment) * 100, 1
        )
    }


def make_yearly_summary(results):
    rows = []

    for year in range(results.shape[0]):
        values = results[year]

        rows.append({
            "Year": year + 1,
            "10th Percentile": round(np.percentile(values, 10), 2),
            "25th Percentile": round(np.percentile(values, 25), 2),
            "Median": round(np.percentile(values, 50), 2),
            "75th Percentile": round(np.percentile(values, 75), 2),
            "90th Percentile": round(np.percentile(values, 90), 2),
            "Average": round(np.mean(values), 2)
        })

    return pd.DataFrame(rows)


def plot_paths(results, initial_investment):
    years = np.arange(1, results.shape[0] + 1)

    plt.figure(figsize=(11, 6))

    # Show up to 200 paths so the graph isn't too crowded
    for i in range(min(results.shape[1], 200)):
        plt.plot(years, results[:, i], alpha=0.08)

    plt.plot(
        years,
        np.percentile(results, 10, axis=1),
        linestyle="--",
        linewidth=2,
        label="10th percentile"
    )

    plt.plot(
        years,
        np.percentile(results, 50, axis=1),
        linewidth=2,
        label="Median"
    )

    plt.plot(
        years,
        np.percentile(results, 90, axis=1),
        linestyle="--",
        linewidth=2,
        label="90th percentile"
    )

    plt.axhline(
        initial_investment,
        linestyle=":",
        label="Starting investment"
    )

    plt.title("Monte Carlo Portfolio Simulation")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value (€)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("simulation_paths.png", dpi=150)
    plt.close()


def plot_distribution(results, initial_investment):
    final_values = results[-1]

    plt.figure(figsize=(10, 5))
    plt.hist(final_values, bins=40, edgecolor="black", alpha=0.75)

    median = np.median(final_values)

    plt.axvline(
        median,
        linestyle="--",
        linewidth=2,
        label=f"Median: €{median:,.0f}"
    )

    plt.axvline(
        initial_investment,
        linestyle=":",
        linewidth=2,
        label="Starting investment"
    )

    plt.title("Distribution of Final Portfolio Values")
    plt.xlabel("Final Portfolio Value (€)")
    plt.ylabel("Number of Simulations")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("final_distribution.png", dpi=150)
    plt.close()


def plot_percentiles(results, initial_investment):
    years = np.arange(1, results.shape[0] + 1)

    p10 = np.percentile(results, 10, axis=1)
    p25 = np.percentile(results, 25, axis=1)
    p50 = np.percentile(results, 50, axis=1)
    p75 = np.percentile(results, 75, axis=1)
    p90 = np.percentile(results, 90, axis=1)

    plt.figure(figsize=(11, 6))

    plt.fill_between(years, p10, p90, alpha=0.15,
                     label="10th - 90th percentile")

    plt.fill_between(years, p25, p75, alpha=0.25,
                     label="25th - 75th percentile")

    plt.plot(years, p50, linewidth=2, label="Median")

    plt.axhline(
        initial_investment,
        linestyle=":",
        label="Starting investment"
    )

    plt.title("Portfolio Outcomes Over Time")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value (€)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("percentile_bands.png", dpi=150)
    plt.close()


def main():
    print("Monte Carlo Portfolio Simulation")
    print("-" * 40)

    try:
        initial_investment = float(input("Initial investment (€): "))
        years = int(input("Investment period (years): "))
        simulations = int(input("Number of simulations: "))
    except ValueError:
        print("Please enter valid numbers.")
        return

    if initial_investment <= 0 or years <= 0 or simulations <= 0:
        print("Investment, years and simulations must all be above 0.")
        return

    use_stock = input(
        "Estimate return and volatility from a real stock? (y/n): "
    ).strip().lower()

    if use_stock == "y":
        ticker = input("Stock ticker (e.g. AAPL): ").upper().strip()

        try:
            history_years = int(input("Years of history to use (e.g. 10): "))
            if history_years <= 0:
                raise ValueError("History must be above 0 years.")

            print("\nDownloading data...")
            annual_return, volatility = get_stock_estimates(
                ticker, history_years
            )
        except Exception as error:
            print(f"Could not estimate from stock data: {error}")
            return

        print(f"Estimated annual return: {annual_return:.2f}%")
        print(f"Estimated annual volatility: {volatility:.2f}%")
    else:
        try:
            annual_return = float(input("Expected annual return (%): "))
            volatility = float(input("Annual volatility (%): "))
        except ValueError:
            print("Please enter valid numbers.")
            return

        if volatility < 0:
            print("Volatility cannot be negative.")
            return

    print("\nRunning simulation...")

    # Makes the results repeatable
    np.random.seed(42)

    results = run_simulation(
        initial_investment,
        annual_return,
        volatility,
        years,
        simulations
    )

    summary = get_summary(results, initial_investment)

    print("\nFinal Results")
    print("-" * 40)

    for name, value in summary.items():
        if isinstance(value, float):
            print(f"{name}: {value:,.2f}")
        else:
            print(f"{name}: {value}")

    # Save yearly results
    yearly_data = make_yearly_summary(results)
    yearly_data.to_csv("simulation_summary.csv", index=False)

    print("\nSummary saved to simulation_summary.csv")

    print("Creating charts...")
    plot_paths(results, initial_investment)
    plot_distribution(results, initial_investment)
    plot_percentiles(results, initial_investment)

    print("Charts saved: simulation_paths.png, "
          "final_distribution.png, percentile_bands.png")
    print("\nDone.")


if __name__ == "__main__":
    main()
