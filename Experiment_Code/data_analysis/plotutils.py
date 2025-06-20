import matplotlib.pyplot as plt 
import pandas as pd
from trial import Trial

def plot_trajectory(trial: Trial) -> None:
    """
    Plots a simple trajectory from timestamp and position_x
    
    @param df A trial dataframe
    """

    # Target pos and trial index stay the same during trial
    target_pos_y = trial.get_target()[1]
    trial_index = trial.get_trial_index()

    # trial inherits from DataFrame and can be used as such
    timestamp = trial[["timestamp"]]
    pos = trial[["current_pos_y"]]

    plt.plot(timestamp, pos, label="y-trajectory")
    plt.axhline(y=target_pos_y, color="red", label="target y-pos")

    plt.xlabel("time in seconds")
    plt.ylabel("y position")
    plt.title(f"Trial {trial_index}")

    plt.show()