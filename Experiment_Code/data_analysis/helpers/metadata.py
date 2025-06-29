"""
Metadatabase where we can store important information about our experiment.
Please do only use immutable datatypes and document your additions.
"""

PIXEL_DISTANCES = (-564.89, -342.64, -120.39, 101.86, 324.12, 558.71, 768.62)
"""
Pixel distances on the tablet from low to high 
which are the classes for each intensity.
"""

PERCENT_INTENSITIES = (28, 40, 52, 64, 76, 88, 100)
"""
Percent intensities played by the Arduino from low to high 
which are the classes for each distance.
"""

PIXEL_RAIL_BOTTOM = -807
"""
Start of the rail in pixels from where the participant could start to draw.
"""

PIXEL_RAIL_TOP = 901
"""
End of the rail in pixels where the participant must stop to draw.
"""