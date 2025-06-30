from helpers import Condition,Participant,Trial
from plotting import plot_xy_trajectory, plot_y_trajectory_over_time

rd = Condition.load_conditional_group(condition="rd")

print(rd.get_participant_count())
participant = rd.get_participant_by_index(0)

trial = participant.get_trial(32)
plot_xy_trajectory(trial)

plot_y_trajectory_over_time(trial)
