import matplotlib.pyplot as plt
from helpers import Trial
from helpers.metadata import TABLET_SIZE

def plot_y_trajectory_over_time(trial: Trial) -> None:
    """
    Plots a simple trajectory from timestamp and position_x
    
    @param df A trial dataframe
    """

    # Target pos and trial index stay the same during trial
    target_pos_y = trial.get_target_in_cm()[1]
    trial_index = trial.get_trial_index()

    # trial inherits from DataFrame and can be used as such
    timestamp = trial[["timestamp"]]
    pos = trial.get_trajectory_data_in_cm()[["current_pos_y"]]

    plt.plot(timestamp, pos, label="y-trajectory")
    plt.axhline(y=target_pos_y, color="red", label="target y-pos", linestyle="--")

    ticks = list(range(0, int(TABLET_SIZE)+5, 5))
    ticks.append(target_pos_y)
    plt.yticks(ticks)

    plt.xlabel("time in seconds")
    plt.ylabel("y position")

    plt.title(f"Trial {trial_index}")
    plt.legend()

    plt.show()

def plot_xy_trajectory(trial: Trial) -> None:
    """
    Plots a simple trajectory from x and y position without time data
    
    @param df A trial dataframe
    """

    # Target pos and trial index stay the same during trial
    target_pos_y = trial.get_target_in_cm()[1]
    trial_index = trial.get_trial_index()

    # trial inherits from DataFrame and can be used as such
    pos = trial.get_trajectory_data_in_cm()[["current_pos_x", "current_pos_y"]]

    # plot the figure

    plt.figure()

    plt.plot(pos[["current_pos_x"]], pos[["current_pos_y"]], label="trajectory")
    plt.axhline(y=target_pos_y, color="red", label="target y-pos", linestyle="--")

    ticks = list(range(0, int(TABLET_SIZE)+5, 5))
    ticks.append(target_pos_y)
    plt.yticks(ticks)

    plt.xlim(-5, 5)

    plt.xlabel("time in seconds")
    plt.ylabel("y position")

    plt.title(f"Trial {trial_index}")
    plt.legend()

    plt.show()