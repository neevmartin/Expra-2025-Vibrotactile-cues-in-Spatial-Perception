# tablet_input.py

from psychopy.event import Mouse
from psychopy.visual import Circle
from psychopy import core

# Globals to hold the stream state
_mouse = None
_dot = None
_clock = None
_trajectory = []

def start_stream(win, cursor_visible=False, dot_visible=False):
    """
    Initialize the mouse input stream, optional red dot, and reset the trajectory.

    Parameters:
    win : psychopy.visual.Window
        The PsychoPy window to associate the mouse input with.
    cursor_visible : bool, optional
        Whether the system (OS) cursor should be visible during tracking. Default is False.
    dot_visible : bool, optional
        Whether to draw a red dot at the tracked position. Default is False.
    """
    global _mouse, _dot, _clock, _trajectory
    _mouse = Mouse(visible=cursor_visible, win=win)
    _clock = core.Clock()
    _trajectory = []

    # Optional: Create a red dot to draw the cursor position
    # if dot_visible:
    #     _dot = Circle(win, radius=5, fillColor='red', lineColor='red')
    # else:
    #     _dot = None

    _dot = None  # Dot disabled by default

def update_stream(win):
    """
    Record the current mouse position, button state, and timestamp.
    Optionally draws the red dot if enabled.

    Parameters:
    win : psychopy.visual.Window
        The PsychoPy window where drawing and tracking occurs.
    """
    global _mouse, _dot, _trajectory
    pos = _mouse.getPos()
    buttons = _mouse.getPressed()
    timestamp = _clock.getTime()
    _trajectory.append((timestamp, *pos, *buttons))

    # Optional: Draw the red dot at the cursor position
    # if _dot:
    #     _dot.pos = pos
    #     _dot.draw()
    #     win.flip()

def get_trajectory():
    """
    Retrieve the collected trajectory data.

    Returns:
    list of tuples
        Each tuple contains (timestamp, x, y, left, middle, right).
    """
    return _trajectory
