import streamlit as st
import sqlite3
import os
import time
import pandas as pd  # Ensure pandas is imported

# Connect to SQLite database (creates the database if it doesn't exist)
def connect_to_db():
    conn = sqlite3.connect('rankings.db')
    return conn

# Function to create the rankings table if it doesn't exist
def create_table(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        time TEXT NOT NULL
    )
    ''')
    conn.commit()

# Function to load top 10 rankings
def load_top_rankings(conn):
    return pd.read_sql('SELECT * FROM rankings ORDER BY time ASC LIMIT 10', conn)

# Function to save rankings
def save_ranking(conn, username, time_display):
    conn.execute('INSERT INTO rankings (username, time) VALUES (?, ?)', (username, time_display))
    conn.commit()

# Function to get user's ranking position
def get_user_ranking_position(conn, username):
    ranking_df = pd.read_sql('SELECT username, time FROM rankings ORDER BY time ASC', conn)
    ranking_df['Position'] = ranking_df.reset_index().index + 1  # Add position column
    user_rank = ranking_df[ranking_df['username'] == username]
    if not user_rank.empty:
        return user_rank.iloc[0]['Position']
    return None

# Initialize Streamlit app
st.title("Timer Application")

# Connect to database
conn = connect_to_db()
create_table(conn)

# User input for username
username = st.text_input("Enter your username:")

# Load top 10 rankings
rankings = load_top_rankings(conn)
st.write("Top 10 Rankings:")
st.write(rankings)

# Timer logic
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'user_position' not in st.session_state:
    st.session_state.user_position = None

# Timer display
if st.session_state.running:
    elapsed_seconds = (time.time() - st.session_state.start_time) * 1000  # Convert to milliseconds
    st.session_state.elapsed_time = elapsed_seconds
else:
    st.session_state.elapsed_time = 0

# Calculate seconds and milliseconds
seconds = int(st.session_state.elapsed_time // 1000)
milliseconds = int(st.session_state.elapsed_time % 1000)

# Format the timer display as SS.sss
time_display = f"{seconds:02}.{milliseconds:03}"
st.write(f"Timer: {time_display}")

# Start/Stop button
if st.button("Start/Stop Timer"):
    if not st.session_state.running:
        st.session_state.start_time = time.time() - (st.session_state.elapsed_time / 1000)  # Convert to seconds
        st.session_state.running = True
    else:
        st.session_state.running = False

# Accept/Decline buttons
if not st.session_state.running and st.session_state.elapsed_time > 0:
    if st.button("Accept"):
        save_ranking(conn, username, time_display)
        st.success("Time recorded! Please refresh to see the updated rankings.")

        # Get the user's ranking position
        position = get_user_ranking_position(conn, username)
        st.session_state.user_position = position

    if st.button("Decline"):
        st.session_state.elapsed_time = 0  # Reset timer

# Show the user's ranking position after accepting the time
if st.session_state.user_position is not None:
    st.write(f"Congratulations! Your current ranking position is: #{st.session_state.user_position}")

# Close the database connection
conn.close()

