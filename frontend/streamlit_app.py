# streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def main():
    st.title("Workout Tracker")
    log_workout()
    workouts = get_workout_history()
    
    display_workout_history()
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
        response = requests.post("https://triathlon-training-tracker-fastapi.onrender.com/workout", json=workout)
        if response.status_code == 200:
            st.success("Workout logged successfully!")
        else:
            st.error("Failed to log workout")

# write the function to get the workout history from the api and display it in streamlit
def get_workout_history():
    response = requests.get("https://triathlon-training-tracker-fastapi.onrender.com/workouts")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch workout history")
        return None

def display_workout_history():
    st.subheader("Workout History")
    workouts = get_workout_history()
    if workouts:
        with st.expander("View Workout History Table"):
            table_workout_history(workouts)
        plot_workout_history(workouts)

def table_workout_history(workouts):
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'], format='mixed')
    df = df.sort_values('date', ascending=False)

    # display the workout history in a table with delete buttons
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
        with col1:
            st.write(row['date'].strftime('%Y-%m-%d'))
        with col2:
            st.write(row['workout_type'])
        with col3:
            st.write(f"{row['distance']:.2f} km")
        with col4:
            st.write(f"{row['time']:.2f} min")
        with col5:
            st.write(row['id'])
        with col6:
            if st.button('❌', key=f"delete_{row['id']}", help="Delete this workout"):
                response = requests.delete(f"https://triathlon-training-tracker-fastapi.onrender.com/workout/{row['id']}")
                if response.status_code == 200:
                    st.session_state.delete_success = f"Workout {row['id']} deleted successfully!"
                    st.rerun()
                else:
                    st.session_state.delete_error = "Failed to delete workout"

    # Display success or error message below the table
    if 'delete_success' in st.session_state:
        st.success(st.session_state.delete_success)
        del st.session_state.delete_success
    elif 'delete_error' in st.session_state:
        st.error(st.session_state.delete_error)
        del st.session_state.delete_error   
    
def plot_workout_history(workouts):
    
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'], format='mixed')

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
