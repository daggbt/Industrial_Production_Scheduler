# Industrial Production Scheduler

## Overview
The Industrial Production Scheduler is a Python-based optimization tool that solves complex job shop scheduling problems using constraint programming. It efficiently schedules manufacturing operations across multiple machines while considering various constraints such as machine capabilities, processing times, and job sequences.

## Table of Contents
- [Industrial Production Scheduler](#industrial-production-scheduler)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Algorithm Details](#algorithm-details)
    - [Constraint Programming Model](#constraint-programming-model)
    - [Optimization Process](#optimization-process)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Advanced Usage](#advanced-usage)
  - [Configuration](#configuration)
    - [Scheduler Parameters](#scheduler-parameters)
    - [Visualization Settings](#visualization-settings)
  - [Visualization](#visualization)
  - [Performance Metrics](#performance-metrics)

## Features
- **Flexible Job Shop Scheduling**: Handle multiple jobs with varying operation sequences
- **Machine Capability Management**: Define machine-specific capabilities and efficiency factors
- **Constraint Handling**:
  - Operation precedence within jobs
  - Machine capacity constraints
  - Processing time variations
  - Setup time considerations
- **Visualization**:
  - Interactive Gantt charts
  - Machine utilization charts
  - Schedule analysis tools
- **Performance Metrics**:
  - Makespan optimization
  - Machine utilization tracking
  - Job completion time analysis

## Algorithm Details

### Constraint Programming Model
The scheduler uses the CP-SAT solver from Google OR-Tools to solve the job shop scheduling problem. The model includes:

1. **Decision Variables**:
```python
- job_starts[job, operation, machine]: Start time of each operation
- job_ends[job, operation, machine]: End time of each operation
- job_machines[job, operation, machine]: Binary variable for machine assignment
```

2. **Constraints**:
- **Assignment Constraints**: Each operation must be assigned to exactly one machine
```python
sum(job_machines[j,o,m] for m in compatible_machines) == 1
```

- **Precedence Constraints**: Operations within a job must be sequential
```python
job_ends[j,o,m1] <= job_starts[j,o+1,m2]
```

- **Resource Constraints**: No machine can process multiple operations simultaneously
```python
NoOverlap(intervals_for_machine)
```

3. **Objective Function**:
```python
Minimize(makespan)
where makespan = max(job_ends[j, last_operation, m])
```

### Optimization Process
1. Problem Initialization
   - Load job and machine data
   - Define operation sequences and durations
   - Set machine capabilities and efficiency factors

2. Model Creation
   - Generate variables for all possible assignments
   - Add necessary constraints
   - Set up the objective function

3. Solution Process
   - Solve using CP-SAT solver
   - Extract and validate solution
   - Generate schedule and metrics

## Project Structure
```
industrial_scheduler/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration parameters
├── models/
│   ├── __init__.py
│   └── data_models.py       # Data classes for jobs and machines
├── scheduler/
│   ├── __init__.py
│   ├── optimizer.py         # Core scheduling logic
│   └── validator.py         # Schedule validation
├── utils/
│   ├── __init__.py
│   ├── visualization.py     # Visualization tools
│   └── helpers.py          # Utility functions
├── tests/
│   ├── __init__.py
│   └── test_scheduler.py    # Unit tests
├── main.py                  # Main application entry
└── requirements.txt         # Dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/daggbt/Industrial_Production_Scheduler.git
cd industrial_scheduler
```

2. Create and activate a conda environment:
```bash
conda env create -f environment.yml
```

3. Activate environment
```bash
conda activate scheduler
```

4. Verify installation:
```bash
python -c "import ortools; import plotly; import pandas; import numpy; print('All packages installed successfully!')"
```

## Running the Application

1. Make sure you're in the project directory:
```bash
cd industrial_scheduler
```

2. Activate the environment:
```bash
conda activate scheduler
```

3. Run the application:
```bash
python main.py
```

## Usage

### Basic Usage
```python
from scheduler.optimizer import ProductionScheduler
from models.data_models import Job, Machine
from datetime import datetime, timedelta

# Create jobs
job1 = Job(
    job_id="J1",
    operations=["cutting", "welding", "assembly"],
    due_date=datetime.now() + timedelta(days=1),
    priority=1,
    release_date=datetime.now()
)

# Create machines
machine1 = Machine(
    machine_id="M1",
    capabilities=["cutting", "welding"],
    efficiency_factor=1.0
)

# Initialize scheduler
scheduler = ProductionScheduler(horizon_minutes=480)

# Add jobs and machines
scheduler.add_job(job1)
scheduler.add_machine(machine1)

# Generate schedule
schedule = scheduler.optimize()

# Visualize results
from utils.visualization import create_gantt_chart
fig = create_gantt_chart(schedule)
fig.show()
```

### Advanced Usage
```python
# Get detailed statistics
stats = scheduler.get_schedule_statistics(schedule)

# Validate schedule
from scheduler.validator import ScheduleValidator
is_valid, issues = ScheduleValidator.validate_schedule(schedule)

# Export results
fig.write_html("schedule.html")
```

## Configuration

### Scheduler Parameters
Configure in `config/settings.py`:
```python
DEFAULT_HORIZON_MINUTES = 1440  # 24 hours
DEFAULT_OPTIMIZATION_TIMEOUT = 60  # seconds

OPERATION_DURATIONS = {
    'cutting': 45,
    'welding': 60,
    'assembly': 90,
    # ...
}
```

### Visualization Settings
```python
GANTT_COLORS = [
    '#2E91E5',  # Blue
    '#E15F99',  # Pink
    '#1CA71C',  # Green
    # ...
]
```

## Visualization

The scheduler provides several visualization tools:

1. **Gantt Charts**
   - Interactive timeline of operations
   - Color-coded by machine or job
   - Hover tooltips with detailed information

2. **Utilization Charts**
   - Machine utilization percentages
   - Job duration analysis
   - Resource loading visualization

## Performance Metrics

The scheduler tracks various performance metrics:

1. **Schedule Quality**
   - Makespan (total completion time)
   - Machine utilization
   - Job completion times

2. **Optimization Performance**
   - Solution time
   - Solution quality
   - Constraint satisfaction

