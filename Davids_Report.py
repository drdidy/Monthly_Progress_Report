import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="David's Progress Dashboard - University of Chicago",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for University of Chicago branding and enhanced UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #8B0000, #A52A2A);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #8B0000;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .task-completed {
        background: linear-gradient(90deg, #d4edda, #c3e6cb);
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .category-header {
        color: #8B0000;
        border-bottom: 2px solid #8B0000;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .progress-text {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa, #e9ecef);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎓 David's Progress Dashboard</h1>
    <h3>University of Chicago</h3>
    <p>Research Progress & Task Completion Tracker</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for month selection and filters
st.sidebar.markdown("### 📅 Report Configuration")
selected_month = st.sidebar.selectbox(
    "Select Month",
    ["August 2025", "September 2025", "October 2025", "November 2025", "December 2025"],
    index=0
)

# Data structure for tasks (easily expandable for other months)
task_data = {
    "August 2025": {
        "PhD Manuscripts": {
            "tasks": [
                "Revised manuscript one (transport-related physical activity) based on supervisor's feedback",
                "Revised manuscript two (light rail and occupational groups) with updated statistical analyses", 
                "Revised manuscript three (occupational sedentary time) with clarified methodology",
                "Completed detailed proofreading and formatting for manuscript one",
                "Coordinated feedback and revisions with committee/supervisors",
                "Prepared manuscript one for final submission by 09/05/25",
                "Outlined final submission timelines for manuscripts two (end of September) and three (October)"
            ],
            "completion": 100,
            "priority": "High"
        },
        "Journal Submission Preparation": {
            "tasks": [
                "Prepared cover letter drafts for journal submission for manuscript one",
                "Finalized supplementary files and appendices for journal submission",
                "Ensured compliance with journal formatting and reference styles"
            ],
            "completion": 100,
            "priority": "High"
        },
        "ONCO-D IRB Protocol Rewrite": {
            "tasks": [
                "Reviewed previous ONCO-D IRB protocol in full detail",
                "Researched updated IRB requirements and templates provided by Julie Johnson",
                "Rewrote the entire ONCO-D protocol from scratch using template",
                "Structured protocol sections clearly",
                "Added sections for data governance and database integration",
                "Drafted detailed data flow charts for ONCO-D database processes",
                "Reviewed relevant IRB protocols feeding into ONCO-D to prepare for cross-referencing",
                "Outlined plan to reference and integrate all related IRB protocols into ONCO-D sections",
                "Coordinated with colleagues (Ilona and Toshio) for preliminary feedback on rewritten draft"
            ],
            "completion": 100,
            "priority": "Medium"
        }
    }
}

# Function to add data for future months (placeholder structure)
def add_month_data(month, categories):
    if month not in task_data:
        task_data[month] = categories

# Get current month data
current_data = task_data.get(selected_month, {})

# Main dashboard content
if current_data:
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = sum(len(cat["tasks"]) for cat in current_data.values())
    completed_tasks = sum(len(cat["tasks"]) for cat in current_data.values() if cat["completion"] == 100)
    categories = len(current_data)
    avg_completion = np.mean([cat["completion"] for cat in current_data.values()])
    
    with col1:
        st.metric("Total Tasks Completed", completed_tasks, f"out of {total_tasks}")
    
    with col2:
        st.metric("Project Categories", categories, "Active areas")
    
    with col3:
        st.metric("Overall Progress", f"{avg_completion:.0f}%", "Average completion")
    
    with col4:
        st.metric("Month", selected_month.split()[0], "Reporting period")

    st.markdown("---")

    # Progress Overview Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Category Progress Overview")
        
        # Create progress chart using streamlit native charts
        categories = list(current_data.keys())
        completions = [current_data[cat]["completion"] for cat in categories]
        task_counts = [len(current_data[cat]["tasks"]) for cat in categories]
        
        # Create dataframe for chart
        chart_df = pd.DataFrame({
            'Category': categories,
            'Completion %': completions,
            'Task Count': task_counts
        })
        
        st.markdown("**Completion Status by Category:**")
        st.bar_chart(chart_df.set_index('Category')['Completion %'], height=300)
        
        # Show completion status with colored indicators
        for i, cat in enumerate(categories):
            completion = completions[i]
            if completion == 100:
                st.success(f"✅ **{cat}**: {completion}% ({task_counts[i]} tasks)")
            elif completion >= 75:
                st.warning(f"🔄 **{cat}**: {completion}% ({task_counts[i]} tasks)")
            else:
                st.error(f"⚠️ **{cat}**: {completion}% ({task_counts[i]} tasks)")
    
    with col2:
        st.markdown("### 🎯 Task Distribution")
        
        # Create a simple visual representation of task distribution
        total_tasks = sum(task_counts)
        
        st.markdown("**Tasks by Category:**")
        for i, cat in enumerate(categories):
            percentage = (task_counts[i] / total_tasks) * 100
            st.markdown(f"**{cat}:** {task_counts[i]} tasks ({percentage:.1f}%)")
            st.progress(percentage / 100)
        
        # Summary metrics
        st.markdown("---")
        st.metric("Total Tasks", total_tasks)
        st.metric("Avg per Category", f"{total_tasks/len(categories):.1f}")
        
        # Task completion chart using native streamlit
        completion_df = pd.DataFrame({
            'Category': categories,
            'Tasks': task_counts
        })
        st.markdown("**Task Count Distribution:**")
        st.bar_chart(completion_df.set_index('Category'))

    st.markdown("---")

    # Detailed Task Breakdown
    st.markdown("### 📋 Detailed Task Breakdown")
    
    for category, details in current_data.items():
        with st.expander(f"**{category}** - {len(details['tasks'])} tasks completed", expanded=True):
            
            # Category header with priority and completion
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**Priority:** {details['priority']}")
            with col2:
                st.markdown(f"**Progress:** {details['completion']}%")
            with col3:
                st.markdown(f"**Tasks:** {len(details['tasks'])}")
            
            # Progress bar
            st.progress(details['completion'] / 100)
            
            # Task list
            st.markdown("**Completed Tasks:**")
            for i, task in enumerate(details['tasks'], 1):
                st.markdown(f"""
                <div class="task-completed">
                    ✅ <strong>{i}.</strong> {task}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Timeline and Next Steps
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗓️ Upcoming Milestones")
        if selected_month == "August 2025":
            st.markdown("""
            - **September 5, 2025:** Final submission of manuscript one
            - **End of September:** Target completion for manuscript two
            - **October:** Target completion for manuscript three
            - **Ongoing:** ONCO-D IRB protocol refinement and approval process
            """)
        else:
            st.info("Milestone data will be populated as tasks are added for this month.")
    
    with col2:
        st.markdown("### 📈 Performance Summary")
        if selected_month == "August 2025":
            st.success("🎉 **Exceptional Progress!** All planned tasks completed successfully")
            st.info("📚 **3 manuscripts** advanced significantly with clear submission timeline")
            st.info("📋 **IRB protocol** completely rewritten and structured for approval")
            st.info("📝 **Journal submission** materials prepared and formatted")

else:
    st.info(f"📝 Task data for {selected_month} will be added as work progresses. Use the sidebar to select August 2025 to view completed work.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>University of Chicago David's Progress Dashboard | Generated: {}</p>
    <p style="font-size: 0.9em;">Track your research milestones and task completion with data-driven insights</p>
</div>
""".format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)

# Instructions for updating
with st.expander("📝 How to Update Dashboard for New Months"):
    st.markdown("""
    To add data for future months:
    
    1. **Locate the `task_data` dictionary** in the code (around line 47)
    2. **Add a new month entry** following this structure:
    
    ```python
    "September 2025": {
        "Category Name": {
            "tasks": ["Task 1", "Task 2", "Task 3"],
            "completion": 85,  # Percentage completed
            "priority": "High"  # High, Medium, or Low
        }
    }
    ```
    
    3. **Update the task lists** as you complete work throughout the month
    4. **Adjust completion percentages** based on your progress
    5. **Add new categories** as needed for different types of work
    
    The dashboard will automatically update charts and metrics based on your data!
    """)
