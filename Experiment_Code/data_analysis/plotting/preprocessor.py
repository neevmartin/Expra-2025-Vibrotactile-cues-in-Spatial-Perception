from typing import (
    Literal, 
    Tuple, 
    List
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
):
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
def calculate_intensity(mapping: Literal['direct', 'reversed'], target_pos_y: float) -> float:
    validate_oneof(mapping, MAPPINGS, 'mapping')
    validate_oneof(target_pos_y, PIXEL_DISTANCES, check_type='distance class')

    distance_idx = PIXEL_DISTANCES.index(target_pos_y)
    distance_idx = -(distance_idx + 1) if mapping == 'reversed' else distance_idx
    intensity = PERCENT_INTENSITIES[distance_idx]

    return intensity

def extract_intensity_to_distance_predictions(df, allowed_states: dict, dominant_hand: Literal['left', 'right']):
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
    data = pd.DataFrame(data) # Ensures loc method is available
    means, stds = [], []

    for intensity in PERCENT_INTENSITIES:
        class_distances = data.loc[data['intensity'] == intensity, 'distance']
        means.append(class_distances.mean(skipna=True))
        stds.append(class_distances.std(skipna=True))

    return means, stds

def _find_exceeding_threshold_positions(positions: pd.DataFrame, dominant_hand: Literal['left', 'right']):
    validate_oneof(dominant_hand, HANDEDNESSES, 'handedness')

    # Select avoid position for dominant hand / trace rail
    avoiding_boundary = {
        'left': LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY,
        'right': RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY
    }[dominant_hand]

    # Chose valid avoid positions that exceed the found avoid position
    exceeding_positions = positions.loc[positions['current_pos_x'] >= avoiding_boundary].reset_index(drop=True)
    
    return exceeding_positions