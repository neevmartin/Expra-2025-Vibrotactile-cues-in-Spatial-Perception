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

def draw_rails(win: visual.Window, color: str):
    """
    Draw the two rails with the given color
    Args:
        win: the window we are working on
        color: the color of the rails
    """
    # Only runs correctly with the monitor
    tablet_size = 31.1
    rail_left = visual.Rect(win, width=0.5 / tablet_size * win.size[1], height=28 / tablet_size * win.size[1],
                            units="pix", pos=[-1 / tablet_size * win.size[1], 0.5 / tablet_size * win.size[1]],
                            color=color, colorSpace='rgb')
    rail_right = visual.Rect(win, width=0.5 / tablet_size * win.size[1], height=28 / tablet_size * win.size[1],
                             units="pix", pos=[1 / tablet_size * win.size[1], 0.5 / tablet_size * win.size[1]],
                             color=color, colorSpace='rgb')

    rail_left.draw()
    rail_right.draw()


def draw_debug_screen(win: visual.Window, trajectory: list, mouse_pos: tuple,
                      start_pos: tuple, stop_pos: tuple, radius: int, obstacle: tuple = None):
    """
    Displays the rails, start position, target position, trajectory, mouse when in debug mode
    Args:
        win: the window we are working on
        trajectory: the trajectory up until now
        mouse_pos: the current mouse position
        start_pos: the start position
        stop_pos: the target position
        radius: the radius of the circle representing the start, target, stop positions
        obstacle: the position of the obstacle
    """
    my_cursor = visual.Circle(win, pos=mouse_pos, radius=10, fillColor='red', lineColor='red', colorSpace='rgb')

    start = visual.Circle(win, radius=radius, pos=start_pos, fillColor='black', colorSpace='rgb')
    stop = visual.Circle(win, radius=radius, pos=stop_pos, fillColor='black', colorSpace='rgb')

    if obstacle:
        obstacle = visual.Circle(win, radius=radius, pos=obstacle, fillColor='yellow', colorSpace='rgb')
        obstacle.draw()

    draw_rails(win, 'white')
    start.draw()
    stop.draw()

    if len(trajectory) > 0:
        drawn_line = [(x, y) for (_, x, y, _, _, _) in trajectory]
        line = visual.ShapeStim(win, vertices=drawn_line, closeShape=False, lineColor='black', lineWidth=10, colorSpace='rgb')
        line.draw()

    my_cursor.draw()

def draw_text_feedback(win: visual.Window, target_pos: tuple, stop_pos: tuple, task: str):
    """
    Calculates the distance to the expected target and displays this as a feedback
    Args:
        win: the window we are working on
        target_pos: the expected position of the target
        stop_pos: the actual position of the participant
        task: the current task, avoiding or reaching
    """
    off_point = np.abs(target_pos[1] - stop_pos[1])
    delta = target_pos[1] - stop_pos[1]

    # Only runs correctly with the monitor
    tablet_size = 31.1
    threshold_green = 0.5/tablet_size * win.size[1]
    threshold_yellow = 4/tablet_size * win.size[1]

    if task == "reaching":
        if off_point < threshold_green:
            text = "You hit the target!"
            color = (-1, 1, -1)
        elif off_point < threshold_yellow:
            if delta < 0:
                text = "You slightly overshot the target!"
                color = (1, 1, -1)
            else:
                text = "You slightly undershot the target!"
                color = (1, 1, -1)
        else:
            text = "You completely missed the target!"
            color = (1, -1, -1)
            
    else:
        if off_point < threshold_green:
            text = "You avoided the obstacle successfully!"
            color = (-1, 1, -1)
        elif off_point < threshold_yellow:
            if delta > 0:
                text = "You avoided the obstacle too early!"
                color = (1, 1, -1)
            else:
                text = "You hit the obstacle!"
                color = (1, 1, -1)
        else:
            if delta > 0:
                text = "You avoided the obstacle way too early!"
                color = (1, -1, -1)
            else:
                text = "You hit the obstacle real bad!"
                color = (1, -1, -1)

    draw_centered_text(win, text, color)