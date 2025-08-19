# file: applications_model.py
import numpy as np
from sd_core import Stock, Flow, Model

def make_applications_model(
    initial_backlog=0,
    inflow_low=30, inflow_high=60,
    base_capacity=45,
    variability=0,        # e.g., 0.2 for ±20% day-to-day capacity noise
    priority_spillover=False,
    rejection_rate=0.5,   # share (0..1) of new daily applications immediately rejected
    horizon=365           # NEW: preallocate caches to this many days
):
    rng = np.random.default_rng(42)

    def inflow_raw(t, series, params):
        low, high = params['inflow_low'], params['inflow_high']
        return rng.integers(low, high+1)  # uniform integer daily arrivals

    def inflow_fn(t, series, params):
        total = inflow_raw(t, series, params)
        rate = params['rejection_rate']
        rejected = int(round(total * rate))
        accepted = total - rejected
        # Cache for analytics
        params['todays_arrivals'][t]     = total
        params['todays_rejected'][t]     = rejected
        params['todays_accepted'][t]     = accepted
        params['todays_inflow_cache'][t] = accepted
        return accepted

    def outflow_fn(t, series, params):
        backlog = series['backlog'][t]
        base = params['base_capacity']
        var = params['variability']
        capacity_today = base if var == 0 else base * (1 + rng.uniform(-var, var))
        if priority_spillover:
            processed = min(backlog + params['todays_inflow_cache'][t], capacity_today)
        else:
            processed = min(backlog, capacity_today)
        return processed

    stocks   = {'backlog': Stock('backlog', initial_backlog)}
    flows_in  = {'backlog': Flow('applications_accepted', inflow_fn)}
    flows_out = {'backlog': Flow('applications_processed', outflow_fn)}

    params = dict(
        inflow_low=inflow_low, inflow_high=inflow_high,
        base_capacity=base_capacity, variability=variability,
        rejection_rate=rejection_rate,
        todays_inflow_cache=np.zeros(horizon),
        todays_arrivals=np.zeros(horizon, dtype=int),
        todays_accepted=np.zeros(horizon, dtype=int),
        todays_rejected=np.zeros(horizon, dtype=int)
    )
    return Model(stocks, flows_in, flows_out, params)
