import numpy as np
import pandas as pd
from typing import Literal
from itertools import chain

from helpers.validation import (
    validate_states,
    validate_oneof,
    validate_hand_info_needed
)
from helpers.metadata import (
    PIXEL_DISTANCES, 
    PERCENT_INTENSITIES, 
    PIXEL_RAIL_LEFT, 
    PIXEL_RAIL_RIGHT, 
    PIXEL_FROM_RAIL_CONFIRM_DISTANCE
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

    pre_allowed_states.update({
        'phases':    ['Pre-Test'], 
        'block_nrs': [1]
    })
    post_allowed_states.update({
        'phases':    ['Post-Test'], 
        'block_nrs': [1]
    })

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
def calculate_intensity(mapping, target_pos_y):
    validate_oneof(mapping, ['direct', 'reversed'], 'mapping')
    validate_oneof(target_pos_y, PIXEL_DISTANCES, type='distance class')

    distance_idx = PIXEL_DISTANCES.index(target_pos_y)
    match mapping:
        case 'direct'  : intensity = PERCENT_INTENSITIES[distance_idx]
        case 'reversed': intensity = PERCENT_INTENSITIES[-(distance_idx+1)]
    
    return intensity

def extract_intensity_to_distance_predictions(df, allowed_states: dict, dominant_hand: Literal['left', 'right']):
    validate_states(allowed_states)   
    validate_oneof(dominant_hand, ['left', 'right'], 'handedness') 

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

def _find_predicted_distance(trial, task, dominant_hand = None):
    validate_oneof(task, ['reaching', 'avoiding'], type='Task')
    validate_hand_info_needed(dominant_hand, task)

    match task:
        case 'reaching':
            predicted_distance = trial['current_pos_y'].iloc[-1]
        case'avoiding':
            predicted_distance = find_avoiding_position(
                trial[['current_pos_x', 'current_pos_y']], 
                dominant_hand
            )['current_pos_y']

    return predicted_distance

def compute_distances_meanstds(data: dict | pd.DataFrame):
    data = pd.DataFrame(data) # Ensures loc method is available
    means, stds = [], []

    for intensity in PERCENT_INTENSITIES:
        class_distances = data.loc[data['intensity'] == intensity, 'distance']
        means.append(class_distances.mean(skipna=True))
        stds.append(class_distances.std(skipna=True))

    return means, stds

def find_avoiding_position(positions: pd.DataFrame, dominant_hand: Literal['left', 'right']):
    validate_oneof(dominant_hand, ['left', 'right'], 'handedness')

    # Select avoid position for dominant hand / trace rail
    match dominant_hand:
        case 'left': avoid_position = PIXEL_RAIL_RIGHT - PIXEL_FROM_RAIL_CONFIRM_DISTANCE
        case 'right': avoid_position = PIXEL_RAIL_LEFT + PIXEL_FROM_RAIL_CONFIRM_DISTANCE

    # Chose valid avoid positions that exceed the found avoid position
    valid_positions = positions.loc[positions['current_pos_x'] >= avoid_position].reset_index(drop=True)

    if len(valid_positions) == 0:
        # Set marker for when the participant did not avoid
        valid_positions = pd.DataFrame({
            'current_pos_x': np.nan,
            'current_pos_y': np.nan
        }, index=[0])
    
    first_avoiding_position = valid_positions.iloc[0]
    return first_avoiding_position