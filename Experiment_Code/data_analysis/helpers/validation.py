# Standard
from typing import (
    Any, 
    List, 
    Iterable, 
    Dict,
    Literal
)
from collections.abc import Sized

# Intern
from .messages import ErrorMessages as errmsg

ALLOWED_STATES = {
    'tasks': {'avoiding', 'reaching'},
    'mappings': {'direct', 'reversed'},
    'phases': {'Pre-Test', 'Training', 'Post-Test'},
    'block_nrs': {1, 2, 3, 4, 5},
}
"""
Constant of the biggest possible state dictionary with all states a trial can be in.
"""

# Collection of all validation classes we might need

def validate_subset(sub: Iterable, super: Iterable):
    """
    Validates that all elements in `subset` exist in `superset`.

    Args:
        subset (Iterable): The candidate subset.
        superset (Iterable): The collection to validate against.

    Raises:
        ValueError: If `subset` is not a subset of `superset`.
    """
    if not set(sub).issubset(set(super)):
        raise ValueError(errmsg.NO_SUBSET_OF_SUPERSET.format(sub=sub, super=super))
    
def validate_states(states: Dict[str, Iterable]):
    """
    Validates the structure and values of a `states` dictionary
    which captures all the possible state combinations in a trial.

    Expected Keys and Valid Values:
        - 'tasks': {'avoiding', 'reaching'}
        - 'mappings': {'direct', 'reversed'}
        - 'phases': {'Pre-Test', 'Training', 'Post-Test'}
        - 'block_nrs': {1, 2, 3, 4, 5}

    Args:
        states (Mapping[str, Iterable]): A dictionary of state names to their values.

    Raises:
        ValueError: If any key is missing or contains invalid values.
    """
    for key, value in ALLOWED_STATES.items():
        try:
            validate_subset(states[key], value)
        except KeyError:
            raise ValueError(errmsg.MISSING_KEY.format(key=key))
        except ValueError:
            raise ValueError(errmsg.INVALID_TYPE_VALUE.format(check_type=key, value=states[key]))
    
def validate_oneof(
        one: Any, 
        of: Iterable[Any], 
        check_type: str
    ) -> Any:
    """
    Validates that a given value exists within a list of allowed values.

    The function attempts to normalize the input value and the list of allowed
    values using internal `_make_comparable` utilities. If a match is found,
    the matched value is returned. Otherwise, a ValueError is raised.

    Args:
        one (Any): The value to validate.
        of (Iterable[Any]): A collection of allowed values.
        type (str): A string representing the type or context for error messaging.

    Returns:
        Any: The matching value from the allowed list, if validation succeeds.

    Raises:
        ValueError: If the input value is not found in the allowed list.
    """
    one = _make_comparable(one)
    of = _make_comparables(of)
    for o in of:
        if one == o:
            return o
    raise ValueError(errmsg.INVALID_TYPE_VALUE.format(check_type=check_type, value=one))

def validate_hand_info_needed(
        dominant_hand: Literal['left', 'right'], 
        task: Literal['avoiding', 'reaching']
    ):
    """Validates that dominant handedness is provided for avoiding task.

    Args:
        dominant_hand (str): Participant's dominant hand.
        task (str): Current task.

    Raises:
        ValueError: If avoiding task and handedness info is missing.
    """
    task = _make_comparable(task)
    if task == 'avoiding' and not dominant_hand:
        raise ValueError(errmsg.NO_DOMINANT_HAND_AVOIDING)
    
def validate_nonempty(sized: Sized, msg: str) -> None:
    """
    Raises an error if the provided object is empty.

    Args:
        sized (Sized): Any object that implements __len__().
        msg (str): Error message to raise if the object is empty.

    Raises:
        ValueError: If the object is empty.
    """
    if len(sized) == 0: raise ValueError(msg)
    
### Private helpers
    
def _make_comparable(a: Any) -> Any:
    """
    Normalizes strings for comparison.

    Args:
        a (Any): Input value.

    Returns:
        Any: Casefolded and stripped string if input is str, else original value.
    """
    return a.casefold().strip() if isinstance(a, str) else a

def _make_comparables(l: List[Any]) -> List[Any]:
    """
    Applies normalization to each element in a list.

    Args:
        l (List[Any]): Input list.

    Returns:
        List[Any]: List of elements where each string is normalized.
    """
    return [_make_comparable(e) for e in l]