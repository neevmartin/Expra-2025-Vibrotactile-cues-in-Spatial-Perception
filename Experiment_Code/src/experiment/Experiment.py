from psychopy.visual import Window
from psychopy import core
from typing import Any

class Experiment:
    """
    Base class for psychophysical experiments using PsychoPy.

    This class provides a general framework for running experiments that involve
    a full experimental pipeline including introduction to experiment, main experiment logic,
    and outro/acknowledgement. Further, it sets up the PsychoPy visual Windows.

    Subclasses should override `run_introduction`, `run_experiment`, and 
    `run_outro` methods to define specific experimental behavior.

    Attributes:
        window (Window): The PsychoPy visual window used for stimulus presentation.
        debug (bool): Whether to run in debug mode (affects verbosity or behavior in subclasses).

    Args:
        win_config (dict): A dictionary containing window configuration parameters. Must include:
            - 'screenID' (int): The screen number to display the window on.
            - 'resolution' (tuple[int, int]): The resolution of the window in pixels.
            - 'windowed' (bool): Whether to use windowed mode (as opposed to fullscreen).
        debug (bool, optional): Flag to enable debug mode. Defaults to False.

    Note:
        A short delay (core.wait(0.1)) is added after window creation to ensure the
        graphics context is fully initialized before use, avoiding platform-specific
        rendering issues.
    """

    window: Window
    debug: bool

    def __init__(self, win_config: dict[str, Any], debug: bool = False):
        """
        win_config must contain:
            - screenID (int)
            - resolution (tuple[int, int])
            - windowed (bool)
        """
        self.window = Window(
            screen=win_config['screenID'],
            size=win_config['resolution'],
            units="pix",
            colorSpace = "rgb255",
            color = (128,128,128),
            fullscr=not win_config['windowed'] # 'windowed' == True corresponds to a fullscreen which is counterintuitive
        )
        self.debug = debug

        core.wait(0.1) # avoid rendering issues

    def run(self) -> None:
        """
        Executes the full experiment lifecycle.

        This method sequentially runs the introduction, main experiment routine, and 
        outro phases of the experiment, followed by cleanup and termination. Each of 
        these phases is implemented as a separate method, which can be overridden by 
        subclasses to define custom behavior.

        The default implementation assumes that:
            - `run_introduction()` presents instructions or a welcome screen.
            - `run_experiment()` runs the core trial logic or stimuli presentation as well as data collection.
            - `run_outro()` provides final messages, feedback, or a debriefing.
            - `exit()` handles window closing and quitting PsychoPy.

        This method is the main entry point for executing the experiment from start to finish.

        Returns:
            None
        """
        self.run_introduction()
        self.run_experiment()
        self.run_outro()
        self.exit()

    def exit(self) -> None:
        """
        Closes the PsychoPy window and exits the experiment.

        This method handles cleanup by closing the display window and terminating 
        the PsychoPy core event loop.

        Returns:
            None
        """
        self.window.close()
        core.quit()

    def run_introduction(self) -> None:
        """
        Runs the introduction phase of the experiment.

        Intended to be overridden by subclasses to provide experiment-specific instructions or setup.

        Returns:
            None
        """
        pass

    def run_experiment(self) -> None:
        """
        Runs the main experimental procedure.

        This method should be implemented by subclasses to execute the sequence of trials,
        manage experiment flow, and handle any task-specific logic.

        Returns:
            None
        """
        pass
    
    def run_outro(self) -> None:
        """
        Runs the closing phase of the experiment.

        Intended to be overridden by subclasses to provide experiment-specific debriefing or cleanup.

        Returns:
            None
        """
        pass