# Standard
from typing import (
    Literal, 
    Tuple, 
    List,
    Dict
)
from itertools import chain

# Third Party
import numpy as np
import pandas as pd

# Intern
from helpers.validation import (
    validate_subset,
    validate_states,
    validate_oneof,
    validate_hand_info_needed,
    validate_nonempty
)
from helpers.warnings import (
    nan_occurrence_warning
)
from helpers.metadata import (
    HANDEDNESS_LITERALS, TASKS, MAPPINGS, # String checks
    PIXEL_DISTANCES, 
    PERCENT_INTENSITIES, 
    LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY,
    RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY,
    CONFIRM_BUTTON_COLUMN_NAME,
    HANDEDNESS
)
from helpers import ErrorMessages as errmsg

def generate_prepost_comparison(
        participants: list, 
        pre_allowed_states: dict, 
        post_allowed_states: dict,
) -> Tuple[dict, dict]:
    """
    Generates pre/post comparison statistics (mean, std) of predicted distances across participants.

    Filters each participant's data based on allowed pre- and post-test states,
    extracts intensity-distance prediction pairs, and computes summary statistics.

    Args:
        participants (list): List of `Participant` objects.
        pre_allowed_states (dict): Allowed filtering states for the pre-test condition.
        post_allowed_states (dict): Allowed filtering states for the post-test condition.
        
    Returns:
        Tuple[dict, dict]: Two dictionaries containing mean and standard deviation of distances for
                           pre-test and post-test phases, respectively.
    """
    # Add necessary metadata
    pre_allowed_states = {**pre_allowed_states, 'phases': ['Pre-Test'], 'block_nrs': [1]}
    post_allowed_states = {**post_allowed_states, 'phases': ['Post-Test'], 'block_nrs': [1]}
    
    # Played intensity to predicted distance pairs 
    # NOTE: This might be considerably slower than iterating through 
    #       all participants once but I decided to keep it more readable for everyone.
    pre_predictions = collect_prediction_pairs(participants, pre_allowed_states)
    post_predictions = collect_prediction_pairs(participants, post_allowed_states)

    # Compute summary statistics
    pre_means, pre_stds = compute_distances_meanstds(pre_predictions)
    post_means, post_stds = compute_distances_meanstds(post_predictions)

    # Wrap results for comprehensibility
    pre_data_meanstds = {
        'means': pre_means,
        'stds' : pre_stds
    }
    post_data_meanstds = {
        'means': post_means,
        'stds' : post_stds
    }

    return pre_data_meanstds, post_data_meanstds

