from ortools.sat.python import cp_model
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from models.data_models import Job, Machine
from utils.helpers import get_operation_duration
from config.settings import DEFAULT_HORIZON_MINUTES, DEFAULT_OPTIMIZATION_TIMEOUT

logger = logging.getLogger(__name__)

class ProductionScheduler:
    def __init__(self, horizon_minutes: int = DEFAULT_HORIZON_MINUTES):
        """Initialize the production scheduler"""
        self.horizon = horizon_minutes
        self.jobs: List[Job] = []
        self.machines: List[Machine] = []
        
    def add_job(self, job: Job):
        """Add a job to the scheduling problem"""
        self.jobs.append(job)
        logger.info(f"Added job {job.job_id} with {len(job.operations)} operations")

    def add_machine(self, machine: Machine):
        """Add a machine to the scheduling problem"""
        self.machines.append(machine)
        logger.info(f"Added machine {machine.machine_id} with capabilities: {machine.capabilities}")

    def _create_variables(self, model: cp_model.CpModel) -> Tuple[Dict, Dict, Dict, Dict]:
        """Create all necessary variables for the optimization model"""
        job_starts = {}
        job_ends = {}
        job_intervals = {}
        job_machines = {}
        
        # For each job, operation, and compatible machine
        for job in self.jobs:
            for op_idx, operation in enumerate(job.operations):
                # Find compatible machines
                compatible_machines = [m for m in self.machines if operation in m.capabilities]
                if not compatible_machines:
                    logger.error(f"No compatible machine for operation {operation} of job {job.job_id}")
                    continue
                
                # Create variables for each possible machine assignment
                for machine in compatible_machines:
                    suffix = f'{job.job_id}_{op_idx}_{machine.machine_id}'
                    
                    # Create presence variable (indicates if operation is assigned to this machine)
                    presence = model.NewBoolVar(f'presence_{suffix}')
                    
                    # Start time variable
                    start = model.NewIntVar(0, self.horizon, f'start_{suffix}')
                    
                    # Calculate duration based on machine efficiency
                    duration = self._calculate_operation_duration(operation, machine)
                    
                    # End time variable
                    end = model.NewIntVar(0, self.horizon, f'end_{suffix}')
                    
                    # Interval variable
                    interval = model.NewOptionalIntervalVar(
                        start, duration, end, presence,
                        f'interval_{suffix}'
                    )
                    
                    # Store all variables
                    job_starts[job.job_id, op_idx, machine.machine_id] = start
                    job_ends[job.job_id, op_idx, machine.machine_id] = end
                    job_intervals[job.job_id, op_idx, machine.machine_id] = interval
                    job_machines[job.job_id, op_idx, machine.machine_id] = presence
        
        return job_starts, job_ends, job_intervals, job_machines

    def _add_constraints(self, model: cp_model.CpModel, 
                        job_starts: Dict, job_ends: Dict, 
                        job_intervals: Dict, job_machines: Dict):
        """Add all necessary constraints to the model"""
        
        # 1. Each operation must be assigned to exactly one machine
        self._add_assignment_constraints(model, job_machines)
        
        # 2. Operations within each job must be sequential
        self._add_precedence_constraints(model, job_starts, job_ends, job_machines)
        
        # 3. No overlapping operations on machines
        self._add_resource_constraints(model, job_intervals)
        
        # 4. Release time constraints
        self._add_time_constraints(model, job_starts, job_machines)

    def _add_assignment_constraints(self, model: cp_model.CpModel, job_machines: Dict):
        """Ensure each operation is assigned to exactly one machine"""
        for job in self.jobs:
            for op_idx, operation in enumerate(job.operations):
                compatible_machines = [m for m in self.machines if operation in m.capabilities]
                model.Add(
                    sum(job_machines[job.job_id, op_idx, m.machine_id] 
                        for m in compatible_machines) == 1
                )

    def _add_precedence_constraints(self, model: cp_model.CpModel, 
                                  job_starts: Dict, job_ends: Dict, 
                                  job_machines: Dict):
        """Ensure operations within each job are performed in sequence"""
        for job in self.jobs:
            for op_idx in range(len(job.operations) - 1):
                current_op = job.operations[op_idx]
                next_op = job.operations[op_idx + 1]
                
                current_machines = [m for m in self.machines if current_op in m.capabilities]
                next_machines = [m for m in self.machines if next_op in m.capabilities]
                
                for m1 in current_machines:
                    for m2 in next_machines:
                        model.Add(
                            job_ends[job.job_id, op_idx, m1.machine_id] <=
                            job_starts[job.job_id, op_idx + 1, m2.machine_id]
                        ).OnlyEnforceIf([
                            job_machines[job.job_id, op_idx, m1.machine_id],
                            job_machines[job.job_id, op_idx + 1, m2.machine_id]
                        ])

    def _add_resource_constraints(self, model: cp_model.CpModel, job_intervals: Dict):
        """Ensure no machine is processing multiple operations simultaneously"""
        for machine in self.machines:
            machine_intervals = []
            for job in self.jobs:
                for op_idx, operation in enumerate(job.operations):
                    if operation in machine.capabilities:
                        machine_intervals.append(
                            job_intervals[job.job_id, op_idx, machine.machine_id]
                        )
            model.AddNoOverlap(machine_intervals)

    def _add_time_constraints(self, model: cp_model.CpModel, 
                            job_starts: Dict, job_machines: Dict):
        """Add release time and due date constraints"""
        for job in self.jobs:
            for op_idx, operation in enumerate(job.operations):
                compatible_machines = [m for m in self.machines if operation in m.capabilities]
                for machine in compatible_machines:
                    # Release time constraint
                    model.Add(
                        job_starts[job.job_id, op_idx, machine.machine_id] >= 0
                    ).OnlyEnforceIf(job_machines[job.job_id, op_idx, machine.machine_id])

    def _set_objective(self, model: cp_model.CpModel, 
                      job_ends: Dict, job_machines: Dict) -> cp_model.IntVar:
        """Set up the optimization objective"""
        max_end = model.NewIntVar(0, self.horizon, 'makespan')
        
        # Minimize makespan (completion time of last operation)
        for job in self.jobs:
            last_op_idx = len(job.operations) - 1
            last_op = job.operations[last_op_idx]
            compatible_machines = [m for m in self.machines if last_op in m.capabilities]
            
            for machine in compatible_machines:
                model.Add(
                    max_end >= job_ends[job.job_id, last_op_idx, machine.machine_id]
                ).OnlyEnforceIf(job_machines[job.job_id, last_op_idx, machine.machine_id])
        
        model.Minimize(max_end)
        return max_end

    def _calculate_operation_duration(self, operation: str, machine: Machine) -> int:
        """Calculate operation duration considering machine efficiency"""
        base_duration = get_operation_duration(operation)
        return int(base_duration / machine.efficiency_factor)

    def _create_schedule(self, solver: cp_model.CpSolver, 
                        job_starts: Dict, job_ends: Dict, 
                        job_machines: Dict, makespan: cp_model.IntVar) -> Optional[Dict]:
        """Create the final schedule from the solver's solution"""
        schedule = {
            'jobs': [],
            'makespan': solver.Value(makespan)
        }
        
        for job in self.jobs:
            job_schedule = {
                'job_id': job.job_id,
                'operations': []
            }
            
            for op_idx, operation in enumerate(job.operations):
                compatible_machines = [m for m in self.machines if operation in m.capabilities]
                
                for machine in compatible_machines:
                    if solver.Value(job_machines[job.job_id, op_idx, machine.machine_id]):
                        start_time = solver.Value(
                            job_starts[job.job_id, op_idx, machine.machine_id]
                        )
                        end_time = solver.Value(
                            job_ends[job.job_id, op_idx, machine.machine_id]
                        )
                        
                        job_schedule['operations'].append({
                            'operation': operation,
                            'machine': machine.machine_id,
                            'start_time': start_time,
                            'end_time': end_time
                        })
            
            schedule['jobs'].append(job_schedule)
        
        return schedule

    def optimize(self) -> Optional[Dict]:
        """Main optimization method"""
        logger.info("Starting optimization...")
        model = cp_model.CpModel()
        
        # Create variables
        job_starts, job_ends, job_intervals, job_machines = self._create_variables(model)
        
        # Add constraints
        self._add_constraints(model, job_starts, job_ends, job_intervals, job_machines)
        
        # Set objective
        makespan = self._set_objective(model, job_ends, job_machines)
        
        # Solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = DEFAULT_OPTIMIZATION_TIMEOUT
        logger.info("Starting solver...")
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Solution found with status: {status}")
            return self._create_schedule(solver, job_starts, job_ends, job_machines, makespan)
        else:
            logger.error(f"No solution found. Status: {status}")
            return None

    def get_schedule_statistics(self, schedule: Dict) -> Dict:
        """Calculate various statistics about the schedule"""
        if not schedule:
            return {}
            
        stats = {
            'makespan': schedule['makespan'],
            'total_jobs': len(schedule['jobs']),
            'machine_utilization': {},
            'job_durations': {},
            'machine_load': {}
        }
        
        # Calculate machine utilization
        for machine in self.machines:
            machine_time = 0
            machine_ops = 0
            for job in schedule['jobs']:
                for op in job['operations']:
                    if op['machine'] == machine.machine_id:
                        machine_time += op['end_time'] - op['start_time']
                        machine_ops += 1
            
            stats['machine_utilization'][machine.machine_id] = \
                (machine_time / schedule['makespan']) * 100
            stats['machine_load'][machine.machine_id] = machine_ops
        
        # Calculate job durations
        for job in schedule['jobs']:
            if job['operations']:
                start = min(op['start_time'] for op in job['operations'])
                end = max(op['end_time'] for op in job['operations'])
                stats['job_durations'][job['job_id']] = end - start
        
        return stats