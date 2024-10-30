import logging
import logging.config
from datetime import datetime, timedelta
from config.settings import LOGGING_CONFIG
from models.data_models import Job, Machine
from scheduler.optimizer import ProductionScheduler
from scheduler.validator import ScheduleValidator
from utils.visualization import (
    create_gantt_chart, 
    export_schedule_figure,
    create_utilization_chart
)

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample jobs and machines"""
    jobs = [
        Job(
            job_id="J1",
            operations=["cutting", "welding", "assembly"],
            due_date=datetime.now() + timedelta(days=1),
            priority=1,
            release_date=datetime.now()
        ),
        Job(
            job_id="J2",
            operations=["cutting", "assembly"],
            due_date=datetime.now() + timedelta(days=1),
            priority=2,
            release_date=datetime.now()
        )
    ]
    
    machines = [
        Machine(
            machine_id="M1",
            capabilities=["cutting", "welding"],
            efficiency_factor=1.0
        ),
        Machine(
            machine_id="M2",
            capabilities=["welding", "assembly"],
            efficiency_factor=1.0
        )
    ]
    
    return jobs, machines

def main():
    # Create sample data
    jobs, machines = create_sample_data()
    
    # Initialize scheduler
    scheduler = ProductionScheduler(horizon_minutes=480)  # 8-hour horizon
    
    # Add jobs and machines
    for job in jobs:
        scheduler.add_job(job)
    for machine in machines:
        scheduler.add_machine(machine)
    
    # Generate schedule
    schedule = scheduler.optimize()
    
    if schedule:
        # Validate schedule
        is_valid, issues = ScheduleValidator.validate_schedule(schedule)
        if not is_valid:
            logger.error("Schedule validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return
        
        # Create and save Gantt chart
        gantt_fig = create_gantt_chart(schedule)
        export_schedule_figure(gantt_fig, "production_schedule.html")
        logger.info("Schedule visualization saved to 'production_schedule.html'")
        
        # Calculate and visualize machine utilization
        stats = scheduler.get_schedule_statistics(schedule)
        util_fig = create_utilization_chart(schedule, stats['machine_utilization'])
        export_schedule_figure(util_fig, "machine_utilization.html")
        logger.info("Utilization chart saved to 'machine_utilization.html'")
        
        # Print summary
        print("\nSchedule Summary:")
        print(f"Makespan: {schedule['makespan']} minutes")
        print("\nMachine Utilization:")
        for machine, util in stats['machine_utilization'].items():
            print(f"{machine}: {util:.1f}%")
        print("\nJob Details:")
        for job in schedule['jobs']:
            print(f"\nJob {job['job_id']}:")
            for op in job['operations']:
                print(f"  {op['operation']} on {op['machine']}: "
                      f"{op['start_time']} -> {op['end_time']}")
    else:
        logger.error("Failed to generate schedule")

if __name__ == "__main__":
    main()