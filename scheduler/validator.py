from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ScheduleValidator:
    @staticmethod
    def validate_schedule(schedule: Dict) -> Tuple[bool, List[str]]:
        """Validate the complete schedule"""
        issues = []
        
        # Check for basic schedule structure
        if not schedule or 'jobs' not in schedule:
            issues.append("Invalid schedule format")
            return False, issues
            
        # Validate each job's operations
        for job in schedule['jobs']:
            if 'operations' not in job:
                issues.append(f"Missing operations for job {job.get('job_id', 'unknown')}")
                continue
                
            # Check operation sequence
            for i in range(len(job['operations']) - 1):
                curr_op = job['operations'][i]
                next_op = job['operations'][i + 1]
                if curr_op['end_time'] > next_op['start_time']:
                    issues.append(
                        f"Invalid sequence in job {job['job_id']}: "
                        f"{curr_op['operation']} ends after {next_op['operation']} starts"
                    )
        
        return len(issues) == 0, issues