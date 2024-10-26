from decimal import Decimal
from typing import List, Tuple, Union
from dojo.actions.uniswapV3 import UniswapV3Trade
from dojo.policies import BasePolicy
from dojo.observations.uniswapV3 import UniswapV3Observation

class ArbitragePolicy(BasePolicy):  # type: ignore
    def __init__(self, agent):
        super().__init__(agent=agent)
        self.block_last_trade: int = -1
        self.min_block_dist: int = 20
        self.min_signal: float = 1.901
        self.tradeback_via_pool: Union[str, None] = None

    def compute_signal(self, obs: UniswapV3Observation) -> Tuple[Decimal, Decimal]:
        pools = obs.pools
        pool_tokens_0 = obs.pool_tokens(pool=pools[0])
        pool_tokens_1 = obs.pool_tokens(pool=pools[1])

        if pool_tokens_0 != pool_tokens_1:
            print("Pools do not match for arbitrage.")
            return Decimal(0), Decimal(0)

        price_0 = obs.price(token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[0])
        price_1 = obs.price(token=pool_tokens_0[0], unit=pool_tokens_0[1], pool=pools[1])
        ratio = price_0 / price_1
        print(f"Observed prices: Pool 0 - {price_0}, Pool 1 - {price_1}, Ratio - {ratio}")

        signals = (
            ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
            1 / ratio * (1 - obs.pool_fee(pools[0])) * (1 - obs.pool_fee(pools[1])),
        )

        print(f"Calculated signals: {signals}")
        return signals

    def predict(self, obs: UniswapV3Observation) -> List[UniswapV3Trade]:  # type: ignore
        pools = obs.pools
        pool_tokens_0 = obs.pool_tokens(pool=pools[0])
        pool_tokens_1 = obs.pool_tokens(pool=pools[1])

        if pool_tokens_0 != pool_tokens_1:
            print("Pools do not match, no arbitrage opportunity.")
            return []

        amount_0 = self.agent.quantity(pool_tokens_0[0])
        amount_1 = self.agent.quantity(pool_tokens_0[1])
        print(f"Agent quantities: {pool_tokens_0[0]} - {amount_0}, {pool_tokens_0[1]} - {amount_1}")

        if self.tradeback_via_pool is not None:
            action = UniswapV3Trade(
                agent=self.agent,
                pool=self.tradeback_via_pool,
                quantities=(Decimal(0), amount_1),
            )
            print(f"Executing tradeback in pool {self.tradeback_via_pool}")
            self.tradeback_via_pool = None
            return [action]

        signals = self.compute_signal(obs)
        earnings = max(signals)
        index_pool_first = signals.index(max(signals))
        pool = obs.pools[index_pool_first]

        if earnings < self.min_signal or obs.block - self.block_last_trade < self.min_block_dist:
            print("No trade executed: Earnings below minimum or block distance too short.")
            return []

        print("Executing arbitrage trade!")
        self.tradeback_via_pool = obs.pools[0] if index_pool_first == 1 else obs.pools[1]
        self.block_last_trade = obs.block
        return [
            UniswapV3Trade(
                agent=self.agent,
                pool=pool,
                quantities=(amount_0, Decimal(0)),
            )
        ]
