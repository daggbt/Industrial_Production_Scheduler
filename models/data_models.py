from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple

@dataclass
class Job:
    job_id: str
    operations: List[str]
    due_date: datetime
    priority: int
    release_date: datetime

@dataclass
class Machine:
    machine_id: str
    capabilities: List[str]
    efficiency_factor: float