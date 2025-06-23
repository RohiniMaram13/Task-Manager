from datetime import datetime
from typing import List, Optional
from supabase import create_client, Client

class TaskManager:
    """Manages tasks by connecting to a Supabase cloud database."""

    def __init__(self, supabase_url: str, supabase_key: str):
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
            # NEW: Only select users where is_active is true
            response = self.supabase.table('profiles').select("username").eq('is_active', True).execute()
            return [profile['username'] for profile in response.data]
        except Exception as e:
            print(f"Error fetching team members: {e}")
            return ["Alex", "Brenda", "Charles"]

    def add_user(self, user_name: str) -> bool:
        """Adds a new, active user to the profiles table."""
        if user_name and user_name not in self.team_members:
            try:
                # When adding a user, ensure they are set to active
                self.supabase.table('profiles').insert({"username": user_name, "is_active": True}).execute()
                self.team_members.append(user_name)
                return True
            except Exception:
                return False
        return False
        
    # NEW: Replaced delete_user with deactivate_user
    def deactivate_user(self, user_name: str) -> None:
        """Deactivates a user instead of deleting them, to preserve history."""
        if not self.supabase: return
        try:
            # Simply set the user's status to inactive
            self.supabase.table('profiles').update({"is_active": False}).eq('username', user_name).execute()
            # Refresh the active team members list
            self.team_members.remove(user_name)
        except Exception as e:
            print(f"Error deactivating user {user_name}: {e}")
            
    # The rest of the functions do not need to change
    def get_all_tasks(self) -> List[dict]:
        if not self.supabase: return []
        try:
            response = self.supabase.table('tasks').select("*").order('id', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def add_user(self, user_name: str) -> bool:
        # ... (no change to this function)
        if user_name and user_name not in self.team_members:
            try:
                self.supabase.table('profiles').insert({"username": user_name}).execute()
                self.team_members.append(user_name)
                return True
            except Exception:
                return False
        return False
        
    # --- NEW FUNCTION: DELETE A USER ---
    def delete_user(self, user_name: str) -> None:
        """Deletes a user and unassigns their tasks."""
        if not self.supabase: return

        try:
            # Step 1: Find all tasks assigned to this user and set them to 'Unassigned'
            self.supabase.table('tasks').update({"assigned_to": None}).eq('assigned_to', user_name).execute()
            
            # Step 2: Delete the user from the 'profiles' table
            self.supabase.table('profiles').delete().eq('username', user_name).execute()
            
            # Step 3: Refresh the local list of team members
            self.team_members.remove(user_name)
        except Exception as e:
            print(f"Error deleting user {user_name}: {e}")

   

    def add_task(self, title: str, priority: str, due_date: datetime, assigned_to: Optional[str] = None, details: Optional[str] = "") -> None:
        # ... (no change to this function)
        try:
            task_data = { "title": title, "priority": priority, "due_date": due_date.isoformat(), "assigned_to": assigned_to, "details": details, "status": "Pending", "created_at": datetime.now().isoformat() }
            self.supabase.table('tasks').insert(task_data).execute()
        except Exception as e:
            print(f"Error adding task: {e}")

    # --- UPDATED FUNCTIONS BELOW ---

    def complete_task(self, task_id: int) -> None:
        """Updates a task's status to 'Completed' using its unique ID."""
        try:
            self.supabase.table('tasks').update({ "status": "Completed", "completed_date": datetime.now().isoformat() }).eq('id', task_id).execute()
        except Exception as e:
            print(f"Error completing task with id {task_id}: {e}")
    
    def delete_task(self, task_id: int) -> None:
        """Deletes a task from the database using its unique ID."""
        try:
            self.supabase.table('tasks').delete().eq('id', task_id).execute()
        except Exception as e:
            print(f"Error deleting task with id {task_id}: {e}")

    def edit_task(self, task_id: int, new_title: str, new_priority: str, new_assigned_to: str, new_details: str) -> None:
        """Edits an existing task in the database using its unique ID."""
        try:
            self.supabase.table('tasks').update({ "title": new_title, "priority": new_priority, "assigned_to": new_assigned_to, "details": new_details }).eq('id', task_id).execute()
        except Exception as e:
            print(f"Error editing task with id {task_id}: {e}")
        
    def clear_completed_tasks(self) -> None:
        """Deletes all completed tasks from the database."""
        try:
            self.supabase.table('tasks').delete().eq('status', 'Completed').execute()
        except Exception as e:
            print(f"Error clearing completed tasks: {e}")
