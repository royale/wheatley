from typing import Optional

import numpy as np

from instances.generate_taillard import generate_taillard

from .rcpsp import Rcpsp


class TaillardRcpsp(Rcpsp):
    """Instantiate a randomly generated taillard instance and modelise the instance
    as a RCPSP problem.
    """

    def __init__(
        self,
        pb_id: int,
        n_jssp_jobs: int,
        n_jssp_machines: int,
        seed: Optional[int] = None,
        source=True,
        sink=True,
        generate_bounds=None,
        duration_mode_bounds=None,
        duration_delta=None,
        stochastic=False,
    ):
        self.n_jssp_jobs = n_jssp_jobs
        self.n_jssp_machines = n_jssp_machines
        self.seed = seed

        self.generate_bounds = generate_bounds
        self.duration_mode_bounds = duration_mode_bounds
        self.duration_delta = duration_delta

        self.stochastic = stochastic

        self.durations, self.affectations = generate_taillard(
            n_jssp_jobs, n_jssp_machines, self.duration_mode_bounds, seed
        )

        # In RCPSP, the number of jobs is the total number of tasks in JSSP.
        # It also count the source and sink nodes.
        # BELOW W/ SOURCE/SINK
        # n_jobs = n_jssp_jobs * n_jssp_machines + 2
        n_jobs = n_jssp_jobs * n_jssp_machines
        task_ids = np.arange(n_jobs) + 1
        task_ids = task_ids.reshape(n_jssp_jobs, n_jssp_machines)
        if source:
            n_jobs += 1
            source_id = 1
            task_ids = task_ids + 1
        if sink:
            n_jobs += 1
            sink_id = n_jobs
        # source_id, sink_id = 1, n_jobs

        n_modes_per_job = [1] * n_jobs
        # BELOW W/ SOURCE/SINK

        # Successors.
        successors = np.roll(task_ids, shift=-1, axis=1)

        # BELOW W/ SOURCE/SINK
        if sink:
            successors[:, -1] = sink_id
        else:
            successors[:, -1] = -1
        # successors = list(successors.reshape(-1, 1))
        # BELOW W/ SOURCE/SINK
        if sink:
            successors = [[s] for s in successors.reshape(-1)]
        else:
            successors = [[s] if s != -1 else [] for s in successors.reshape(-1)]

        # BELOW W/ SOURCE/SINK
        if source:
            source_successors = list(task_ids[:, 0])
        if sink:
            sink_successors = []
        if source:
            successors = [source_successors] + successors
        if sink:
            successors = successors + [sink_successors]

        # Durations.
        durations = list(self.durations.reshape(-1))
        # Add source and sink durations.
        # BELOW W/ SOURCE/SINK
        if source:
            durations = [0] + durations
        if sink:
            durations = durations + [0]
        # durations = [0] + durations + [0]
        # Add the mode dimension.
        # Add the dmin and dmax duration bounds.
        # durations = [[d, d, d] for d in durations]
        if self.generate_bounds is None:
            if self.duration_delta is not None and self.stochastic:
                rng = np.random.default_rng(seed)

                deltamin = rng.integers(
                    1, self.duration_delta[0], size=(len(durations) - 2)
                )
                dmin = np.array(durations)[1:-1] - deltamin
                dmin = np.where(dmin < 1, 1, dmin).tolist()
                dmin = [0] + dmin + [0]
                deltamax = rng.integers(
                    1, self.duration_delta[1], size=(len(durations) - 2)
                )
                dmax = (np.array(durations)[1:-1] + deltamax).tolist()
                dmax = [0] + dmax + [0]
                durations = [
                    [[d] for d in durations],
                    [[d] for d in dmin],
                    [[d] for d in dmax],
                ]
            else:
                durations = [[d] for d in durations]
                durations = [durations, durations, durations]
        else:
            dmin = [[d * (1.0 - self.generate_bounds[0])] for d in durations]
            dmax = [[d * (1.0 + self.generate_bounds[1])] for d in durations]
            durations = [[[d] for d in durations], dmin, dmax]

        # resources constraints.
        affectations = self.affectations.reshape(-1)
        rr = n_jobs
        if source:
            rr = rr - 1
        if sink:
            rr = rr - 1
        resources_cons = [
            [
                1 if r == affectations[task_id] else 0
                for r in range(1, n_jssp_machines + 1)
            ]
            # BELOW W/ SOURCE/SINK
            # for task_id in range(n_jobs - 2)
            for task_id in range(rr)
        ]
        # BELOW W/ SOURCE/SINK
        # resources_cons = (
        #     [[0 for _ in range(n_jssp_machines)]]  # Source.
        #     + resources_cons
        #     + [[0 for _ in range(n_jssp_machines)]]  # Sink.
        # )
        # Add the mode dimension.
        if source:
            resources_cons = [[0 for _ in range(n_jssp_machines)]] + resources_cons
        if sink:
            resources_cons = resources_cons + [[0 for _ in range(n_jssp_machines)]]
        resources_cons = [[r] for r in resources_cons]

        resources_availabilities = [1 for _ in range(n_jssp_machines)]
        n_renewable_resources = n_jssp_machines
        n_nonrenewable_resources = 0
        n_doubly_constrained_resources = 0

        job_ids = list(range(1, n_jobs + 1))

        super().__init__(
            pb_id,
            job_ids,
            n_modes_per_job,
            successors,
            durations,
            resources_cons,
            resources_availabilities,
            n_renewable_resources,
            n_nonrenewable_resources,
            n_doubly_constrained_resources,
        )

    def sample(self, sampling_type: Optional[str] = None) -> "TaillardRcpsp":
        """Sample a new taillard instance."""
        self.seed = self.seed + 1 if self.seed is not None else None
        return TaillardRcpsp(
            self.pb_id,
            self.n_jssp_jobs,
            self.n_jssp_machines,
            self.seed,
            source=True,
            sink=True,
            generate_bounds=self.generate_bounds,
            duration_mode_bounds=self.duration_mode_bounds,
            duration_delta=self.duration_delta,
            stochastic=self.stochastic,
        )
