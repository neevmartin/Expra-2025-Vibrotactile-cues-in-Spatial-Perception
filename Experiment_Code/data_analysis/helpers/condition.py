import os
import glob
import helpers.warnings as warnings
from helpers.participant import Participant

class Condition():
    """This class represents a single experimental condition containing participants"""

    def __init__(self, group_name:str, participants: list[Participant]):
        self.__participants = participants
        self.__group = group_name

    def __iter__(self, ):
        """@return iterator object to iterate over the participants of a experimental condition with normal loops"""
        return ConditionIterator(self.__participants)
    
    def get_group_name(self, ) -> str:
        """@return the name of the group (rd, ri, ad, ai)"""
        return self.__group
    
    def get_participant_count(self, ) -> int:
        """@return the ammount of participants in the group"""
        return len(self.__participants)
    
    def get_participant_by_index(self, i:int) -> Participant:
        """@return returns a single participant"""
        return self.__participants[i]
    
    @staticmethod
    def load_conditional_groups(folder: str = "../data") -> list:
        """@return tuple of for elements each containing all participants belonging to one experimental condition"""
        
        if not os.path.exists(folder):
            raise FileNotFoundError(f"The given folder {folder} does not exist")
        
        condition_map = {'rd':[], 'ri':[], 'ad':[], 'ai': []}
        for folder in glob.iglob(f'{folder}/*'):
            condition = folder[-2:] #rd, ri, ad, ai

            # Ignores suspicious participant folder endings.
            if condition not in condition_map.keys():
                warnings.condition_warning(condition)
                continue

            condition_map[condition].append(Participant.load_participant(folder))

        return list(map(lambda k_v_pair: Condition(k_v_pair[0], k_v_pair[1]), condition_map.items()))
    
    @staticmethod
    def load_conditional_group(folder: str = "../data", condition: str = "rd") -> object:
        """@return single condition"""

        if not os.path.exists(folder):
            raise FileNotFoundError(f"The given folder {folder} does not exist")
     
        if condition not in ["rd", "ri", "ad", "ai"]:
            raise ValueError("Only condtitions of type ['rd', 'ri', 'ad', 'ai'] allowed")

        participants = []
        for folder in glob.iglob(f'{folder}/*{condition}'):
            participants.append(Participant.load_participant(folder))

        return Condition(condition, participants)

class ConditionIterator():
    """
    This class represents a iterator object to iterate over the participant of a condition
    """

    def __init__(self, participants: Participant):
        self.__participants = participants
        self.__index = 0

    def __next__(self, ) -> Participant:
        if self.__index == len(self.__participants):
            raise StopIteration
        
        
        participant = self.__participants[self.__index]
        self.__index += 1
        return participant
