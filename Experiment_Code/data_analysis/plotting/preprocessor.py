from typing import (
    Literal, 
    Tuple, 
    List,
    Dict
)
from itertools import chain

import numpy as np
import pandas as pd

from helpers.validation import (
    validate_states,
    validate_oneof,
    validate_hand_info_needed
)
from helpers.metadata import (
    HANDEDNESSES, TASKS, MAPPINGS, # String checks
    PIXEL_DISTANCES, 
    PERCENT_INTENSITIES, 
    LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY,
    RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY
)

def generate_prepost_comparison(
        participants: list, 
        pre_allowed_states: dict, 
        post_allowed_states: dict,
        dominant_hands = [] # TODO: dominant hand should be in participant object
) -> Tuple[dict, dict]:
    """
    Generates pre/post comparison statistics (mean, std) of predicted distances across participants.

    Filters each participant's data based on allowed pre- and post-test states,
    extracts intensity-distance prediction pairs, and computes summary statistics.

    Args:
        participants (list): List of `Participant` objects.
        pre_allowed_states (dict): Allowed filtering states for the pre-test condition.
        post_allowed_states (dict): Allowed filtering states for the post-test condition.
        dominant_hands (list, optional): Placeholder for future support of per-participant handedness.

    Returns:
        Tuple[dict, dict]: Two dictionaries containing mean and standard deviation of distances for
                           pre-test and post-test phases, respectively.
    """
    pre_global_predictions = {
        'intensity': [],
        'distance': []
    }
    post_global_predictions = {
        'intensity': [],
        'distance': []
    }

    pre_allowed_states = {**pre_allowed_states, 'phases': ['Pre-Test'], 'block_nrs': [1]}
    post_allowed_states = {**post_allowed_states, 'phases': ['Post-Test'], 'block_nrs': [1]}

    for participant in participants:
        df = participant.get_as_one_dataframe()

        # TODO: later dominant hands are changed for each participant
        pre_intensities, pre_distances = extract_intensity_to_distance_predictions(df, pre_allowed_states, dominant_hand='right')
        post_intensities, post_distances = extract_intensity_to_distance_predictions(df, post_allowed_states, dominant_hand='right')

        pre_global_predictions['intensity'].append(pre_intensities)
        pre_global_predictions['distance'].append(pre_distances)
        post_global_predictions['intensity'].append(post_intensities)
        post_global_predictions['distance'].append(post_distances)

    # Extract inner nestings
    pre_global_predictions['intensity'] = list(chain(*pre_global_predictions['intensity']))
    pre_global_predictions['distance'] = list(chain(*pre_global_predictions['distance']))
    post_global_predictions['intensity'] = list(chain(*post_global_predictions['intensity']))
    post_global_predictions['distance'] = list(chain(*post_global_predictions['distance']))

    pre_means, pre_stds = compute_distances_meanstds(pre_global_predictions)
    post_means, post_stds = compute_distances_meanstds(post_global_predictions)

    pre_data_meanstds = {
        'means': pre_means,
        'stds' : pre_stds
    }
    post_data_meanstds = {
        'means': post_means,
        'stds' : post_stds
    }

    return pre_data_meanstds, post_data_meanstds

# Calculate intensities with given mapping and distances
def calculate_intensity(
        mapping: Literal['direct', 'reversed'], 
        target_pos_y: float
    ) -> float:
    """
    Returns the intensity for a given Y-position and mapping.
    
    This info is not in our output csv and thus needs to be computed in this function.

    Args:
        mapping (Literal['direct', 'reversed']): Mapping direction.
        target_pos_y (float): Target distance of distance classes.

    Returns:
        float: Corresponding intensity.

    Raises:
        ValueError: If mapping does not exist or target position is not part of a class.
    """

    validate_oneof(mapping, MAPPINGS, 'mapping')
    validate_oneof(target_pos_y, PIXEL_DISTANCES, check_type='distance class')

    distance_idx = PIXEL_DISTANCES.index(target_pos_y)
    distance_idx = -(distance_idx + 1) if mapping == 'reversed' else distance_idx
    intensity = PERCENT_INTENSITIES[distance_idx]

    return intensity

