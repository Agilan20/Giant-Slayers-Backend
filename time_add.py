from datetime import datetime, timedelta

def adjust_time(start_time, offset_seconds):
    # Convert the start time to a datetime object
    start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    # Calculate the adjusted time by adding the offset in seconds
    adjusted_datetime = start_datetime + timedelta(seconds=offset_seconds)

    # Format the adjusted time as YYYY-MM-DD HH:MM:SS
    adjusted_time = adjusted_datetime.strftime("%Y-%m-%d %H:%M:%S")

    return adjusted_time

# Example usage
start_time = "2024-02-17 17:50:22"  # Replace with your start time
offset_seconds = 38             # Replace with your offset in seconds

adjusted_time = adjust_time(start_time, offset_seconds)
print("Adjusted Time:", adjusted_time)
