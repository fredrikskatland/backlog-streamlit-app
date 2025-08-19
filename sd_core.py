# file: sd_core.py
from dataclasses import dataclass, field
from typing import Callable, Dict
import numpy as np

@dataclass
class Stock:
    name: str
    initial: float

@dataclass
class Flow:
    name: str
    fn: Callable[[int, Dict[str, np.ndarray], Dict], float]  # fn(t, series, params)-> value

@dataclass
class Model:
    stocks: Dict[str, Stock]
    flows_in: Dict[str, Flow]        # flows that add to stock, keyed by stock name
    flows_out: Dict[str, Flow]       # flows that remove from stock, keyed by stock name
    params: Dict                     # arbitrary parameters

    def run(self, T: int) -> Dict[str, np.ndarray]:
        series = {s: np.zeros(T, dtype=float) for s in self.stocks}
        # set initial values
        for s, st in self.stocks.items():
            series[s][0] = st.initial

        for t in range(T-1):
            # compute flows at t
            add = {s: self.flows_in[s].fn(t, series, self.params) if s in self.flows_in else 0.0 
                   for s in self.stocks}
            rem = {s: self.flows_out[s].fn(t, series, self.params) if s in self.flows_out else 0.0 
                   for s in self.stocks}
            # update stocks with non-negativity safeguard
            for s in self.stocks:
                net = series[s][t] + add[s] - rem[s]
                series[s][t+1] = max(net, 0.0)
        return series
