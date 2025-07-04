from enum import Enum

"""
Database for all error messages that might occurr during program flow.
Please do only use string constants. If you want to use formatted strings
please write them with braces like below and use .format() to initialise them.
"""

class ErrorMessages(str, Enum):
    """
    Database for all messages that indicate an application-terminating error.
    """
    
    NO_SUBSET_OF_SUPERSET = "Set {sub} is not a subset of {super}."
    
    MISSING_KEY     = "Missing required key in states: '{key}'"

    INVALID_TYPE_VALUE = "Invalid '{check_type}': {value}"

    NO_DOMINANT_HAND_AVOIDING = "Avoiding performance cannot be evaluated when no dominant hand was assigned."

    EMPTY_FILTERING = "Dataframe is empty. It is very likely an impossible state was given leading to disjunct sets in the query." \
                      "Check your queries for such impossible states: e.g. 'Participant mapping is inverse but we select direct'."

class WarningMessages(str, Enum):
    """
    Database for all messages that indicate an application-ignoring warning.
    """

    INVALID_CONDITION_IGNORE = "Found invalid condition '{condition}'. Ignoring it."
