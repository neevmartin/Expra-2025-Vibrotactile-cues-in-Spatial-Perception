import os
import glob
from trial import Trial
import pandas as pd

class Participant():
    """
    Represents a single participant with all data
    """

    def __init__(self, trials: list[Trial]):
        self.__trials: Trial = trials

    def __iter__(self, ):
        """@return iterator object to iterate over the trials of a participant"""
        return PartipantIterator(self.__trials)

    def get_as_one_dataframe(self) -> Trial:
        """@return all trials concatinated to a single data frame"""
        return pd.concat(self.__trials)
    
    def get_trial_count(self) -> int:
        """@return the ammount of trials"""
        return len(self.__trials)

    def get_trial(self, i:int) -> Trial:
        """@return trial at index i"""
        return self.__trials[i]


    @staticmethod    
    def load_participant(folder: str) -> object:
        """
        Loads all trials of a participant and retruns a participant object

        @param folder The folder containing the trials as csv files
        @retrun Participant object containing all data of participant
        """

        if not os.path.exists(folder):
            raise FileNotFoundError(f"The given folder {folder} does not exist")
        

        return Participant(list(map(lambda file: Trial(pd.read_csv(file)), glob.iglob(f'{folder}/*'))))
    

class PartipantIterator():
    """
    This class represents a iterator object to iterate over the participants trials
    """

    def __init__(self, trials):
        self.__trials = trials
        self.__index = 0

    def __next__(self,):
        if self.__index == len(self.__trials):
            raise StopIteration
        
        
        trial = self.__trials[self.__index]
        self.__index += 1
        return trial