import datetime
from dojo import Backtester, Portfolio, TradingSession
from dojo.observations.uniswapV3 import UniswapV3Observation
from dojo.agents import BaseAgent
from arbitrage_policy import ArbitragePolicy  # Assuming ArbitragePolicy is in arbitrage_policy.py

# Set up initial portfolio based on competition guidelines
initial_portfolio = Portfolio({
    'WETH': 25,
    'WBTC': 1,
    'USDC': 50_000,
    'PEPE': 1_000_000_000
})

# Define time range for the backtest
start_date = datetime.datetime(2024, 6, 20)
end_date = datetime.datetime(2024, 9, 3)

# Create a trading session for the backtesting period
trading_session = TradingSession(start_date=start_date, end_date=end_date)

# Instantiate a BaseAgent with the initial portfolio
agent = BaseAgent(portfolio=initial_portfolio)

# Initialize the ArbitragePolicy with the agent
policy = ArbitragePolicy(agent=agent)

# Set up the backtester with the trading session, agent, and policy
backtester = Backtester(session=trading_session, portfolio=initial_portfolio)
backtester.add_policy(policy)

# Run the backtest
print("Starting backtest...")
backtester.run()
backtester.report_results()  # Outputs results after the backtest is complete
