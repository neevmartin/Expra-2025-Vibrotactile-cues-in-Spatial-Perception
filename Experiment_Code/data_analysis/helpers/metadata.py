"""
Metadatabase where we can store important information about our experiment.
Please do only use immutable datatypes and document your additions.
"""

PIXEL_DISTANCES = (-564.89, -342.64, -120.39, 101.86, 324.12, 558.71, 768.62)
"""
Y coordinate distances on the tablet from low to high 
in pixels which are the classes for each intensity.
"""

PERCENT_INTENSITIES = (28, 40, 52, 64, 76, 88, 100)
"""
Percent intensities played by the Arduino from low to high 
which are the classes for each distance.
"""

PIXEL_RAIL_BOTTOM = -807
"""
Start of the rail in pixels from where the participant could start to draw. This is a y coordinate.
"""

PIXEL_RAIL_TOP = 901
"""
End of the rail in pixels where the participant must stop to draw. This is a y coordinate.
"""

PIXEL_RAIL_LEFT = -37
"""
Left rail edge in pixels. This is an x coordinate.
"""

PIXEL_RAIL_RIGHT = 44
"""
Right rail edge in pixels. This is an x coordinate.
"""

PIXEL_RAILWAY_WIDTH = abs(PIXEL_RAIL_LEFT - PIXEL_RAIL_RIGHT)
"""
Width of the railway in pixels.
"""

AVOIDING_THRESHOLD = 0.8
"""
Ratio of the rail width starting from the rail opposite to the participant's dominant hand.
Decides in the avoiding task when the movement to the opposite rail counts as 'avoiding'. 
"""

PIXEL_FROM_RAIL_CONFIRM_DISTANCE = PIXEL_RAILWAY_WIDTH * AVOIDING_THRESHOLD
"""
Length from rail opposite to the dominant hand of the participant. If exceeded
the participant has confirmed their avoiding action.
"""

TABLET_SIZE = 31.1
"""
The size of the drawable space on the tablet
"""

WINDOW_SIZE = 1080, 1920
"""
The size of the psychopy window
"""