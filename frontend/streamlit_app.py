# streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def main():
    st.title("Workout Tracker")
    log_workout()
    display_workout_history()
    workouts = get_workout_history()
    plot_workout_distance_over_time(workouts)

# write the function to log a workout in streamlit and post it to the api
def log_workout():
    st.subheader("Log a Workout")
    workout_type = st.selectbox("Workout Type", ["Running", "Swimming", "Cycling"])
    distance = st.number_input("Distance (km)", min_value=0.0)
    time = st.number_input("Time (minutes)", min_value=0.0)
    date = st.date_input("Date", value=pd.Timestamp.now().date())
    date = pd.to_datetime(date).isoformat()  # Convert to ISO format string
    if st.button("Log Workout"):
        workout = {"workout_type": workout_type.lower(), "distance": distance, "time": time, "date": date}
        response = requests.post("http://localhost:8000/workout", json=workout)
        if response.status_code == 200:
            st.success("Workout logged successfully!")
        else:
            st.error("Failed to log workout")

# write the function to get the workout history from the api and display it in streamlit
def get_workout_history():
    response = requests.get("http://localhost:8000/workouts")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch workout history")
        return None

def display_workout_history():
    st.subheader("Workout History")
    workouts = get_workout_history()
    if workouts:
        plot_workout_history(workouts)
    
def plot_workout_history(workouts):
    
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'], format='mixed')

    # display the workout history in a table
    st.write(df)

    # plot the workout history
    # Group the data by date and workout_type, summing the distances
    df_grouped = df.groupby([df['date'].dt.date, 'workout_type'])['time'].sum().reset_index()

    # Create a bar plot
    fig = px.bar(df_grouped, x='date', y='time', color='workout_type', 
                 title='Daily Workout Times by Type',
                 labels={'date': 'Date', 'time': 'Total Time (minutes)', 'workout_type': 'Workout Type'},
                 barmode='group')  # 'group' mode to show bars side by side

    # Customize the layout
    fig.update_layout(xaxis_tickangle=-45)

    # Display the plot
    st.plotly_chart(fig)

# function that displays the workout history as a plot of total distance over time for each workout type
def plot_workout_distance_over_time(workouts):
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'], format='mixed')

    # Group the data by date and workout_type, summing the distances
    df_grouped = df.groupby([df['date'].dt.date, 'workout_type'])['distance'].sum().reset_index()

    # Calculate cumulative sum of distance for each workout type
    df_grouped['cumulative_distance'] = df_grouped.groupby('workout_type')['distance'].cumsum()

    # Create a line plot
    fig = px.line(df_grouped, x='date', y='cumulative_distance', color='workout_type', 
                 title='Cumulative Workout Distance Over Time',
                 labels={'date': 'Date', 'cumulative_distance': 'Total Distance (km)', 'workout_type': 'Workout Type'})

    # Customize the layout
    fig.update_layout(xaxis_tickangle=-45)

    # Display the plot
    st.plotly_chart(fig)

    
if __name__ == "__main__":
    main()
