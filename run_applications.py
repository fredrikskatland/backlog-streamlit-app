# file: run_applications.py
import numpy as np, matplotlib.pyplot as plt
from applications_model import make_applications_model

T = 180  # days
m = make_applications_model(
    initial_backlog=25,
    inflow_low=30, inflow_high=60,
    base_capacity=25, variability=0.15,
    rejection_rate=0.40  # default 50%
)

series = m.run(T)
backlog = series['backlog']
arrivals = m.params['todays_arrivals'][:T]
accepted = m.params['todays_accepted'][:T]
rejected = m.params['todays_rejected'][:T]

# Plot backlog
plt.figure()
plt.plot(backlog, label='Backlog (applications)')
plt.title('Unhandled Applications Backlog')
plt.xlabel('Day'); plt.ylabel('Applications')
plt.legend()
plt.show()

# Plot arrivals split (optional)
plt.figure()
plt.plot(arrivals, label='Arrivals (total)')
plt.plot(accepted, label='Accepted')
plt.plot(rejected, label='Rejected')
plt.title('Daily Arrivals Split')
plt.xlabel('Day'); plt.ylabel('Applications')
plt.legend()
plt.show()

print(f"Avg daily arrivals:  {arrivals.mean():.1f}")
print(f"Avg accepted/day:    {accepted.mean():.1f}")
print(f"Avg rejected/day:    {rejected.mean():.1f}")
print(f"Max backlog:         {backlog.max():.0f}")
