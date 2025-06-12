from psychopy import visual, event, core

class Experimental_Setup:
    """
    Class handling participant setup phase of the experiment.

    This setup handles:
    - Participant ID input
    - Experiment mode selection ("Reaching" or "Avoiding")
    - Mapping selection ("Direct" or "Inverse")
    - Display of task-specific instructions

    Designed to run before the experimental trials begin. Uses PsychoPy
    for visual display and input collection.

    Attributes
    ----------
    win : visual.Window
        PsychoPy window used for rendering interface elements.
    participant_id : str
        The entered ID of the participant.
    mode : str
        The selected experiment mode ("Reaching" or "Avoiding").
    mapping : str
        The selected mapping strategy ("direct" or "inverse").

    Methods
    -------
    run() -> dict
        Runs the full setup routine and returns all participant parameters.
    collect_id()
        Prompts for and collects participant ID input from the keyboard.
    select_mode()
        Lets the participant choose between "Reaching" and "Avoiding" task modes.
    select_mapping()
        Lets the participant choose between "Direct" and "Inverse" mapping strategies.
    show_instructions()
        Displays task-specific instructions depending on the selected mode.
    input_params() -> dict
        Returns all participant-related parameters as a dictionary.
    """

   
    def __init__(self, window):
        """
        Initializes the Experimental_Setup instance.

        Parameters: 
            window : visual.Window
                A PsychoPy visual window object used for display.
        """
        self.win = window
        self.participant_id = ""
        self.mode = None
        self.mapping = None


    def input_params(self) -> dict:
        """
        Returns all collected participant parameters.

        Returns
        -------
        dict
            Includes participantID, mode, mapping, and participant_dir.
        """
        return {
            "participantID": self.participant_id,
            "mode": self.mode.lower(),
            "mapping": self.mapping.lower(),
            "participant_dir": f"data/{self.participant_id}"
        }


    def run(self) -> dict:
        """
        Runs the full participant setup process.

        This includes:
            - ID entry
            - Task mode selection
            - Mapping selection
            - Instruction display

        Returns
        -------
        dict
            Dictionary containing all participant parameters.
        """
        self.collect_id()
        self.select_mode()
        self.select_mapping()
        self.show_instructions()
        ##return {
        ##    "participantID": self.participant_id,
        ##    "mode": self.mode.lower(),
        ##    "participant_dir": f"data/{self.participant_id}"
        ##}
        return self.input_params()
    


    def collect_id(self):
        """
        Prompts the participant to enter their ID using the keyboard.

        Displays typed characters in real-time. ENTER confirms input,
        BACKSPACE deletes, and ESC exits the experiment.
        """
        prompt = visual.TextStim(self.win, text="Enter Participant ID:", pos=(0, 100), height=28)
        input_display = visual.TextStim(self.win, text="", pos=(0, 50), height=28)
        info = visual.TextStim(self.win, text="Press ENTER when done", pos=(0, -100), height=20)

        while True:
            prompt.draw()
            input_display.text = self.participant_id
            input_display.draw()
            info.draw()
            self.win.flip()

            keys = event.waitKeys()
            for key in keys:
                if key == "return" and self.participant_id.strip():
                    return
                elif key == "backspace":
                    self.participant_id = self.participant_id[:-1]
                elif key in ["escape", "q"]:
                    core.quit()
                else:
                    self.participant_id += key

    def select_mode(self):
        """
        Displays on-screen buttons to let the participant choose a task mode.

        LEFT arrow → "Reaching" mode  
        RIGHT arrow → "Avoiding" mode  
        ESC or Q exits the program.
        """
        prompt = visual.TextStim(self.win, text="Select Task Mode:\n\nLeft Arrow = Reaching\nRight Arrow = Avoiding", pos=(0, 100), height=26)
        left_label = visual.TextStim(self.win, text="Reaching", pos=(-150, -50), height=22)
        right_label = visual.TextStim(self.win, text="Avoiding", pos=(150, -50), height=22)
        box_left = visual.Rect(self.win, width=200, height=100, pos=(-150, -50), fillColor="lightblue")
        box_right = visual.Rect(self.win, width=200, height=100, pos=(150, -50), fillColor="lightgreen")

        while self.mode is None:
            prompt.draw()
            box_left.draw()
            box_right.draw()
            left_label.draw()
            right_label.draw()
            self.win.flip()

            keys = event.waitKeys()
            for key in keys:
                if key == "left":
                    self.mode = "Reaching"
                elif key == "right":
                    self.mode = "Avoiding"
                elif key in ["escape", "q"]:
                    core.quit()

    def show_instructions(self):
        """
        Displays task-specific instructions based on selected mode.

        Participant must press SPACE to proceed.
        """

        if self.mode.lower() == "reaching":
            text = (
                "----- Reaching Task -----\n\n"
                "In this task, you should REACH the target by moving the pen to the target with the help of the vibrotactile cues\n"
                "Press SPACE to continue."
            )
        else:
            text = (
                "----- Avoiding Task -----\n\n"
                "In this task, you should AVOID hitting the obstacle and reach the target with help of vibrotactile cues.\n"
                "Press SPACE to continue."
            )

        instruction = visual.TextStim(self.win, text=text, height=22, color="white", wrapWidth=1000)
        instruction.draw()
        self.win.flip()
        event.waitKeys(keyList=["space"])
    
    
    
    def select_mapping(self):
        """
        Displays on-screen buttons to let the participant choose a mapping strategy.

        LEFT arrow → "Direct" mapping  
        RIGHT arrow → "Inverse" mapping  
        ESC or Q exits the program.
        """
        prompt = visual.TextStim(self.win, text="Select Mapping:\n\nLeft Arrow = Direct\nRight Arrow = Inverse", pos=(0, 100), height=26)
        left_label = visual.TextStim(self.win, text="Direct", pos=(-150, -50), height=22)
        right_label = visual.TextStim(self.win, text="Inverse", pos=(150, -50), height=22)
        box_left = visual.Rect(self.win, width=200, height=100, pos=(-150, -50), fillColor="lightblue")
        box_right = visual.Rect(self.win, width=200, height=100, pos=(150, -50), fillColor="lightgreen")

        while self.mapping is None:
            prompt.draw()
            box_left.draw()
            box_right.draw()
            left_label.draw()
            right_label.draw()
            self.win.flip()

            keys = event.waitKeys()
            for key in keys:
                if key == "left":
                    self.mapping = "direct"
                elif key == "right":
                    self.mapping = "inverse"
                elif key in ["escape", "q"]:
                    core.quit()
