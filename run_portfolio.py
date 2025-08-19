# file: run_portfolio.py
import numpy as np, matplotlib.pyplot as plt
from portfolio_model import make_portfolio_model

T = 60  # months
base = make_portfolio_model()
grow = make_portfolio_model(monthly_disbursements=350_000.0, prepay_rate=0.003)
stress = make_portfolio_model(annual_rate=0.07, prepay_rate=0.015, chargeoff_rate=0.004)

S_base = base.run(T)['principal']
S_grow = grow.run(T)['principal']
S_stress = stress.run(T)['principal']

plt.figure()
plt.plot(S_base, label='Base')
plt.plot(S_grow, label='Growth (higher disb.)')
plt.plot(S_stress, label='Stress (higher rate/prepay/CO)')
plt.title('Loan Portfolio Principal (Monthly)')
plt.xlabel('Month'); plt.ylabel('NOK')
plt.legend(); plt.show()
