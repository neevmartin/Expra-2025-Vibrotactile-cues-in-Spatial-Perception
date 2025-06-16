import os
import time

from typing import Literal, Any
from warnings import warn

import src.io.tablet_input as tablet
import src.io.gui as gui
from src.config.config_loader import ExperimentConfig
from src.io.vibration_controller import VibrationController
from src.experiment.Experiment import Experiment

import numpy as np
from psychopy import core
from psychopy import event
from psychopy.visual import Window
from psychopy.clock import Clock




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

        vibrator (VibrationController):
            Controller for the arduino board. Used for playing cues and closing Arduino.

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

        clock (Clock):
            The clock keeps track of the time that has passed 
            since the start of the experiment / run_experiment has been called.

        last_trial_time (float):
            Time since last task phase has started.
            Is used to determine the length of the 
            trial and keeping track of the 10ms we 
            collect the data.

        TRIAL_START_TEXT_INTERVAL (flaot):
            Specifies the time for the 'Trial starts.' text shown in the
            beginning of each trial in seconds. This is not the PTI!

        CUE_INTERVAL (float):
            Specifies the time for each vibrotactile cue.
            Timing is (roughly) specified to match the participant's JND.

        OUTPUT_INTERVAL (float):
            The interval in seconds after which we record the new output data
            that is the mouse position and time as well as metadata.

        FEEDBACK_INTERVAL(float):
            Interval in seconds how long the feedback text should be shown.

        PTI (float):
            The pre trial interval in seconds.
            Is used before cue is being played.    

        ITI (float):
            The inter trial interval in seconds.
            Is used after feedback has been given.

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

        TUTORIAL_TRIAL_NUMBER (int):
            Represents the number of tutorial trials we show 
            the participants in the beginning of the experiment.

        break_index (int):
            The index for the current break number.
            Is used to iterate through possible break
            messages.
    """
    config: ExperimentConfig
    participant: dict
    vibrator: VibrationController

    RADIUS: int # TODO: Should the circles be sized differently?

    # Startpoint
    STARTPOS: list[int, int]

    # Endpoint
    STOPPOS: list[int, int]

    # Padding for start and end point distance to target
    TARGET_PADDING: int
    
    # Reference point: 'reaching' -> targetpoint, 'avoiding' -> obstacle.
    MIN_TARGETDIST: list[int, int]
    MAX_TARGETDIST: list[int, int]
    target_pos: list[float, float]

    # Global state variables
    current_trial: dict
    previous_trial: dict

    state: dict

    clock: Clock
    last_trial_time: float
    TRIAL_START_TEXT_INTERVAL: float
    CUE_INTERVAL: float
    OUTPUT_INTERVAL: float
    FEEDBACK_INTERVAL: float
    PTI: float
    ITI: float

    text_confirmed: bool
    trial_confirmed: bool
    mouse_pressed_last_frame: bool
    right_button_pressed_last_frame: bool

    trial_running: bool
    TUTORIAL_TRIAL_NUMBER: int

    break_index: int

    AVOID_CONFIRM_RATIO: float
    MAX_CONFIRM_DISTANCE: int

    TABLET_SIZE: float

    slides: dict

    def __init__(
            self, win_config: dict, 
            experiment_config: ExperimentConfig, 
            participant: dict[str, Any], 
            vibration_controller: VibrationController = None, 
            debug: bool = False,
            slides: dict = None 
        ):
        """
        experiment_config is an `ExperimentConfig` instance managing trial definitions,
            phases, tasks, and parameters loaded from YAML config files. See `config_loader.py` for more info.

        participant must contain:
            - 'participantID' (str): Unique identifier for the participant.
            - 'participant_dir' (str): Directory path for participant-specific data storage.
        """
        super().__init__(win_config, debug)

        self.config = experiment_config
        self.vibrator = vibration_controller
        self.participant = participant

        self.TABLET_SIZE    = 31.1
        self.TARGET_PADDING = int(2.5 / self.TABLET_SIZE * self.window.size[1])

        self.current_trial = None
        self.previous_trial = None

        # During the whole experiement the standard mouse-cursor is invisible
        event.Mouse().setVisible(False)

        self.clock = Clock()
        # Time in seconds
        self.TRIAL_START_TEXT_INTERVAL = 0.3
        self.CUE_INTERVAL = 0.2 # as suggested by literature
        self.OUTPUT_INTERVAL = 0.01
        self.FEEDBACK_INTERVAL = 1
        self.PTI = 0.5
        self.ITI =  0.2

        self.text_confirmed = False
        self.trial_confirmed = False
        self.mouse_pressed_last_frame = False
        self.right_button_pressed_last_frame = False

        self.TUTORIAL_TRIAL_NUMBER = 10

        self.break_index = 0

        self.AVOID_CONFIRM_RATIO = 0.8
        self.MAX_CONFIRM_DISTANCE = 20

        self.state = {
            'explanation': False,
            'feedback'   : False,
            'break'      : False
        }

        self.slides = slides

    # ------------------------------------------------------------------------------
    # Meta control flow
    # ------------------------------------------------------------------------------

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

        if self.right_button_pressed():
            self.text_confirmed = True

    def wait_confirm(self) -> None:
        """
        Waits until the participant confirms by pressing the designated confirmation key.

        Has side effects and ensures global integration of key handler.

        Returns:
            None
        """
        self.text_confirmed = False
        while not self.text_confirmed:
            self.handle_keys()

    def wait_time(self, time: float) -> None:
        """
        Waits until the given time in seconds is up.

        Has side effects and ensures global integration of key handler.

        Args:
            time (float): The time to be waited for in seconds.

        Returns:
            None
        """
        t = self.clock.getTime()
        while self.clock.getTime() - t < time:
            self.handle_keys()

    def show_text_prompt(self, text: str) -> None:
        """
        Shows a text in the middle of the screen.
        Waits for participant to confirm that text.
        Window gets flipped.

        TODO: This method needs to be adjusted to the later implementation 
              of the show text which are images instead of TextStimuli objects.

        Returns:
            None
        """
        gui.draw_centered_text(
            win=self.window, 
            text=text
        )
        self.window.flip()
        self.wait_confirm()

    def show_image_prompt(self, image_path: str) -> None:
        """
        Shows an image in the middle of the screen.
        Waits for participant to confirm that image.
        Window gets flipped.

        TODO: This method needs to be adjusted to the later implementation 
                of the show text which are images instead of TextStimuli objects.

        Returns:
            None
        """
        gui.draw_centered_image(
            win=self.window, 
            image_path=image_path
        )
        self.window.flip()
        self.wait_confirm()

    def run_introduction(self):
        self.run_explanation_sequence(self.slides.get("INTRODUCTION"))

    def run_experiment(self) -> None:
        """
        Runs the main experiment.

        Starts the clock in the beginning of the experiment.

        Iterates through all remaining trials in the configuration, managing
        task-specific initialization, explanations, breaks, and feedback phases.
        Each trial is initialized and executed, with state updates between trials.

        Each trial the global state is updated. At the beginning of each trial
        necessary hyperparameters like the target position are initialized.
        Depending on the global state different pre- and post- text is used.

        The initialization of task hyperparameters for circle position is lazy
        evaluated such that those only change when the task changes.

        Important side-effect:
            Function automatically closes connected Arduino board
            when all trials are done.

        Returns:
            None
        """
        self.run_tutorial()
        # Init
        self.clock.reset()
        # Trial sequence
        while len(self.config.get_remaining_trials()) > 0:
            self.current_trial = self.config.get_next_trial()

            ### Phase control

            self.update_state(self.previous_trial, self.current_trial)

            # In case task has changed: give an explanation for the upcoming task.
            # Lazy evaluation of task initialization.
            if self.state['explanation'] == True:
                current_task = self.current_trial.get('task')
                current_phase = self.current_trial.get('phase')

                if current_task == 'avoiding':
                    self.init_avoiding_task()
                elif current_task == 'reaching':
                    self.init_reaching_task()

                # We give a custom explanation sequence based on meta data
                self.give_explanation(phase=current_phase, task=current_task) 
            # IMPORTANT: The elif ensures that there is no conflict at the end of a phase
            #            Imagine we switch to the training phase. We give an explanation 
            #            of the task and after that give a break. That would not be necessary.     
            elif self.state['break'] == True:
                self.give_break()

            # Input and output streams start here.
            self.init_trial()
            self.run_trial()
            # End of streams here.
            
            self.previous_trial = self.current_trial
        # Clean up
        if self.vibrator != None:
            self.vibrator.close()

    def run_outro(self):
        self.show_text_prompt(
            'Thank you for your participation in our study! \n' \
           'Press the big pen button to close the experiment window.'
        )

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
        self.state['explanation'] = True if previous_trial == None or previous_trial.get('task') != current_trial.get('task') or previous_trial.get('phase') != current_trial.get('phase')  else False  
        self.state['feedback']    = True if current_trial.get('phase') == 'Training' or current_trial.get('phase') == 'Recap' or self.debug else False  
        self.state['break']       = True if previous_trial != None and previous_trial.get('block') < current_trial.get('block') else False
    
    def run_tutorial(self) -> None:
        """
        Runs the interactive tutorial phase of the experiment.

        Steps performed:
            - Hides the mouse cursor.
            - Draws centered instructional text on the experiment window.
            - Waits for the participant to press ENTER to proceed.
            - Executes 10 tutorial trials to familiarize the participant with the experiment flow.

        Returns:
            None
        """
        self.run_explanation_sequence(self.slides["TUTORIAL"])

        task1, task2 = ('avoiding', 'reaching') if self.config.mode == 'avoiding' else ('reaching', 'avoiding')
        explanation_seq1, explanation_seq2 = ((self.slides["TUTORIAL_AVOIDING"], self.slides["TUTORIAL_REACHING"])
                                              if task1 == 'avoiding' 
                                              else (self.slides["TUTORIAL_REACHING"], self.slides["TUTORIAL_AVOIDING"]))

        n = 6
        intensity_list = [30, 30, 30, 100, 100, 100] # in percentage
        assert len(intensity_list) == n
        np.random.shuffle(intensity_list)

        self.run_explanation_sequence(explanation_seq1)

        if task1 == 'avoiding':
            self.init_avoiding_task()
        else:
            self.init_reaching_task()

        for i in range(n):
            self.run_tutorial_trial(intensity_list[i])

        self.run_explanation_sequence(explanation_seq2)

        if task2 == 'avoiding':
            self.init_avoiding_task()
        else:
            self.init_reaching_task()

        for i in range(n):
            self.run_tutorial_trial(intensity_list[i])
        

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

        2. **Task phase** (`while self.trial_running`):
        Runs the active trial, continuously updating trial data and handling input 
        until the trial ends. Trajectory is drawn if debug mode is active.
        The participant has to confirm once more when they think they reached their destination.
        After confirmation the stream does not get updated anymore.

        The PsychoPy window is updated (`window.flip()`) each iteration to reflect changes.

        **One trial follows structure: <br/>
        Cue | Confirmation | Task | (Feedback) | ITI**

        Returns:
            None
        """
        # Wait for participant to return to starting position before proceeding
        self.wait_until_participant_returns_to_start()
        self.vibrotactile_cue() # CUE

        while not self.trial_confirmed: # CONFIRMATION
            self.handle_keys()

            if self.trial_confirmation():
                self.trial_confirmed = True

            if self.debug:
                self.draw_debug()
            
            gui.draw_rails(self.window, "white")

            self.window.flip()
        
        self.last_trial_time = self.clock.getTime()

        last_scan = self.clock.getTime()
        while self.trial_running: # TASK
            self.handle_keys()
            self.update_trial()

            if self.debug:
                self.draw_debug()
                
            
            gui.draw_rails(self.window, "green")
            self.window.flip()

            delta_time = self.config.get_scan_time() - abs(self.clock.getTime() - last_scan)
            if delta_time > 0:
                time.sleep(delta_time)

            last_scan = self.clock.getTime() # use this for output intervals every 10 ms

        if self.state['feedback'] == True: # FEEDBACK
            self.give_feedback()

        self.inter_trial_interval() # ITI

    def run_tutorial_trial(self, intensity_percentage: int):
        """
        Executes a single tutorial trial, handling participant input and updating trial state.

        The method is equivalent with `run_trial` though no data is collected and there is no debug mode.

        **One trial follows structure: <br/>
        Cue | Confirmation | Task | ITI**

        Args:
            intensity_percentage (int): Intensity for the Arduino that should be played.

        Returns:
            None
        """
        # Wait for participant to return to starting position before proceeding
        self.wait_until_participant_returns_to_start()
        self.vibrotactile_cue(intensity_percentage=intensity_percentage) # CUE

        self.trial_confirmed = False
        while not self.trial_confirmed: # CONFIRMATION
            self.handle_keys()

            if self.trial_confirmation():
                self.trial_confirmed = True

            gui.draw_rails(self.window, "white")
            self.window.flip()
        
        self.trial_running = True

        while self.trial_running: # TASK
            self.handle_keys()

            if self.trial_confirmation(): # We do not collect any data in this
                self.trial_running = False

            gui.draw_rails(self.window, "green")
            self.window.flip()

        self.inter_trial_interval() # ITI
        
    def wait_until_participant_returns_to_start(self) -> None:
        """
        Waits until the participant returns to the starting position before proceeding.

        Continuously checks the mouse position and distance from the start position.
        If the distance is less than `MAX_CONFIRM_DISTANCE`, it breaks the loop.
        In debug mode, it draws the start position and rails on the window.

        Returns:
            None
        """
        tablet.start_stream(self.window)
        while True:
            self.handle_keys()
            mouse_info = tablet.get_mouse()
            if mouse_info is not None:
                mouse_pos = mouse_info.getPos()
                distance_from_start = abs(mouse_pos[1] - self.STARTPOS[1])
                if distance_from_start < self.MAX_CONFIRM_DISTANCE:
                    break
            if self.debug:
                # TODO: Maybe we should also draw the start position if we're not in debug mode, to show the participant where to return to?
                gui.draw_start(self.window, self.STARTPOS, self.RADIUS)
            gui.draw_rails(self.window, "white")
            # TODO: Maybe add some text here that tells the participant to return to the start position?
            self.window.flip()

    def vibrotactile_cue(self, intensity_percentage: float = None) -> None:
        """
        Gives vibrotactile cue and safely waits until the cue ends.

        Displays a cue message on the window, 
        activates the vibrator at the current trial's specified intensity for the cue interval, 
        and waits for the cue to end while monitoring for key presses.

        If no vibrator exists, a warning is issued.

        Args:
            intensity_percentage (int | float):
                Optional. If argument is given will take this intensity instead of the current trial intensity.
                As the name suggests this awaits percentages. Careful: values from 0-1 are treated as relative numbers.
                Please just use values >1 for percentages.

        Raises:
            RuntimeWarning: If no Arduino board is detected and the cue cannot be given.
        """
        
        # Cue message (optional)
        gui.draw_centered_text(win=self.window, text='Trial starts.')

        self.window.flip()
        self.wait_time(self.TRIAL_START_TEXT_INTERVAL)

        self.window.flip() # time without text
        self.wait_time(self.PTI)

        # Vibration should succeed before drawing so timing lines up
        if intensity_percentage == None:
            intensity_proportion = 0.01 * self.current_trial.get('intensity')
        else:
            intensity_proportion = 0.01 * intensity_percentage

        if self.vibrator != None:
            self.vibrator.vibrate(intensity=intensity_proportion, duration_sec=self.CUE_INTERVAL)
        else:
            warn('No Arduino board detected - cue suppressed.', category=RuntimeWarning)

        # Safely wait for cue to end
        self.wait_time(self.CUE_INTERVAL)

    def trial_confirmation(self) -> bool:
        """
        Checks whether the trial confirmation condition has been met.

        Returns True when the participant presses the mouse button in case they have not confirmed the trial yet.
                If they have confirmed the trial method returns true if they release the mouse button again.

        Returns:
            bool: True if the trial is confirmed, False otherwise.
        """
        if tablet.get_mouse() is not None:
            mouse_info = tablet.get_mouse()
            mouse_pressed = mouse_info.getPressed()[0]
        else:
            mouse_info = event.Mouse()
            mouse_pressed = mouse_info.getPressed()[0]

        confirmed = False

        # If trial not confirmed yet: any new click starts the trial
        if not self.trial_confirmed:
            confirmed = mouse_pressed and not self.mouse_pressed_last_frame
        # If trial is running: any new click ends the trial
        else:
            confirmed = mouse_pressed and not self.mouse_pressed_last_frame

        self.mouse_pressed_last_frame = mouse_pressed

        return confirmed
    
    def right_button_pressed(self):
        mouse = event.Mouse()
        right_button_pressed = mouse.getPressed()[2]

        pressed = right_button_pressed and not self.right_button_pressed_last_frame

        self.right_button_pressed_last_frame = right_button_pressed

        return pressed

    def update_trial(self) -> None:
        """
        Updates trial data from the tablet and checks for trial completion.

        Calls function to export trial data to a CSV file and updates the tablet input stream.

        Stops the trial if the confirmation condition is met 
        (e.g., participant releases the mouse button or presses a key).


        Returns:
            None
        """
        tablet.update_stream(self.window)
        if self.trial_confirmation():
            self.export_trial_data_all() # Export all data points of the trial.
                
            self.trial_running = False
            
    def export_trial_data_all(self) -> None:
        """
        Exports all trajectory data for the current trial to a CSV file.
        This method retrieves the trajectory data from the tablet, prepares the output CSV file (including writing the header if the file is newly created), and appends all trajectory points for the current trial. Each row in the CSV contains participant and trial metadata, target position, timestamp, current position, and button press states.
        The output file is named 'trial_results.csv' and is saved in the participant's directory as specified in `self.participant['participant_dir']`.
        Returns:
            None
        """
        
        trajectory = tablet.get_trajectory()
        # Prepare output path
        output_path = os.path.join(self.participant.get('participant_dir', '.'), self.__get_filename())

        # Prepare header
        header = [
            'participant_id',
            'trial_index',
            'task',
            'mapping',
            'phase',
            'block',
            'target_pos_x',
            'target_pos_y',
            'timestamp',
            'current_pos_x',
            'current_pos_y',
            'left_button_pressed',
            'middle_button_pressed',
            'right_button_pressed'
        ]

        # Write all trajectory points for this trial
        with open(output_path, 'w') as f:
            f.write(','.join(header) + '\n')
            for entry in trajectory:
                row = [
                    self.participant.get('participantID'),
                    self.config.get_trial_index(),
                    self.current_trial.get('task'),
                    self.config.get_mapping_type(),
                    self.current_trial.get('phase'),
                    self.current_trial.get('block'),
                    round(self.target_pos[0], 2),
                    round(self.target_pos[1], 2),
                    round(entry[0], 3),   # timestamp
                    entry[1],             # current_pos_x
                    entry[2],             # current_pos_y
                    entry[3],             # left_button_pressed
                    entry[4],             # middle_button_pressed
                    entry[5],             # right_button_pressed
                ]
                f.write(','.join(str(value) for value in row) + '\n')

    def inter_trial_interval(self) -> None:
        """
        Waits for the duration of the inter-trial interval (ITI), updating the display
        and handling keypresses during the wait. Window gets flipped one time.

        Returns:
            None

        """
        self.window.flip()
        self.wait_time(self.ITI)

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
        trajectory      = tablet.get_trajectory()
        last_mouse_pos = (trajectory[-1][1], trajectory[-1][2])
        confirm_mouse_info = last_mouse_pos if self.current_trial.get('task') == 'reaching' else self.find_exceed_thresh_pos(trajectory)
        confirm_mouse_pos  = [confirm_mouse_info[0], confirm_mouse_info[1]]

        if self.current_trial.get("task") == "avoiding":
            # Seperated because we check for whether they avoided in find_exceed_tresh_pos()
            # and pass that as an argument to draw_text_feedback()
            gui.draw_text_feedback(self.window, self.target_pos, confirm_mouse_pos, self.current_trial.get("task"), confirm_mouse_info[2])    
        else:
            gui.draw_text_feedback(self.window, self.target_pos, confirm_mouse_pos, self.current_trial.get("task"))
        self.window.flip()

        self.wait_time(self.FEEDBACK_INTERVAL)

    def find_exceed_thresh_pos(self, trajectory: list):
        """
        Finds the first x-position in the trajectory that falls below the specified threshold.

        Iterates through trajectory points and returns the x-coordinate of the first point
        where x is less than the threshold.
        If no such point is found, returns STOPPOS.

        Args:
            trajectory (list): List of mouse info tuples/lists where x-coordinate is at index 1.

        Returns:
            float: The x-coordinate that meets the condition or STOPPOS if none found.
        """
        mouse_position = (trajectory[-1][1], trajectory[-1][2]) # returns last recorded mouse position if not exceeding thresh
        for mouse_info in trajectory:
            x = mouse_info[1]
            current_distance = abs(self.STARTPOS[0] - x)
            threshold = abs(self.STARTPOS[0] - self.STOPPOS[0]) * self.AVOID_CONFIRM_RATIO
            if current_distance > threshold:
                return (mouse_info[1], mouse_info[2], False)
        
        
        return (mouse_position[0], mouse_position[1], True) # Return whether they switched lanes

    def give_explanation(
            self, 
            phase: Literal['Pre-Test', 'Training', 'Post-Test', 'Recap'], 
            task: Literal['avoiding', 'reaching']
        ) -> None:
        """
        Displays a task-specific explanation message sequence and waits for participant confirmation for each text slide.

        This is a control method that interrupts the normal experiment flow by entering a
        main loop that uses `handle_keys` to process input until the participant confirms.

        Args:
            phase (Literal['Pre-Test', 'Training', 'Post-Test', 'Recap']): The phase type for which to show the explanation.
            task (Literal['avoiding', 'reaching']): The task type for which to show the explanation.

        Returns:
            None
        """
        if self.config.mode == 'avoiding':
            if phase == 'Pre-Test':
                phase_slide_path = self.slides["PRETEST_AVOIDING2"] if task == 'avoiding' else self.slides["PRETEST_AVOIDING1"]
            elif phase == 'Training':
                phase_slide_path = self.slides["TRAINING_AVOIDING"]
            elif phase == 'Post-Test':
                phase_slide_path = self.slides["POSTTEST_AVOIDING1"] if task == 'avoiding' else self.slides["POSTTEST_AVOIDING2"]
            elif phase == 'Recap':
                phase_slide_path = self.slides["RECAP_AVOIDING"]
        # Difference between Group1 & Group2 is the sequence of the tasks which makes the difference here
        elif self.config.mode == 'reaching':
            if phase == 'Pre-Test':
                phase_slide_path = self.slides["PRETEST_REACHING1"] if task == 'avoiding' else self.slides["PRETEST_REACHING2"]
            elif phase == 'Training':
                phase_slide_path = self.slides["TRAINING_REACHING"]
            elif phase == 'Post-Test':
                phase_slide_path = self.slides["POSTTEST_REACHING2"] if task == 'avoiding' else self.slides["POSTTEST_REACHING1"]
            elif phase == 'Recap':
                phase_slide_path = self.slides["RECAP_REACHING"]

        self.run_explanation_sequence(phase_slide_path)

    def run_explanation_sequence(self, image_paths: list) -> None:
        """
        Runs the explanation sequence for a list of image paths.

        Iterates through the provided list of image file paths and displays 
        each image then waits for the confirmation of the participant.

        Args:
            image_paths (list): A list of strings, where each string is the file path to an image.
                                Here it should be an Explanation list value from the enum in `explanation.py`
        
        Returns:
            None
        """
        for p in image_paths:
            self.show_image_prompt(image_path=p)

    def give_break(self) -> None:
        """
        Displays a break message and waits for participant to take a break and then confirm.

        This is a control method that interrupts the normal experiment flow by entering a
        main loop that uses `handle_keys` to process input until the participant confirms.

        Returns:
            None
        """
        self.show_image_prompt(self.slides["BREAK"][self.break_index % len(self.slides["BREAK"])]) # Iterates through all images again and again
        self.break_index += 1

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
        mouse_pos = tablet.get_mouse().getPos()
        trajectory = tablet.get_trajectory() if self.trial_confirmation else []
        current_task = self.current_trial.get('task')
        gui.draw_debug_screen(
            win=self.window, 
            trajectory=trajectory, 
            mouse_pos=mouse_pos, 
            start_pos=self.STARTPOS, 
            stop_pos=self.STOPPOS if current_task == 'avoiding' else self.target_pos,
            radius=self.RADIUS,
            obstacle=self.target_pos if current_task == 'avoiding' else None
        )
    
    # ------------------------------------------------------------------------------
    # Setup initilizations
    # ------------------------------------------------------------------------------
    
    def init_target(self, distance: float) -> None:
        """
        Initializes the target position based on a percentage distance.

        The input `percent_distance` represents the target location as a percentage 
        of the total possible distance (0 to 100). It is converted to a relative 
        value between 0 and 1, which is then translated into an absolute pixel 
        position along the Y-axis. 
        
        As a reference we use the maximum and minimum target distance allowed.

        Args:
            distance (float): Target distance in cm.

        Returns:
            None
        """

        target_posX = self.STARTPOS[0]
        target_posY = distance / self.TABLET_SIZE * self.window.size[1] - self.window.size[1]/2

        self.target_pos = (target_posX, target_posY)

    def init_reaching_task(self) -> None:
        """
        Sets up parameters for the 'reaching' task.

        Initializes radius, start and stop positions based on window size,
        and calculates minimum and maximum target distances along the Y-axis.

        TODO:
            Will possibly changed into one function with `init_avoiding_task`.

        Returns:
            None
        """
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [-0.75/self.TABLET_SIZE*self.window.size[0], -13.15/self.TABLET_SIZE*self.window.size[1]]
        self.STOPPOS   = [0, 0] # Won´t be used

        self.MIN_TARGETDIST = self.STARTPOS[1] + self.TARGET_PADDING
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1] - self.TARGET_PADDING

    def init_avoiding_task(self) -> None:
        """
        Sets up parameters for the 'avoiding' task.

        Initializes radius, start and stop positions based on window size,
        and calculates minimum and maximum target distances along the Y-axis.

        TODO:
            Will possibly changed into one function with `init_reaching_task`.

        Returns:
            None
        """
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [-0.75/self.TABLET_SIZE*self.window.size[0], -13.15/self.TABLET_SIZE*self.window.size[1]]
        self.STOPPOS   = [0.75/self.TABLET_SIZE*self.window.size[0], 14.5/self.TABLET_SIZE*self.window.size[1]]

        self.MIN_TARGETDIST = self.STARTPOS[1] + self.TARGET_PADDING
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1] - self.TARGET_PADDING

    def __get_filename(self) -> str:
        """
        Returns a filename concatinated from the participant id and trial number
        e.g. haml_trial1.csv
        """
        return self.participant.get('participantID') + "_trial" + str(self.config.get_trial_index()) + ".csv"
    