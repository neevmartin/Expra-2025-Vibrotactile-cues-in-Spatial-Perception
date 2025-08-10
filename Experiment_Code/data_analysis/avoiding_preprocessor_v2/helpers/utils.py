import pandas as pd
import helpers.metadata as meta

def pixel_to_cm_on_tablet(px: int | pd.Series, axis: int):
    """
    Reverses the cm to pixel calculation from the experiment
    @param px:  The number of pixels
    @param axis: 0 = width, 1 = height
    """        
    if axis == 0:
        return ((px - meta.PIXEL_RAIL_LEFT) / (meta.PIXEL_RAIL_RIGHT - meta.PIXEL_RAIL_LEFT)) * meta.RAIL_WIDTH_CM
    elif axis == 1:
        return ((px - meta.PIXEL_RAIL_BOTTOM) / meta.WINDOW_SIZE[axis]) * meta.TABLET_SIZE 
    else:
        raise ValueError(f"Axis {axis} invalid. Should be either 0 or 1.")