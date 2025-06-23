import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# --- SETUP ---
project_path = os.path.join(os.getcwd(), 'workspace', 'task_manager', 'task_manager')
sys.path.append(project_path)
from task_manager import TaskManager

# --- Initialize Session State ---
if 'task_manager' not in st.session_state:
    try:
        st.session_state.task_manager = TaskManager(
            supabase_url=st.secrets["SUPABASE_URL"],
            supabase_key=st.secrets["SUPABASE_KEY"]
        )
    except Exception as e:
        st.error(f"Could not connect to the database. Please check your Supabase credentials in secrets.toml. Error: {e}")
        st.stop()

if 'editing_task_id' not in st.session_state:
    st.session_state.editing_task_id = None
if 'confirming_deactivate_user' not in st.session_state:
    st.session_state.confirming_deactivate_user = None

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Team Task Manager")

# --- Main Application UI ---
st.title("✅ Team Task Manager")

# --- Sidebar ---
with st.sidebar:
    st.title("User Controls")
    team_member_list = st.session_state.task_manager.team_members
    current_user = st.selectbox("Select Your User Profile", team_member_list)
    st.info(f"You are logged in as: **{current_user}**")
    
    st.title("Manage Team")
    with st.expander("Add New User"):
        new_user_name = st.text_input("New User Name", key="new_user_input")
        if st.button("Add User"):
            if new_user_name:
                if st.session_state.task_manager.add_user(new_user_name):
                    st.success(f"User '{new_user_name}' added!")
                    st.rerun() 
                else:
                    st.warning(f"User '{new_user_name}' already exists.")
            else:
                st.warning("Please enter a user name.")
    
    with st.expander("Deactivate User"):
        if len(team_member_list) > 1:
            user_to_deactivate = st.selectbox("Select User to Deactivate", [name for name in team_member_list if name != 'Unassigned'])
            if st.button("Deactivate User", type="primary"):
                st.session_state.confirming_deactivate_user = user_to_deactivate
                st.rerun()
        else:
            st.warning("Cannot deactivate the last user.")

    if st.session_state.confirming_deactivate_user:
        user_to_deactivate = st.session_state.confirming_deactivate_user
        st.error(f"Are you sure you want to deactivate {user_to_deactivate}?", icon="⚠️")
        col1_del, col2_del = st.columns(2)
        if col1_del.button("YES, DEACTIVATE", use_container_width=True):
            st.session_state.task_manager.deactivate_user(user_to_deactivate)
            st.session_state.confirming_deactivate_user = None
            st.rerun()
        if col2_del.button("Cancel", use_container_width=True):
            st.session_state.confirming_deactivate_user = None
            st.rerun()

# --- Data Loading ---
all_tasks_raw = st.session_state.task_manager.get_all_tasks()
active_team_members = st.session_state.task_manager.team_members

# --- Dashboard Section ---
st.header("Project Dashboard", divider="rainbow")

if not all_tasks_raw:
    st.info("No tasks in the system yet. Add a task to see the dashboard.")
