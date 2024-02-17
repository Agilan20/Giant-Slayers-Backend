import random

def calculate_tire_pressure_rise(initial_pressure_psi, distance_traveled, variance_factor=0.005,pressure_change_per_meter=0.01):
    """
    Calculate the rise in tire pressure with added variance based on a simplified model.
    
    Parameters:
    - initial_pressure_psi: Initial tire pressure in PSI.
    - distance_traveled: Distance traveled by the car in meters.
    - variance_factor: Factor to introduce variance (default is 0.005 for a subtle rise).
    
    Returns:
    - Final tire pressure after the distance traveled with added variance in PSI.
    """
    # Conversion factor from PSI to Pascals
    psi_to_pa_conversion = 6894.76

    # Convert initial pressure to Pascals
    initial_pressure_pa = initial_pressure_psi * psi_to_pa_conversion

    # You need to replace the following line with an appropriate model
    # based on your specific scenario and available data.
    # This is a placeholder and may not be accurate for your use case.

    # Initialize final pressure with initial pressure
    final_pressure_pa = initial_pressure_pa

    # Run the simulation for the specified number of steps
    for _ in range(distance_traveled):
        # Calculate the change in pressure based on the given distance
        delta_pressure_pa = pressure_change_per_meter

        # Introduce variance
        variance = random.uniform(0, variance_factor * initial_pressure_pa)
        delta_pressure_pa += variance

        # Update final pressure after each step
        final_pressure_pa += delta_pressure_pa

    # Convert final pressure back to PSI
    final_pressure_psi = final_pressure_pa / psi_to_pa_conversion

    return final_pressure_psi

# Example usage:
initial_pressure_psi = 32  # Replace with your actual initial pressure in PSI
number_of_steps = 10000  # Replace with the desired number of steps

final_pressure_psi = calculate_tire_pressure_rise(initial_pressure_psi, number_of_steps)
print(f"Initial Pressure: {initial_pressure_psi} PSI")
print(f"Final Pressure after {number_of_steps} steps: {final_pressure_psi} PSI with Variance")


