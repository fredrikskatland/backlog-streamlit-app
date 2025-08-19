# file: queue_simpy.py
import simpy
import numpy as np

class ApplicationQueueSim:
    def __init__(self, arrivals_per_day=(30,60), mean_service_minutes=60, reviewers=10, minutes_per_day=8*60, seed=1):
        self.arrivals_per_day = arrivals_per_day
        self.service_time = mean_service_minutes
        self.reviewers = reviewers
        self.day_minutes = minutes_per_day
        self.rng = np.random.default_rng(seed)

    def run(self, days=60):
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=self.reviewers)
        backlog_sizes = []

        def applicant(name):
            with server.request() as req:
                yield req
                service = self.rng.exponential(self.service_time)  # exponential service time
                yield env.timeout(service)

        def daily_arrivals():
            for d in range(days):
                n = self.rng.integers(self.arrivals_per_day[0], self.arrivals_per_day[1]+1)
                for i in range(n):
                    env.process(applicant(f"d{d}-a{i}"))
                # snapshot backlog: queued + in service
                backlog_sizes.append(len(server.queue) + (server.count))
                yield env.timeout(self.day_minutes)

        env.process(daily_arrivals())
        env.run()
        return backlog_sizes
