from warnings import warn

def condition_warning(condition: str):
    """
    Issues a runtime warning for an invalid experimental condition values.

    Experimental conditions can be:
        - 'rd' (reaching direct)
        - 'ri' (reaching reversed)
        - 'ad' (avoiding direct)
        - 'ai' (avoiding reversed)

    Args:
        condition (str): The condition value that triggered the warning.
    """
    warn(f"Found invalid condition '{condition}'. Ignoring it.", RuntimeWarning)

def not_yet_implemented_warning(to_be_implemented: str):
    """
    Issues a runtime warning for a feature that is not yet implemented.

    Args:
        to_be_implemented (str): A description or name of the feature that is pending implementation.
    """
    warn(f"TODO: '{to_be_implemented}' not yet implemented.", RuntimeWarning)