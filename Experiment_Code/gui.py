from psychopy import visual, event, core
import numpy as np

def draw_instruction_text(win: visual.Window, text: str):
    """
    Displays the instruction text on the screen and waits for the user to press Enter
    Args:
        win: the window we are working on
        text: the text to display
    """
    instruction = visual.TextStim(win, text=text, pos=(0, 0))
    instruction.draw()

def draw_debug_screen(win: visual.Window, trajectory: list):
    """
    Displays the debug screen with the last position of the cursor, the two rails and the drawn trajectory
    Args:
        win: the window we are working on
        trajectory: the list of past cursor positions to draw as a line
    """
    cursor_pos = trajectory[-1] # The last position of the cursor
    my_cursor = visual.Circle(win, pos=cursor_pos, radius=10, fillColor='red', lineColor='red')

    # The positions and size of the rails TO BE CHANGED LATER
    rail_left = visual.Rect(win, width=30, height=200, units="pix", pos=[-50, 0])
    rail_right = visual.Rect(win, width=30, height=200, units="pix", pos=[50, 0])

    my_cursor.draw()
    rail_left.draw()
    rail_right.draw()

    line = visual.ShapeStim(win, vertices=trajectory, closeShape=False, lineColor='black', lineWidth=10)
    line.draw()

def draw_visual_feedback(win: visual.Window, start_pos: tuple, target_pos: tuple, stop_pos: tuple, radius: int):
    """
    Displays a feedback screen showing the starting point, the target and where the participant stopped
    Args:
        radius: the radius of the circle representing the points
        win: the window we are working on
        start_pos: the position of the starting point
        target_pos: the position of the target
        stop_pos: the position where the participant stopped
    """
    start = visual.Circle(win, radius=radius, pos=start_pos, fillColor='white')
    target = visual.Circle(win, radius=radius, pos=target_pos, fillColor='white')
    stop = visual.Circle(win, radius=radius, pos=stop_pos, fillColor='blue')

    start.draw()
    target.draw()
    stop.draw()

def draw_text_feedback(win: visual.Window, target_pos: tuple, stop_pos: tuple):
    """
    Calculates the distance to the expected target and displays this as a feedback
    Args:
        win: the window we are working on
        target_pos: the expected position of the target
        stop_pos: the actual position of the participant
    """
    off_point = f"{np.abs(target_pos[1] - stop_pos[1]):.2f}"

    if float(off_point) < 1: # Threshold to be changed later
        text = "You correctly reached the target!"
        color = [-1, 1, -1]
    elif target_pos[1] > stop_pos[1]:
        text = "You were undershoot by distance = " + off_point
        color = [1, -1, -1]
    else:
        text = "You were overshoot by the distance = " + off_point
        color = [1, -1, -1]

    feedback = visual.TextStim(win, text=text, pos=(0, 0), color=color)

    feedback.draw()