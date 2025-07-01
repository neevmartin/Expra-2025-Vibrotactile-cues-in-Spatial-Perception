from typing import Any, List, Iterable

# Collection of all validation classes we might need

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
    
def validate_oneof(one: Any, of: Iterable[Any], type: str) -> int:
    one = _make_comparable(one)
    of = _make_comparables(of)
    for o in of:
        if one == o:
            return o
    raise ValueError(f'Invalid {type}: \'{one}\'.')

def validate_hand_info_needed(dominant_hand: str, task: str):
    task = _make_comparable(task)
    if task == 'avoiding' and not dominant_hand:
        raise ValueError('Avoiding performance cannot be evaluated when no dominant hand was assigned.')
    
### Private helpers
    
def _make_comparable(a: Any) -> Any:
    if isinstance(a, str): 
        a = a.casefold().strip()
    return a

def _make_comparables(l: List[Any]) -> List[Any]:
    return [_make_comparable(e) for e in l]