def collect_prediction_pairs(
        participants: list, 
        allowed_states: dict, 
    ) -> Dict[str, List[float]]:
    """
    Collects intensity-distance prediction pairs from multiple participants.

    Each participant's data is filtered based on allowed states and processed
    to extract predicted distances. We retrieve the handedness of each participant
    using an immutable dictionary `HANDEDNESS` defined in `metadata.py`

    Args:
        participants (list): List of participant objects, each with `get_as_one_dataframe()`.
        allowed_states (dict): Dictionary defining valid states to filter trials.

    Returns:
        Dict[str, list]: Dictionary with two keys: 'intensity' and 'distance', each mapping to a flat list of floats.
    """
    predictions = {
        'intensity': [],
        'distance': []
    }

    for participant in participants:
        p_id = participant.get_participant_id()
        df = participant.get_as_one_dataframe()
        pre_intensities, pre_distances = extract_intensity_to_distance_predictions(df, allowed_states, dominant_hand=HANDEDNESS.get(p_id, 'right'))

        predictions['intensity'].append(pre_intensities)
        predictions['distance'].append(pre_distances)

    # Extract inner nestings
    predictions['intensity'] = list(chain(*predictions['intensity']))
    predictions['distance'] = list(chain(*predictions['distance']))

    return predictions

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

    Raises:
        ValueError: If allowed states do not follow structure or include contradicting states e.g. mapping = ['direct', 'reversed']. 
                    If for the avoiding task there was no dominant hand assigned.
    """
    validate_states(allowed_states)   
    validate_oneof(dominant_hand, HANDEDNESS_LITERALS, 'handedness') 

    # Minimize df size by only selecting allowed states and necessary columns
    df = df[[
        'trial_index',
        'task',
        'mapping',
        'phase','block',
        'current_pos_x',
        'target_pos_y',
        'current_pos_y', 
        'left_button_pressed'
    ]]
    df = df.loc[  
          df['task'].isin(allowed_states.get('tasks')) 
        & df['mapping'].isin(allowed_states.get('mappings')) 
        & df['phase'].isin(allowed_states.get('phases'))
        & df['block'].isin(allowed_states.get('block_nrs'))
    ]
    # Check for impossible states
    validate_nonempty(df, msg=errmsg.EMPTY_FILTERING)

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
        trial (pd.DataFrame): Trial data containing at least 'current_pos_x' and 'current_pos_y' as well as 'trial_index' columns.
        task (Literal['avoiding', 'reaching']): The task type to determine prediction logic.
        dominant_hand (Literal['left', 'right'], optional): Required for the 'avoiding' task to select associated threshold boundary.

    Returns:
        float: Predicted Y-coordinate distance, or NaN if the participant did not avoid in the avoiding task.

    Raises:
        ValueError: If trial does not include columns 'current_pos_x', 'current_pos_y', 'trial_index'. 
                    If the task does not exist. If for the avoiding task there was no dominant hand assigned.
    """
    validate_subset(('current_pos_x', 'current_pos_y', 'trial_index'), trial.columns)
    validate_oneof(task, TASKS, check_type='task')
    validate_hand_info_needed(dominant_hand, task)

    if task == 'reaching':
        # Returns first recorded position for reaching where confirmation button is pressed.
         # NOTE: HALF TRIAL HEURISTIC
        # We take the halved trial so we do not analyse the first frames 
        # where the confirmation button is still pressed.
        possible_distances = _find_predicted_y_position_reaching_task(
            trial,
            dominant_hand)
    else:
        # Returns first position exceeding threshold for avoiding.
        possible_distances = _find_exceeding_threshold_positions(
            trial[['current_pos_x', 'current_pos_y']], 
            dominant_hand
        )['current_pos_y']

    predicted_distance = possible_distances.iat[0] if not possible_distances.empty else np.nan

    if np.isnan(predicted_distance):
        nan_occurrence_warning(
            task=task,
            context='participant did not avoid' if task == 'avoiding' else "no data was recorded", 
            trial_index=trial['trial_index'].iat[0]
        )

    return predicted_distance

def compute_distances_meanstds(data: dict | pd.DataFrame) -> Tuple[List[float], List[float]]:
    """
    Computes the mean and standard deviation of 'distance' values grouped by predefined intensity levels.

    Args:
        data (dict | pd.DataFrame): Input data containing 'intensity' and 'distance' fields.

    Returns:
        Tuple[List[float], List[float]]: Two lists containing the means and standard deviations for each intensity level.

    Raises:
        ValueError: If data does not contain 'intensity' and 'distance' columns.
    """
    data = pd.DataFrame(data) # Ensures loc method is available
    validate_subset(sub=('intensity', 'distance'), super=data.columns)

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

    Raises:
        ValueError: If handedness does not exist.
    """
    validate_oneof(dominant_hand, HANDEDNESS_LITERALS, 'handedness')

    # Filter positions based on the dominant hand's threshold boundary
    exceeds_threshold = {
        'left': positions['current_pos_x'] <= LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY,
        'right': positions['current_pos_x'] >= RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY
    }[dominant_hand]

    # Chose positions exceeding the boundary marking the point as "avoided".
    exceeding_positions = positions.loc[exceeds_threshold].reset_index(drop=True)
    
    return exceeding_positions

def _find_predicted_y_position_reaching_task(
        trial: pd.DataFrame,
        dominant_hand: Literal['left', 'right']
    ):
    half_trial = trial.iloc[len(trial) // 2:]
    possible_distances = _find_button_press_positions(
        half_trial[['current_pos_x', 'current_pos_y', CONFIRM_BUTTON_COLUMN_NAME]]
    )

    if possible_distances.empty:
        return pd.Series([], dtype=float)

    predicted_position_x = possible_distances.iloc[0]['current_pos_x']
    predicted_position_y = possible_distances.iloc[0]['current_pos_y']

    if dominant_hand == 'left' and predicted_position_x < LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY:
        return pd.Series([], dtype=float)
    if dominant_hand == 'right' and predicted_position_x > RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY:
        return pd.Series([], dtype=float)

    return pd.Series([predicted_position_y])

def _find_button_press_positions(
        press_and_positions: pd.DataFrame, 
    ):
    button_pressed_frames = press_and_positions[press_and_positions[CONFIRM_BUTTON_COLUMN_NAME] == 1]
    button_pressed_positions = button_pressed_frames[['current_pos_x', 'current_pos_y']]
    return button_pressed_positions