else:
    df = pd.DataFrame(all_tasks_raw)
    
    col1_chart, col2_chart = st.columns(2)

    with col1_chart:
        st.subheader("Overall Task Status")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig_pie = px.pie(
                status_counts, 
                names='Status', 
                values='Count', 
                title='Pending vs. Completed',
                color='Status',
                color_discrete_map={'Pending':'#FFD966', 'Completed':'#28a745'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2_chart:
        st.subheader("Active Team Workload by Priority")
        
        # --- THIS IS THE CORRECTED GRAPH LOGIC ---
        tasks_for_graph = [
            task for task in all_tasks_raw 
            if task.get('status') == 'Pending' and 
               ((task.get('assigned_to') in active_team_members) or (task.get('assigned_to') is None))
        ]
        
        if not tasks_for_graph:
            st.info("No pending tasks for the active team.")
        else:
            df_pending = pd.DataFrame(tasks_for_graph)
            if 'assigned_to' in df_pending.columns and 'priority' in df_pending.columns:
                df_pending['assigned_to'].fillna('Unassigned', inplace=True)
                workload_crosstab = pd.crosstab(df_pending['assigned_to'], df_pending['priority'])
                
                # Reorder columns to High, Medium, Low for a logical display
                priority_order = [p for p in ["High", "Medium", "Low"] if p in workload_crosstab.columns]
                workload_crosstab = workload_crosstab[priority_order]

                PRIORITY_COLOR_MAP = {"High": "#0D0564", "Medium": "#3F4BD1", "Low": "#6B97FF"}
                chart_colors = [PRIORITY_COLOR_MAP[col] for col in workload_crosstab.columns if col in PRIORITY_COLOR_MAP]
                
                st.bar_chart(workload_crosstab, color=chart_colors)


# --- Tabs for Different Views ---
card_view_tab, timeline_view_tab, completed_tab = st.tabs(["📇 Task Board", "🗓️ Team Timeline", "✅ Completed Tasks"])

with card_view_tab:
    # ... (code for this tab is the same)
    st.header("Pending Tasks")
    filter_priority = st.radio("Filter by Priority:", options=["All", "High", "Medium", "Low"], horizontal=True)
    
    pending_tasks = [task for task in all_tasks_raw if task.get('status') == "Pending"]
    if filter_priority != "All":
        pending_tasks = [task for task in pending_tasks if task.get('priority') == filter_priority]

    if not pending_tasks:
        st.info("No pending tasks match your filter.")
    else:
        num_columns = 3
        cols = st.columns(num_columns)
        for i, task in enumerate(pending_tasks):
            with cols[i % num_columns]:
                task_id = task.get('id')
                task_title = task.get('title')

                if st.session_state.editing_task_id == task_id:
                    with st.form(key=f"edit_form_{task_id}"):
                        st.write(f"#### Edit Task:")
                        new_title = st.text_input("Title", value=task.get('title'))
                        new_details = st.text_area("Details", value=task.get('details'))
                        new_priority = st.selectbox("Priority", options=["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task.get('priority')))
                        new_assignee = st.selectbox("Assign To", options=team_member_list, index=team_member_list.index(task.get('assigned_to')))
                        
                        col_save, col_cancel = st.columns(2)
                        if col_save.form_submit_button("Save", use_container_width=True, type="primary"):
                            st.session_state.task_manager.edit_task(task_id, new_title, new_priority, new_assignee, new_details)
                            st.session_state.editing_task_id = None
                            st.rerun()
                        if col_cancel.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.editing_task_id = None
                            st.rerun()
                else:
                    with st.container(border=True):
                        st.write(f"#### {task_title}")
                        st.info(f"👤 Assigned to: {task.get('assigned_to') or 'Unassigned'}")
                        if task.get('priority') == "High": st.error(f"Priority: {task.get('priority')}")
                        elif task.get('priority') == "Medium": st.warning(f"Priority: {task.get('priority')}")
                        else: st.info(f"Priority: {task.get('priority')}")
                        
                        if task.get('details'):
                            with st.expander("Show Details"):
                                st.markdown(task.get('details'))
                        
                        col_b1, col_b2, col_b3 = st.columns(3)
                        if col_b1.button("Complete", key=f"complete_{task_id}", use_container_width=True):
                            st.session_state.task_manager.complete_task(task_id)
                            st.rerun()
                        if col_b2.button("Edit", key=f"edit_{task_id}", use_container_width=True):
                            st.session_state.editing_task_id = task_id
                            st.rerun()
                        if col_b3.button("Delete", key=f"delete_{task_id}", use_container_width=True):
                            st.session_state.task_manager.delete_task(task_id)
                            st.rerun()

    with st.expander("➕ Add a New Task", expanded=True):
        with st.form(key="add_task_form", clear_on_submit=True):
            st.write("Enter the details for the new task:")
            col1_add, col2_add = st.columns(2)
            with col1_add:
                new_task_title = st.text_input("Task Title")
                new_task_assignee = st.selectbox("Assign To", options=team_member_list)
            with col2_add:
                new_task_priority = st.selectbox("Priority", options=["High", "Medium", "Low"])
                new_task_due_date = st.date_input("Due Date", value=datetime.now())
            
            new_task_details = st.text_area("Details (Optional)")
            
            if st.form_submit_button("Save Task"):
                if new_task_title:
                    due_datetime = datetime.combine(new_task_due_date, datetime.min.time())
                    st.session_state.task_manager.add_task(new_task_title, new_task_priority, due_datetime, new_task_assignee, new_task_details)
                    st.success("Task added!")
                else:
                    st.warning("Task title cannot be empty.")

with timeline_view_tab:
    st.subheader("Team Task Schedule")
    all_pending_tasks_timeline = [task for task in all_tasks_raw if task.get('status') == "Pending"]
    if not all_pending_tasks_timeline:
        st.info("No pending tasks to display on the timeline.")
    else:
        task_data_timeline = [dict(Task=t.get('title'), Start=datetime.fromisoformat(t.get('due_date')), Finish=datetime.fromisoformat(t.get('due_date')) + timedelta(hours=2), Resource=t.get('assigned_to') or 'Unassigned') for t in all_pending_tasks_timeline]
        df_timeline = pd.DataFrame(task_data_timeline)
        fig = px.timeline(df_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource", title="Task Assignments by Due Date")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

with completed_tab:
    st.header("Completed Task History")
    
    completed_tasks = [task for task in all_tasks_raw if task.get('status') == "Completed"]
    
    if not completed_tasks:
        st.info("No tasks have been completed yet.")
    else:
        if st.button("🧹 Clear All Completed Tasks"):
            st.session_state.task_manager.clear_completed_tasks()
            st.rerun()

        st.caption("A log of all tasks that have been marked as complete.")
        
        completed_tasks.sort(key=lambda x: datetime.fromisoformat(x.get('completed_date')) if x.get('completed_date') else datetime.min, reverse=True)
        
        for task in completed_tasks:
            with st.container(border=True):
                st.write(f"**{task.get('title')}**")
                if task.get('completed_date'):
                    completed_date_str = datetime.fromisoformat(task.get('completed_date')).strftime('%Y-%m-%d at %H:%M')
                    st.success(f"Completed by **{task.get('assigned_to')}** on {completed_date_str}")
