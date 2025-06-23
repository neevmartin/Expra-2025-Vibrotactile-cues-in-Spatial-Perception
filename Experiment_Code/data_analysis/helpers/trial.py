import pandas as pd

class Trial(pd.DataFrame):
    """This class serves as a wrapper for dataframes to hide the uggliness of data access"""

    def __init__(self, df: pd.DataFrame):
        super().__init__(data = df)

    def print_short(self, ):
        return f"Trial: {self.get_trial_index()}, Task: {self.get_task()}, Mapping: {self.get_mapping()}"

    def get_participant_id(self, ) -> str:
        return str(self[["participant_id"]].iloc[0].iloc[0])
        
    def get_trial_index(self, ) -> int:
        return int(self[["trial_index"]].iloc[0].iloc[0])
        
    def get_task(self, ) -> str: 
        return str(self[["task"]].iloc[0].iloc[0])
        
    def get_mapping(self, ) -> str:
        return str(self[["mapping"]].iloc[0].iloc[0])
        
    def get_phase(self, ) -> str:
        return str(self[["phase"]].iloc[0].iloc[0])
    
    def get_block(self,) -> int:
        return int(self[["block"]].iloc[0].iloc[0])
    
    def get_target(self, ) -> str:
        return tuple(self[["target_pos_x", "target_pos_y"]].iloc[0])
    
    def get_trajectory_data(self, ): 
        return self[[
            "timestamp",
            "current_pos_x",
            "current_pos_y",
            "left_button_pressed",
            "middle_button_pressed",
            "right_button_pressed"
        ]]