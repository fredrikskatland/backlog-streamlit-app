# file: portfolio_model.py
import numpy as np
from sd_core import Stock, Flow, Model

def make_portfolio_model(
    initial_principal=1_000_000.0,
    monthly_disbursements=200_000.0,
    annual_rate=0.05,
    scheduled_amort_rate=0.02,   # 2% of principal/month (toy)
    prepay_rate=0.005,           # 0.5% per month
    chargeoff_rate=0.001         # 0.1% per month
):
    r_m = annual_rate/12.0

    def inflow_new_loans(t, series, params):
        return params['monthly_disbursements']

    def inflow_interest(t, series, params):
        return series['principal'][t] * params['r_m']

    def outflow_scheduled(t, series, params):
        return series['principal'][t] * params['scheduled_amort_rate']

    def outflow_prepay(t, series, params):
        return series['principal'][t] * params['prepay_rate']

    def outflow_chargeoff(t, series, params):
        return series['principal'][t] * params['chargeoff_rate']

    stocks = {'principal': Stock('principal', initial_principal)}
    flows_in = {'principal': Flow('new_loans', inflow_new_loans)}
    # if you want to track accounting balance with interest, add a separate 'balance' stock
    flows_in_interest = Flow('interest_accrual', inflow_interest)

    # combine multiple inflows by summing inside a wrapper
    def inflow_sum(t, series, params):
        return inflow_new_loans(t, series, params) + inflow_interest(t, series, params)

    flows_in = {'principal': Flow('inflow_total', inflow_sum)}
    def outflow_total(t, series, params):
        return (outflow_scheduled(t, series, params) +
                outflow_prepay(t, series, params) +
                outflow_chargeoff(t, series, params))

    flows_out = {'principal': Flow('outflow_total', outflow_total)}
    params = dict(
        monthly_disbursements=monthly_disbursements,
        r_m=r_m,
        scheduled_amort_rate=scheduled_amort_rate,
        prepay_rate=prepay_rate,
        chargeoff_rate=chargeoff_rate
    )
    return Model(stocks, flows_in, flows_out, params)
