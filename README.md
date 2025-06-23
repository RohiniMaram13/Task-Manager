# Task-Manager
An interactive, database-powered project management dashboard built with Streamlit and Python. This application allows teams to manage their work through a clean, modern user interface with features for task management, user administration, and data visualization.

✨ Features
Interactive Dashboard: At-a-glance view of the team's workload and progress with dynamic charts.
Persistent Cloud Database: All data is saved permanently using a Supabase (PostgreSQL) backend. No data is lost when the app is closed.
Full Task Management (CRUD): Users can Create, Read (view), Update (edit), and Delete tasks.
Team Management: Simple interface to add new team members or deactivate existing ones.
Multiple Views:
📇 Task Board: A card-based view of all pending tasks.
🗓️ Team Timeline: A Gantt-style chart to visualize task schedules and assignments.
✅ Completed History: A log of all completed tasks, with the ability to clear the history.
Dynamic Filtering: Filter the task board by priority (High, Medium, Low).



# Tech Stack
Frontend: Streamlit
Backend & Logic: Python
Database: Supabase (PostgreSQL)
Data Manipulation: Pandas
Charting: Plotly Express & Streamlit Native Charts
⚙️ Setup and Installation
To run this project locally, follow these steps:

1. Prerequisites:

Python 3.11 or higher
A free Supabase account with a project created.
2. Clone the Repository:

Bash
git clone https://github.com/RohiniMaram13/Task-Manager.git
cd Task-Manager
3. Create a Virtual Environment:

Bash

# For Windows
python -m venv venv
.\venv\Scripts\activate
4. Install Dependencies:
The requirements.txt file contains all necessary libraries.

Bash

pip install -r requirements.txt
5. Set Up Secret Keys:

Create a folder named .streamlit in the main project directory.
Inside that folder, create a file named secrets.toml.
Add your Supabase credentials to this file:
Ini, TOML

# .streamlit/secrets.toml
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
6. Set Up the Database Tables:

Log in to your Supabase project.
Go to the SQL Editor and run the SQL queries from the database_setup.sql file (or copy them from the project description) to create the profiles and tasks tables.
▶️ Running the Application
Once the setup is complete, run the following command from the main project directory in your terminal:

Bash

streamlit run streamlit_app.py
The application will open automatically in your web browser.






