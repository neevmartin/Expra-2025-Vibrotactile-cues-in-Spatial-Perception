import pandas as pd

class Trial(pd.DataFrame):
    """This class serves as a wrapper for dataframes to hide the uggliness of data access"""

    def __init__(self, df: pd.DataFrame):
        super().__init__(data = df)

    def get_participant_id(self, ):
        return self[["participant_id"]].iloc[0]
        
    def get_trial_index(self, ):
        return self[["trial_index"]].iloc[0]
        
    def get_task(self, ): 
        return self[["task"]].iloc[0]
        
    def get_mapping(self, ):
        return self[["mapping"]].iloc[0]
        
    def get_phase(self, ):
        return self[["phase"]].iloc[0]
    
    def get_block(self,):
        return self[["block"]].iloc[0]
    
    def get_target(self, ):
        return self[["target_pos_x", "target_pos_y"]].iloc[0]
    
    def get_trajectory_data(self, ): 
        return self[[
            "timestamp",
            "current_pos_x",
            "current_pos_y",
            "left_button_pressed",
            "middle_button_pressed",
            "right_button_pressed"
        ]]