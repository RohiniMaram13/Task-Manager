from datetime import datetime
from typing import List, Optional
from supabase import create_client, Client

class TaskManager:
    """Manages tasks by connecting to a Supabase cloud database."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initializes the TaskManager and connects to Supabase."""
        self.team_members: List[str] = []
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.team_members = self.get_team_members()
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            self.supabase = None

    def get_team_members(self) -> List[str]:
        """Fetches the list of ACTIVE usernames from the profiles table."""
        if not self.supabase: return ["Alex", "Brenda", "Charles"]
        try:
            response = self.supabase.table('profiles').select("username").eq('is_active', True).execute()
            return [profile['username'] for profile in response.data]
        except Exception as e:
            print(f"Error fetching team members: {e}")
            return ["Alex", "Brenda", "Charles"]

    def get_all_tasks(self) -> List[dict]:
        """Fetches all tasks from the Supabase database, most recent first."""
        if not self.supabase: return []
        try:
            response = self.supabase.table('tasks').select("*").order('id', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def add_user(self, user_name: str) -> bool:
        """Adds a new user or reactivates an existing one using upsert."""
        if user_name:
            try:
                # Upsert will find a user with the matching 'username' and update them,
                # or it will create a new user if one doesn't exist.
                # on_conflict='username' tells Supabase which column to match on.
                self.supabase.table('profiles').upsert(
                    {"username": user_name, "is_active": True},
                    on_conflict="username"
                ).execute()
                
                # Refresh the local list of team members from the database
                self.team_members = self.get_team_members()
                return True
            except Exception as e:
                print(f"Error upserting user: {e}")
                return False
        return False

    def deactivate_user(self, user_name: str) -> None:
        """Deactivates a user by setting is_active to false, preserving history."""
        if not self.supabase: return
        try:
            self.supabase.table('profiles').update({"is_active": False}).eq('username', user_name).execute()
            self.team_members = self.get_team_members()
        except Exception as e:
            print(f"Error deactivating user {user_name}: {e}")

    def add_task(self, title: str, priority: str, due_date: datetime, assigned_to: Optional[str] = None, details: Optional[str] = "") -> None:
        try:
            task_data = { "title": title, "priority": priority, "due_date": due_date.isoformat(), "assigned_to": assigned_to, "details": details, "status": "Pending", "created_at": datetime.now().isoformat() }
            self.supabase.table('tasks').insert(task_data).execute()
        except Exception as e:
            print(f"Error adding task: {e}")

    def complete_task(self, task_id: int) -> None:
        try:
            self.supabase.table('tasks').update({ "status": "Completed", "completed_date": datetime.now().isoformat() }).eq('id', task_id).execute()
        except Exception as e:
            print(f"Error completing task with id {task_id}: {e}")
    
    def delete_task(self, task_id: int) -> None:
        try:
            self.supabase.table('tasks').delete().eq('id', task_id).execute()
        except Exception as e:
            print(f"Error deleting task with id {task_id}: {e}")

    def edit_task(self, task_id: int, new_title: str, new_priority: str, new_assigned_to: str, new_details: str) -> None:
        try:
            self.supabase.table('tasks').update({ "title": new_title, "priority": new_priority, "assigned_to": new_assigned_to, "details": new_details }).eq('id', task_id).execute()
        except Exception as e:
            print(f"Error editing task with id {task_id}: {e}")
        
    def clear_completed_tasks(self) -> None:
        try:
            self.supabase.table('tasks').delete().eq('status', 'Completed').execute()
        except Exception as e:
            print(f"Error clearing completed tasks: {e}")
