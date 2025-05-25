from typing import Literal, Any

import tablet_input as tablet
import gui
from config_loader import ExperimentConfig

from psychopy import core
from psychopy import event
from psychopy.visual import Window

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

class VibrotactileCueExperiment(Experiment):
    """
    Experimental implementation for studying vibrotactile cues in spatial perception.

    This class extends the `Experiment` base class and implements a full behavioral
    experiment in which participants perform either a reaching or avoiding task. 
    Each trial involves tablet input, target initialization, and optional explanations, 
    breaks, or feedback based on the current trial state. If debug mode is enabled
    visual feedback is given. Otherwise participants must rely on vibrotactile cues
    given by the Arduino device.

    The class uses an `ExperimentConfig` loader object to manage the trial structure. 
    Furthermore, the class uses a participant dictionary to store individual data. 

    It defines the spatial layout of start/stop points, target positions,  # TODO: Create a separate loader or use the experiment loader for this.

    and uses `tablet_input.py` for handling input collection.

    Attributes:
        config (ExperimentConfig): 
            The configuration object containing trial structure and parameters.

        participant (dict): 
            Participant-specific metadata or conditions.

        RADIUS (int): 
            Radius of visual target dots, consistent across trials.

        STARTPOS (list[int, int]): 
            Starting point of movement in screen coordinates.

        STOPPOS (list[int, int]): 
            Endpoint of movement in screen coordinates.

        MIN_TARGETDIST (list[int, int]): 
            Minimum distance for placing a target in pixels.

        MAX_TARGETDIST (list[int, int]): 
            Minimum distance for placing a target in pixels.

        target_pos (list[float, float]): 
            Actual position of the target in a trial. 
            It holds MIN_TARGETDIST <= target_pos[1] <= MAX_TARGETDIST.

        current_trial (dict): 
            Metadata of the trial currently running.

        previous_trial (dict): 
            Metadata of the previously run trial.

        state (dict): 
            A dict tracking current phase flags (e.g., explanation, break).

        FEEDBACK_DELAY (float):
            Delay in seconds how long the feedback text should be shown.

        text_confirmed (bool): 
            Tracks whether the participant has acknowledged a text screen.
            Gets updated to `False` every time the participant gets shown a skippable text.

        trial_confirmed (bool): 
            Confirmation of the participant to start/stop a trial/recording.
            Switches twice in a trial. One time to start the tablet stream and data
            collection and one time to end it.

        mouse_pressed_last_frame (bool):
            Variable to hold if mouse was pressed last iteration of the trial loop.
            We need this for confirmation tracking without interrupting the workflow
            of the window flip.

        trial_running (bool): 
            Whether the current trial is actively running.
    """
    config: ExperimentConfig
    participant: dict

    RADIUS: int # TODO: Should the circles be sized differently?

    # Startpoint
    STARTPOS: list[int, int]

    # Endpoint
    STOPPOS: list[int, int]
    
    # Reference point: 'reaching' -> targetpoint, 'avoiding' -> obstacle.
    MIN_TARGETDIST: list[int, int]
    MAX_TARGETDIST: list[int, int]
    target_pos: list[float, float]

    # Global state variables
    current_trial: dict
    previous_trial: dict

    state: dict

    FEEDBACK_DELAY: float

    text_confirmed: bool
    trial_confirmed: bool
    mouse_pressed_last_frame: bool

    trial_running: bool

    def __init__(self, win_config: dict, experiment_config: ExperimentConfig, participant: dict[str, Any], debug: bool = False):
        """
        experiment_config is an `ExperimentConfig` instance managing trial definitions,
            phases, tasks, and parameters loaded from YAML config files. See `config_loader.py` for more info.

        participant must contain:
            - 'participantID' (str): Unique identifier for the participant.
            - 'participant_dir' (str): Directory path for participant-specific data storage.
        """
        super().__init__(win_config, debug)

        self.config = experiment_config
        self.participant = participant

        self.current_trial = None
        self.previous_trial = None

        self.FEEDBACK_DELAY = 2

        self.mouse_pressed_last_frame = False

        self.state = {
            'explanation': False,
            'feedback'   : False,
            'break'      : False
        }

    # ------------------------------------------------------------------------------
    # Meta control flow
    # ------------------------------------------------------------------------------

    def run_introduction(self):
        gui.draw_centered_text(
            self.window, 
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, ' \
            'sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, ' \
            'sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. ' \
            'Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ' \
            'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ' \
            'ut labore et dolore magna aliquyam erat, sed diam voluptua. ' \
            'At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, ' \
            'no sea takimata sanctus est Lorem ipsum dolor sit amet. \n' \
            'Press ENTER to continue.'
        )
        self.window.flip()
        event.waitKeys(keyList=['return'])

    def run_experiment(self) -> None:
        """
        Runs the main experiment.

        Iterates through all remaining trials in the configuration, managing
        task-specific initialization, explanations, breaks, and feedback phases.
        Each trial is initialized and executed, with state updates between trials.

        Each trial the global state is updated. At the beginning of each trial
        necessary hyperparameters like the target position are initialized.
        Depending on the global state different pre- and post- text is used.

        The initialization of task hyperparameters for circle position is lazy
        evaluated such that those only change when the task changes.

        Returns:
            None
        """
        while len(self.config.get_remaining_trials()) > 0:
            self.current_trial = self.config.get_next_trial()

            ### Trial flow

            self.update_state(self.previous_trial, self.current_trial)

            # In case task has changed: give an explanation for the upcoming task.
            # Lazy evaluation of task initialization.
            if self.state['explanation'] == True: 
                if self.current_trial.get('task') == 'avoiding':
                    self.init_avoiding_task()
                    self.give_explanation('avoiding')
                elif self.current_trial.get('task') == 'reaching':
                    self.init_reaching_task()
                    self.give_explanation('reaching')
            # IMPORTANT: The elif ensures that there is no conflict at the end of a phase
            #            Imagine we switch to the training phase. We give an explanation 
            #            of the task and after that give a break. That would not be necessary.     
            elif self.state['break'] == True:
                self.give_break()

            # Input and output streams start here.
            self.init_trial()
            self.run_trial()
            # End of streams here.

            if self.state['feedback'] == True:
                self.give_feedback()
            
            self.previous_trial = self.current_trial

    def run_outro(self):
        gui.draw_centered_text(
           self.window,
           'Thank you for your participation in our study! \n' \
           'Press ENTER to close the experiment window.'
        )
        self.window.flip()
        event.waitKeys(keyList=['return'])

    def handle_keys(self):
        """
        Handles key inputs for the experiment.

        All key events should be processed through this method to ensure consistent
        experiment control, e.g. quitting (Q/Escape) and confirming text prompts (Return).

        For safety call this method whenever you have a while loop for control flow somewhere.

        Returns:
            None
        """
        keys = event.getKeys()

        for key in keys:
            if key == "q" or key == "escape":
                self.exit()
            if key == "return":
                if self.state['explanation'] or self.state['break']:
                    self.text_confirmed = True

    def update_state(self, previous_trial: dict, current_trial: dict) -> None:
        """
        Updates internal state flags based on trial transitions and conditions.

        Args:
            previous_trial (dict): The trial data from the previous trial, or None if first trial.
            current_trial (dict): The trial data for the current trial.

        The state flags updated are:
            - 'explanation': True if this is the first trial or the task type changed.
            - 'feedback': True if the current trial is in the training phase or debug mode is enabled.
            - 'break': True if the block number has increased from the previous to the current trial marking the beginning of a new one.

        Returns:
            None
        """
        self.state['explanation'] = True if previous_trial == None or previous_trial.get('task') != current_trial.get('task')   else False  
        self.state['feedback']    = True if current_trial.get('phase') == 'training' or self.debug                              else False  
        self.state['break']       = True if previous_trial != None and previous_trial.get('block') < current_trial.get('block') else False
    
    # ------------------------------------------------------------------------------
    # Trial control
    # ------------------------------------------------------------------------------

    def init_trial(self) -> None:
        """
        Initializes the trial by setting the target position and starting input tracking.

        Resets trial confirmation and running flag, then starts the tablet input stream.
        In debug mode, enables visible cursor and tracking dot for easier monitoring.

        TODO: 
            Decide whether we need the visible cursor and dot 
            for debug since it is handled in `gui.py`.

        Returns:
            None
        """
        self.init_target(self.current_trial.get('distance'))

        self.trial_confirmed = False
        self.trial_running = True

        if self.debug:
            tablet.start_stream(self.window, cursor_visible=True, dot_visible=True)
        else:
            tablet.start_stream(self.window)

    def run_trial(self) -> None:
        """
        Executes a single trial, handling participant input and updating trial state.

        The method contains two sequential phases:

        1. **Confirmation phase** (`while not self.trial_confirmed`):
        Waits for the participant to confirm readiness (e.g., releasing the mouse button or pressing a key)
        to start the trial and starting data recording stream. During this phase,
        input is monitored and debug info can be drawn if enabled.

        2. **Trial running phase** (`while self.trial_running`):
        Runs the active trial, continuously updating trial data and handling input 
        until the trial ends. Trajectory is drawn if debug mode is active.
        The participant has to confirm once more when they think they reached their destination.
        After confirmation the stream does not get updated anymore.

        The PsychoPy window is updated (`window.flip()`) each iteration to reflect changes.

        Returns:
            None
        """
        while not self.trial_confirmed: # Confirmation phase
            self.handle_keys()

            if self.trial_confirmation():
                self.trial_confirmed = True # e.g. Mouse click

            if self.debug:
                self.draw_debug() # In confirmation phase we only draw setup and not trajectory.

            self.window.flip()
        
        while self.trial_running:
            self.handle_keys()

            self.update_trial() # Data stream and output

            if self.debug:
                self.draw_debug() # Draw trajectory and setup.

            self.window.flip()

    def trial_confirmation(self) -> bool:
        """
        Checks whether the trial confirmation condition has been met.

        Returns True when the participant presses the mouse button in case they have not confirmed the trial yet.
                If they have confirmed the trial method returns true if they release the mouse button again.

        Returns:
            bool: True if the trial is confirmed, False otherwise.
        """
        mouse_pressed = tablet._mouse.getPressed()[0]

        if self.trial_confirmed:
            # Trial is running and participant must release the mouse button.
            confirmed = self.mouse_pressed_last_frame and not mouse_pressed
        else:
            # Trial needs to be confirmed with a button press by the participant.
            confirmed = mouse_pressed and not self.mouse_pressed_last_frame

        self.mouse_pressed_last_frame = mouse_pressed

        return confirmed

    def update_trial(self) -> None:
        """
        Updates trial data from the tablet and checks for trial completion.

        Stops the trial if the confirmation condition is met 
        (e.g., participant releases the mouse button or presses a key).

        TODO: 
            Add output stream. Needs to be either updated continuously or once in the end.
            A pandas dataframe has been shown to improve time complexity in private testing for the latter.
            More to this later if desired.

        Returns:
            None
        """
        tablet.update_stream(self.window)
        ### TODO: Output
        if self.trial_confirmation():
            self.trial_running = False

    # ------------------------------------------------------------------------------
    # Interruption control methods
    # ------------------------------------------------------------------------------

    def give_feedback(self) -> None:
        """
        Displays feedback to the participant based on the last mouse position relative to the target.

        This is a control method that interrupts the experiment flow by entering a
        main loop that uses `handle_keys`, pausing the program to allow the participant 
        to view the feedback.

        Returns:
            None
        """
        last_mouse_info = tablet.get_trajectory()[-1]
        last_mouse_pos  = [last_mouse_info[1], last_mouse_info[2]]

        gui.draw_text_feedback(self.window, self.target_pos, last_mouse_pos)
        self.window.flip()

        start_time = core.getTime()
        while core.getTime() - start_time < self.FEEDBACK_DELAY:
            self.handle_keys()

    def give_explanation(self, task: Literal['avoiding', 'reaching']) -> None:
        """
        Displays a task-specific explanation message and waits for participant confirmation.

        This is a control method that interrupts the normal experiment flow by entering a
        main loop that uses `handle_keys` to process input until the participant confirms.

        Args:
            task (Literal['avoiding', 'reaching']): The task type for which to show the explanation.

        Returns:
            None
        """
        self.text_confirmed = False

        if task == 'avoiding':
            gui.draw_centered_text(self.window, 'Explanation for avoiding. \n Press ENTER to continue.')
        elif task == 'reaching':
            gui.draw_centered_text(self.window, 'Explanation for reaching. \n Press ENTER to continue.')
        else:
            gui.draw_centered_text(self.window, f'Explanation for {task}. \n Press ENTER to continue.')
        self.window.flip()

        while not self.text_confirmed:
            self.handle_keys()
            

    def give_break(self) -> None:
        """
        Displays a break message and waits for participant to take a break and then confirm.

        This is a control method that interrupts the normal experiment flow by entering a
        main loop that uses `handle_keys` to process input until the participant confirms.

        Returns:
            None
        """
        self.text_confirmed = False

        gui.draw_centered_text(self.window, 'Eile mit Weile. \n Press ENTER to continue.')
        self.window.flip()

        while not self.text_confirmed:
            self.handle_keys()

    # ------------------------------------------------------------------------------
    # Debug functions
    # ------------------------------------------------------------------------------

    def draw_debug(self) -> None:
        """
        Renders debugging information on the screen.

        Displays the current mouse position, movement trajectory (if trial is confirmed),
        and key trial parameters such as start position and target position as well as the rails.

        TODO:
            We need figure out whether we need visual feedback about the stop position for testing.

        Returns:
            None
        """
        mouse_pos = tablet._mouse.getPos()
        trajectory = tablet.get_trajectory() if self.trial_confirmation else []
        gui.draw_debug_screen(
            win=self.window, 
            trajectory=trajectory, 
            mouse_pos=mouse_pos, 
            start_pos=self.STARTPOS, 
            target_pos=self.target_pos, 
            radius=self.RADIUS
        )
    
    # ------------------------------------------------------------------------------
    # Setup initilizations
    # ------------------------------------------------------------------------------
    
    def init_target(self, percent_distance) -> None:
        """
        Initializes the target position based on a percentage distance.

        The input `percent_distance` represents the target location as a percentage 
        of the total possible distance (0 to 100). It is converted to a relative 
        value between 0 and 1, which is then translated into an absolute pixel 
        position along the Y-axis. 
        
        As a reference we use the maximum and minimum target distance allowed.

        Args:
            percent_distance (float): Target distance as a percentage (0–100).

        Returns:
            None
        """
        relative_distance = percent_distance * .01

        target_posX = self.STARTPOS[0]
        target_posY = self.MIN_TARGETDIST + self.MAX_TARGETDIST * relative_distance

        self.target_pos = [target_posX, target_posY]

    def init_reaching_task(self) -> None:
        """
        Sets up parameters for the 'reaching' task.

        Initializes radius, start and stop positions based on window size,
        and calculates minimum and maximum target distances along the Y-axis.

        TODO:
            We should decide on a loader class for this info.
            Possibly we could update the experiment config loader for this. 

        Returns:
            None
        """
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [win_midX, -win_size[1]/4]
        self.STOPPOS   = [win_midX, win_size[1]/4]

        self.MIN_TARGETDIST = self.STARTPOS[1]
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1]

    def init_avoiding_task(self) -> None:
        """
        Sets up parameters for the 'avoiding' task.

        Initializes radius, start and stop positions based on window size,
        and calculates minimum and maximum target distances along the Y-axis.

        TODO:
            We should decide on a loader class for this info.
            Possibly we could update the experiment config loader for this. 

        Returns:
            None
        """
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [win_midX, -win_size[1]/4]
        self.STOPPOS   = [win_midX, win_size[1]/4]

        self.MIN_TARGETDIST = self.STARTPOS[1]
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1]