import numpy as np

def linear_interpolate(start_value, slope, tick_count):
    return start_value + slope * tick_count

def compute_end_values():
    # Given Parameters
    slope = -1E-7
    start_x_command = 0
    start_y_command = 0
    total_ticks = 4E8
    loop_delay = 40E6  # Ticks
    base_clock_rate = 40E6  # Ticks which is equal to 1 second

    # Initial values
    tick_count_fxp = 0
    iteration_count = 0
    x_command = start_x_command
    y_command = start_y_command

    while tick_count_fxp <= total_ticks:
        # Update the commands
        x_command = np.clip(linear_interpolate(x_command, slope, tick_count_fxp), -64,64)
        y_command = np.clip(linear_interpolate(y_command, slope, tick_count_fxp), -64,64)

        print('-----------------------------------')
        print(f'Iteration: {iteration_count}')
        print(f'X Command: {x_command}')
        print(f'Y Command: {y_command}')
        print(f'Elapsed Seconds: {tick_count_fxp / base_clock_rate}')

        # Simulate the delay (increment the tick count by the loop delay)
        tick_count_fxp += loop_delay

        # Update iteration count
        iteration_count += 1

    duration = iteration_count * (1 / (base_clock_rate / loop_delay))  # in seconds
    return x_command, y_command, duration

end_x, end_y, duration = compute_end_values()
print(f"End X Command: {end_x}")
print(f"End Y Command: {end_y}")
print(f"Interpolation Duration: {duration} seconds")