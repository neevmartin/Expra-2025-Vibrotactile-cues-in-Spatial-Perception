import numpy as np
import pandas as pd
from typing import Literal

from helpers.metadata import (
    PIXEL_DISTANCES, 
    PERCENT_INTENSITIES, 
    PIXEL_RAIL_LEFT, 
    PIXEL_RAIL_RIGHT, 
    PIXEL_RAILWAY_WIDTH,
    AVOIDING_THRESHOLD
)

def validate_subset(sub, super):
    if not set(sub) <= super:
        raise ValueError(f'Set {sub} is not a subset of {super}.')
    
def validate_states(states: dict):
    try:
        validate_subset(states['tasks'], {'avoiding','reaching'})
        validate_subset(states['mappings'], {'direct','reversed'})
        validate_subset(states['phases'], {'Pre-Test','Training','Post-Test'})
        validate_subset(states['block_nrs'], {1, 2, 3, 4, 5})
    except KeyError:
        raise ValueError('Wrong layout for state dictionary.')

# Calculate intensities with given mapping and distances
def calculate_intensity(mapping, target_pos_y):
    try:
        distance_idx = PIXEL_DISTANCES.index(target_pos_y)
    except ValueError:
        raise ValueError('Target position can not be classified.')
    
    if mapping == 'direct':
        intensity = PERCENT_INTENSITIES[distance_idx]
    elif mapping == 'reversed':
        intensity = PERCENT_INTENSITIES[-(distance_idx+1)]
    else:
        raise ValueError(f'Invalid mapping {mapping} found.')
    
    return intensity

def extract_distance_to_intensities(df, allowed_states: dict, dominant_hand: Literal['left', 'right']):
    # Check for valid dictionary layout
    validate_states(allowed_states)    

    # Minimize df size by only selecting allowed states and necessary columns
    df = df[['trial_index','task','mapping','phase','block','current_pos_x','target_pos_y','current_pos_y']]
    df = df.loc[  
          df['task'].isin(allowed_states.get('tasks')) 
        & df['mapping'].isin(allowed_states.get('mappings')) 
        & df['phase'].isin(allowed_states.get('phases'))
        & df['block'].isin(allowed_states.get('block_nrs'))
    ]

    # Check if input is faulty
    if len(df) == 0:
        raise ValueError(
            'Dataframe is empty. It is very likely an impossible state was given leading to disjunct sets in the query.' \
            'Check your queries for such impossible states: e.g. \'Participant mapping is inverse but we select direct\'.')

    # Compute intesity with the given information -> it is not part of the output data!
    df['intensity'] = df[['mapping', 'target_pos_y']].apply(
        lambda row: calculate_intensity(row['mapping'], row['target_pos_y']),
        axis=1
    )

    # Collect the participant's predictions
    distances = []
    intensities = []
    for _, trial in df.groupby('trial_index'):
        played_intensity, predicted_distance = _find_predicted_mapping(trial, dominant_hand)
        distances.append(predicted_distance)
        intensities.append(played_intensity)

    distance_to_intensities_df = pd.DataFrame({
        'distances': distances,
        'intensities': intensities
    })

    return distance_to_intensities_df

def _find_predicted_mapping(trial, dominant_hand):
    last_frame_idx = trial.index[-1]
    task = trial['task'][last_frame_idx]

    if task == 'reaching':
        # Take last recorded position
        predicted_distance = trial['current_pos_y'][last_frame_idx]
    elif task == 'avoiding':
        predicted_distance = find_avoiding_position(
            trial[['current_pos_x', 'current_pos_y']], 
            AVOIDING_THRESHOLD, 
            dominant_hand
        )['current_pos_y']
    else:
        raise ValueError(f'Invalid task {task} found.')
    
    # For the intensity the index does not matter.
    played_intensity = trial['intensity'][last_frame_idx]

    return played_intensity, predicted_distance

def compute_distances_meanvars(data):
    means, stds = [], []

    for intensity in PERCENT_INTENSITIES:
        class_distances = data.loc[data['intensities'] == intensity, 'distances']
        means.append(class_distances.mean(skipna=True))
        stds.append(class_distances.std(skipna=True))

    meanvar_df = pd.DataFrame({
        'means': means,
        'stds' : stds
    })

    return meanvar_df

def find_avoiding_position(positions: pd.DataFrame, threshold, dominant_hand: Literal['left', 'right']):
    distance_from_rail = PIXEL_RAILWAY_WIDTH * threshold

    # Select avoid position for dominant hand / trace rail
    if dominant_hand.lower() == 'left':
        avoid_position = PIXEL_RAIL_RIGHT - distance_from_rail
    elif dominant_hand.lower() == 'right':
        avoid_position = PIXEL_RAIL_LEFT + distance_from_rail
    else:
        raise ValueError('The literal \'{dominant hand}\' is not a valid dominant hand side.')

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