def extract_intensity_to_distance_predictions(
        df: pd.DataFrame, 
        allowed_states: dict | pd.DataFrame, 
        dominant_hand: Literal['left', 'right']
    ) -> Tuple[List[float], List[float]] :
    """
    Extracts predicted distances for trials, grouped by intensity.

    Filters the input DataFrame based on allowed state parameters (e.g., tasks, mappings, phases, blocks) to reduce computational costs.
    Then computes intensity per trial distance since it is not part of our output data. Then we collect all predictions of the participants
    for each trial. Then we produce a mapping from the played cue intensities to the predicted distances.


    Args:
        df (pd.DataFrame): Input DataFrame containing trial data.
        allowed_states (dict): Dictionary specifying allowed values for 'tasks', 'mappings', 'phases', and 'block_nrs'.
        dominant_hand (Literal['left', 'right']): Dominant hand used to determine avoiding boundary in the avoiding task.

    Returns:
        Tuple[List[float], List[float]]: Lists of intensities and their corresponding predicted distances.
    """
    validate_states(allowed_states)   
    validate_oneof(dominant_hand, HANDEDNESSES, 'handedness') 

    # Minimize df size by only selecting allowed states and necessary columns
    df = df[['trial_index','task','mapping','phase','block','current_pos_x','target_pos_y','current_pos_y']]
    df = df.loc[  
          df['task'].isin(allowed_states.get('tasks')) 
        & df['mapping'].isin(allowed_states.get('mappings')) 
        & df['phase'].isin(allowed_states.get('phases'))
        & df['block'].isin(allowed_states.get('block_nrs'))
    ]

    if len(df) == 0:
        raise ValueError(
            'Dataframe is empty. It is very likely an impossible state was given leading to disjunct sets in the query.' \
            'Check your queries for such impossible states: e.g. \'Participant mapping is inverse but we select direct\'.'
        )

    # Compute intesity with the given information -> it is not part of the output data!
    df['intensity'] = df[['mapping', 'target_pos_y']].apply(
        lambda row: calculate_intensity(row['mapping'], row['target_pos_y']),
        axis=1
    )

    # Collect the participant's predictions
    intensities = []
    distances = []
    for _, trial in df.groupby('trial_index'):
        task = trial['task'][0]
        intensity = trial['intensity'][0]
        distance = _find_predicted_distance(trial, task, dominant_hand)

        distances.append(distance)
        intensities.append(intensity)

    return intensities, distances

def _find_predicted_distance(
        trial: pd.DataFrame, 
        task: Literal['avoiding', 'reaching'], 
        dominant_hand: Literal['left', 'right'] = None
    ) -> float:
    """
    Predicts the Y-coordinate distance based on task type and handedness.

    For 'reaching', returns the last Y-position in the trial.  
    For 'avoiding', returns the first Y-position where the X-coordinate exceeds the threshold boundary which is based on the dominant hand.

    Args:
        trial (pd.DataFrame): Trial data containing at least 'current_pos_x' and 'current_pos_y' columns.
        task (Literal['avoiding', 'reaching']): The task type to determine prediction logic.
        dominant_hand (Literal['left', 'right'], optional): Required for the 'avoiding' task to select associated threshold boundary.

    Returns:
        float: Predicted Y-coordinate distance, or NaN if the participant did not avoid in the avoiding task.
    """
    validate_oneof(task, TASKS, check_type='task')
    validate_hand_info_needed(dominant_hand, task)

    # Returns last recorded position for reaching.  Returns first position exceeding threshold for avoiding.
    if task == 'reaching':
        prediction_idx = -1
        possible_distances = trial['current_pos_y']
    else:
        prediction_idx = 0
        possible_distances = _find_exceeding_threshold_positions(
            trial[['current_pos_x', 'current_pos_y']], 
            dominant_hand
        )['current_pos_y']

    predicted_distance = possible_distances.iloc[prediction_idx] if len(possible_distances) > 0 else np.nan

    return predicted_distance

def compute_distances_meanstds(data: dict | pd.DataFrame) -> Tuple[List[float], List[float]]:
    """
    Computes the mean and standard deviation of 'distance' values grouped by predefined intensity levels.

    Args:
        data (dict | pd.DataFrame): Input data containing 'intensity' and 'distance' fields.

    Returns:
        Tuple[List[float], List[float]]: Two lists containing the means and standard deviations for each intensity level.
    """
    data = pd.DataFrame(data) # Ensures loc method is available
    means, stds = [], []

    for intensity in PERCENT_INTENSITIES:
        class_distances = data.loc[data['intensity'] == intensity, 'distance']
        means.append(class_distances.mean(skipna=True))
        stds.append(class_distances.std(skipna=True))

    return means, stds

def _find_exceeding_threshold_positions(
        positions: pd.DataFrame, 
        dominant_hand: Literal['left', 'right']
    ) -> pd.DataFrame:
    """
    Filters positions where the X-coordinate exceeds the avoidance threshold for the dominant hand.

    Args:
        positions (pd.DataFrame): DataFrame containing at least a 'current_pos_x' and 'current_pos_y' column.
        dominant_hand (Literal['left', 'right']): Dominant hand used to determine the threshold boundary.

    Returns:
        pd.DataFrame: Filtered DataFrame with rows exceeding the threshold boundary for the specified hand.
                      You can call a position by selecting 'current_pos_x' and 'current_pos_y' columns.
    """
    validate_oneof(dominant_hand, HANDEDNESSES, 'handedness')

    # Select avoid position for dominant hand / trace rail
    avoiding_boundary = {
        'left': LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY,
        'right': RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY
    }[dominant_hand]

    # Chose positions exceeding the boundary marking the point as "avoided".
    exceeding_positions = positions.loc[positions['current_pos_x'] >= avoiding_boundary].reset_index(drop=True)
    
    return exceeding_positions