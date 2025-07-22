from types import MappingProxyType

"""
Metadatabase where we can store important information about our experiment.
Please do only use immutable datatypes and document your additions.
"""

HANDEDNESS_LITERALS = ('left', 'right')
"""
Constant to check dominant hand inputs.
"""

TASKS = ('avoiding', 'reaching')
"""
Constant to check task inputs.
"""

MAPPINGS = ('direct', 'reversed')
"""
Constant to check mapping inputs.
"""

PIXEL_DISTANCES = (-564.89, -342.64, -120.39, 101.86, 324.12, 558.71, 768.62)
"""
Y coordinate distances on the tablet from low to high 
in pixels which are the classes for each intensity.
"""

CENTIMETER_DISTANCES = (3.92, 7.52, 11.52, 14.72, 18.32, 22.12, 25.52)
"""
Y coordinate distances on the tablet from low to high 
in centimeters which are the classes for each intensity.
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

LEFT_HANDED_PIXEL_AVOIDING_BOUNDARY = PIXEL_RAIL_RIGHT - PIXEL_FROM_RAIL_CONFIRM_DISTANCE
"""
Marks the vertical boundary in pixels for confirming 
the avoiding action in case of a *left* handed participant.
"""

RIGHT_HANDED_PIXEL_AVOIDING_BOUNDARY = PIXEL_RAIL_LEFT + PIXEL_FROM_RAIL_CONFIRM_DISTANCE
"""
Marks the vertical boundary in pixels for confirming 
the avoiding action in case of a *right* handed participant.
data-analysis
"""

TABLET_SIZE = 31.1
"""
The size of the drawable space on the tablet
"""

WINDOW_SIZE = 1080, 1920
"""
The size of the psychopy window
"""

CONFIRM_BUTTON_COLUMN_NAME = 'left_button_pressed'
"""
Column name in the data csvs which denotes 
if the confirmation button has been pressed.
"""

HANDEDNESS = MappingProxyType({
    '1rd': 'left', 
    '2ri': 'right', 
    '3ad': 'right', 
    '4ai': 'right', 
    '5rd': 'right', 
    '6ri': 'right', 
    '7ad': 'right', 
    '8ai': 'right', 
    '9rd': 'right', 
    '10ri': 'right', 
    '11ad': 'right', 
    '12ai': 'right', 
    '13rd': 'right', 
    '14ri': 'right', 
    '15ad': 'right', 
    '16ai': 'right', 
    '17rd': 'right', 
    '18ri': 'right', 
    '19ad': 'right', 
    '20ai': 'right', 
    '21rd': 'right', 
    '22ri': 'right', 
    '23ad': 'right', 
    '24ai': 'right', 
    '25rd': 'right', 
    '26ri': 'right', 
    '27ad': 'right', 
    '28ai': 'right', 
    '29rd': 'right', 
    '30ri': 'right', 
    '31ad': 'right', 
    '32ai': 'right', 
    '33rd': 'right', 
    '34ri': 'right', 
    '35ad': 'right', 
    '36ai': 'right', 
    '37rd': 'right', 
    '38ri': 'right', 
    '39ad': 'right', 
    '40ai': 'right', 
    '41rd': 'left', 
    '42ri': 'right', 
    '43ad': 'right', 
    '44ai': 'right', 
    '45rd': 'right', 
    '46ri': 'right', 
    '47ad': 'right', 
    '48ai': 'right', 
    '49rd': 'right', 
})
"""
Immutable dictionary which contains the handedness for each participant.
The participant ids are the keys for each dominant hand.
"""