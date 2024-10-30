from typing import Dict, Any
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime, timedelta
from config.settings import GANTT_COLORS
import plotly.graph_objects as go  # Add this import for proper typing

def create_gantt_chart(schedule: Dict[str, Any]) -> go.Figure:
    """
    Create a Gantt chart visualization of the schedule
    
    Args:
        schedule: Dictionary containing schedule information
        
    Returns:
        plotly.graph_objects.Figure: The Gantt chart figure
    """
    df_dict = {
        'Task': [],
        'Start': [],
        'Finish': [],
        'Resource': [],
        'Description': []
    }

    base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    # Create DataFrame for Gantt chart
    for job in schedule['jobs']:
        for op in job['operations']:
            start_time = base_date + timedelta(minutes=op['start_time'])
            end_time = base_date + timedelta(minutes=op['end_time'])
            
            df_dict['Task'].append(f"{job['job_id']}-{op['operation']}")
            df_dict['Start'].append(start_time)
            df_dict['Finish'].append(end_time)
            df_dict['Resource'].append(op['machine'])
            df_dict['Description'].append(
                f"Job: {job['job_id']}<br>"
                f"Operation: {op['operation']}<br>"
                f"Duration: {op['end_time'] - op['start_time']} mins"
            )

    df = pd.DataFrame(df_dict)
    
    # Create color mapping for machines
    unique_machines = df['Resource'].unique()
    colors = {machine: GANTT_COLORS[i % len(GANTT_COLORS)] 
             for i, machine in enumerate(unique_machines)}

    # Create Gantt chart
    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Resource',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        height=400,
        title='Production Schedule'
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Machine',
        title_x=0.5,
        xaxis_tickformat='%H:%M',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Add better tooltips
    for i in range(len(fig.data)):
        fig.data[i].hovertext = df['Description']
        fig.data[i].hoverinfo = "text"

    return fig

def export_schedule_figure(fig: go.Figure, filename: str = "production_schedule.html") -> None:
    """
    Export the Gantt chart to an HTML file
    
    Args:
        fig: The Gantt chart figure
        filename: Name of the output file
    """
    fig.write_html(filename)

def create_utilization_chart(schedule: Dict[str, Any], 
                           machine_utilization: Dict[str, float]) -> go.Figure:
    """
    Create a bar chart showing machine utilization
    
    Args:
        schedule: The schedule dictionary
        machine_utilization: Dictionary of machine utilization percentages
        
    Returns:
        plotly.graph_objects.Figure: The utilization chart figure
    """
    machines = list(machine_utilization.keys())
    utilization = list(machine_utilization.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=machines,
            y=utilization,
            text=[f"{u:.1f}%" for u in utilization],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Machine Utilization",
        xaxis_title="Machine",
        yaxis_title="Utilization (%)",
        yaxis_range=[0, 100],
        showlegend=False
    )
    
    return fig