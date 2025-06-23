import os
import glob
import pandas as pd
from helpers.trial import Trial

class Participant(dict):
    """
    Represents a single participant with all data.
    Inherits from dict and represents the trials in the following structure:

    {
        phase: {
            block: [Trial],
            ...
        },
        ...
    }

    Can be accessed as a dictionary or using the helper methods

    """

    def __init__(self, particpant_id:str, trials: list[Trial]):

        for trial in trials:
            phase = trial.get_phase()
            if phase not in list(self.keys()):
                self[phase] = {}

            block = trial.get_block()
            if block not in list(self[phase].keys()):
                self[phase][block] = []

            self[phase][block].append(trial)
            
        self.__participant_id: str = particpant_id

    def __iter__(self, ):
        """@return iterator object to iterate over the trials of a participant with normal loops"""
        return PartipantIterator(self.get_sorted_list_of_trials())
    
    def __repr__(self):
        """__repr__ is called when you print an object directly"""
        out = "{\n"
        for key_p, item_p in self.items():
            out += f"    {key_p}:" + "{\n"
            for key_b, item_b in item_p.items():
                out += f"        {key_b}: " + str(len(item_b)) + " trials,\n" 
            out += "    },\n"
        out += "}"
        return out

    def get_as_one_dataframe(self, phase=None, block=None) -> Trial:
        """
        Enables fetching data accumulated in a single dataframe for further analysis.
        
        @param phase Gets Data from the specified phase
        @param block Gets Data from the block in the phase. Phase must be specified

        @return All trials concatinated to a single data frame (From a given phase/block)
        """
        
        if phase is None:
            return pd.concat(self.get_sorted_list_of_trials())
        
        phase = self[phase]
        if block is not None:
           return phase[block]
        
        trials = []
        for block in phase.values():
            trials += block

        return trials
    
    def get_trial_count(self) -> int:
        """@return the ammount of trials"""
        count = 0
        for item_p in self.values():
            for item_b in item_p.values():
                count += len(item_b)
        return count

    def get_trial(self, i:int) -> Trial:
        """@return trial at index i"""
        return self.get_sorted_list_of_trials()[i]
    
    def get_participant_id(self, ):
        """@return the participant id (e.g. 11ri)"""
        return self.__participant_id

    def get_phases(self, ):
        """@return get all phases the participant took blocks in"""
        return list(self.keys())
    
    def get_sorted_list_of_trials(self, ):
        """@return get a list of all trials of the participant sorted by the trial number"""
        trials = []
        for item_p in self.values():
            for item_b in item_p.values():
                trials += item_b
        return sorted(trials, key=lambda trial: trial.get_trial_index())

    @staticmethod    
    def load_participant(folder: str) -> object:
        """
        Loads all trials of a participant and retruns a participant object
        Sets the participant id according to the folder name

        @param folder The folder containing the trials as csv files
        @retrun Participant object containing all data of participant
        """

        if not os.path.exists(folder):
            raise FileNotFoundError(f"The given folder {folder} does not exist")
        
        return Participant(folder.split("/")[-1], list(map(lambda file: Trial(pd.read_csv(file)), glob.iglob(f'{folder}/*'))))
        

class PartipantIterator():
    """
    This class represents a iterator object to iterate over the participants trials
    """

    def __init__(self, trials):
        self.__trials = trials
        self.__index = 0

    def __next__(self,) -> Trial:
        if self.__index == len(self.__trials):
            raise StopIteration
        
        
        trial = self.__trials[self.__index]
        self.__index += 1
        return trial