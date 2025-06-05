from psychopy import visual, event, core
import numpy as np

def draw_centered_image(win, image_path):
    """
    Display an image centered on the screen, scaled to fit the window width
    while keeping the original aspect ratio.

    Parameters:
    - win: the window we are working on
    - image_path: path to the image file (e.g., 'images/photo.jpg')
    """
    temp_image = visual.ImageStim(win, image=image_path, units='pix')
    original_size = temp_image.size
    image_aspect = original_size[1] / original_size[0]

    win_width, win_height = win.size

    scaled_width = win_width
    scaled_height = scaled_width * image_aspect

    image = visual.ImageStim(
        win,
        image=image_path,
        units='pix',
        size=(scaled_width, scaled_height),
        pos=(0, 0),
        interpolate=True
    )

    image.draw()

def draw_centered_text(win: visual.Window, text: str, text_color: tuple = (1, 1, 1)):
    """
    Displays centered text on the screen.
    Args:
        win: the window we are working on
        text: the text to display
        text_color: the color of the text
    """
    text = visual.TextStim(win, text=text, pos=(0, 0), color=text_color)
    text.draw()

def draw_debug_screen(win: visual.Window, trajectory: list, mouse_pos: tuple,
                      start_pos: tuple, target_pos: tuple, radius: int):
    """
    Displays the rails, start position, target position, trajectory, mouse when in debug mode
    Args:
        win: the window we are working on
        trajectory: the trajectory up until now
        mouse_pos: the current mouse position
        start_pos: the start position
        target_pos: the target position
        radius: the radius of the circle representing the start, target, stop positions
    """
    my_cursor = visual.Circle(win, pos=mouse_pos, radius=10, fillColor='red', lineColor='red')

    # The positions and size of the rails TO BE CHANGED LATER
    rail_left = visual.Rect(win, width=30, height=200, units="pix", pos=[-50, 0])
    rail_right = visual.Rect(win, width=30, height=200, units="pix", pos=[50, 0])

    start = visual.Circle(win, radius=radius, pos=start_pos, fillColor='black')
    target = visual.Circle(win, radius=radius, pos=target_pos, fillColor='black')

    rail_left.draw()
    rail_right.draw()

    start.draw()
    target.draw()

    if len(trajectory) > 0:
        drawn_line = [(x, y) for (_, x, y, _, _, _) in trajectory]
        line = visual.ShapeStim(win, vertices=drawn_line, closeShape=False, lineColor='black', lineWidth=10)
        line.draw()

    my_cursor.draw()

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
        color = (-1, 1, -1)
    elif target_pos[1] > stop_pos[1]:
        text = "You were undershoot by distance = " + off_point
        color = (1, -1, -1)
    else:
        text = "You were overshoot by distance = " + off_point
        color = (1, -1, -1)

    draw_centered_text(win, text, color)