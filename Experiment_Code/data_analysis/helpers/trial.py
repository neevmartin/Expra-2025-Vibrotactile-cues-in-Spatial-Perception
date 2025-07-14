import pandas as pd
import numpy as np

from helpers.metadata import TABLET_SIZE, WINDOW_SIZE, PIXEL_RAIL_BOTTOM, PIXEL_RAIL_LEFT

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
    
    def get_start(self, ) -> int:
        return tuple(self[["current_pos_x","current_pos_y"]].iloc[0])

    def get_target(self, ) -> str:
        return tuple(self[["target_pos_x", "target_pos_y"]].iloc[0])
 
    def get_target_in_cm(self, ):
        """@return the normalized distance in cm"""
        x, y = self.get_target()

        return (
            Trial._transform_px_to_cm(x - PIXEL_RAIL_LEFT, 0), 
            Trial._transform_px_to_cm(y - PIXEL_RAIL_BOTTOM, 1)
        )
   
    def get_trajectory_data(self, ): 
        return self[[
            "timestamp",
            "current_pos_x",
            "current_pos_y"
        ]]
    
    def get_trajectory_data_in_cm(self, ): 
        """@return the normalized distance in cm"""

        sx, sy = self.get_start()

        return pd.DataFrame({
            "timestamp": self[["timestamp"]].values.flatten(),
            "current_pos_x": list(map(lambda px: Trial._transform_px_to_cm(px - PIXEL_RAIL_LEFT, 0), self[["current_pos_x"]].values.flatten())),
            "current_pos_y": list(map(lambda px: Trial._transform_px_to_cm(px - PIXEL_RAIL_BOTTOM, 1), self[["current_pos_y"]].values.flatten()))
        })
    
    def get_trajectory_data_normalized(self, ): 
        """@return the normalized distance relative to target distance"""
        # TODO: Target : 1 , starte = 0, dann können wir die trials besser zusammenfassen

        sx, sy = self.get_start()
        tx, ty = self.get_target()

        return pd.DataFrame({
            "timestamp": self["timestamp"].values.flatten(),
            "current_pos_x": list(map(lambda px: (px - sx) / (np.abs(tx) - PIXEL_RAIL_LEFT), self[["current_pos_x"]].values.flatten())),
            "current_pos_y": list(map(lambda px: (px - sy) / (np.abs(ty) - PIXEL_RAIL_BOTTOM), self[["current_pos_y"]].values.flatten()))
        })
    
    @classmethod
    def _transform_px_to_cm(self, px: int, axis: int):
        """Reverses the cm to pixel calculation from the experiment"""

        return (px / WINDOW_SIZE[axis]) * TABLET_SIZE 