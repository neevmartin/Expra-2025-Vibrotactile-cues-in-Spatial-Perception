from psychopy import visual, event, core

class Experimental_Setup:
    """
    Class for participant setup phase of the experiment, including:
    - Collecting Participant ID
    - Selecting experiment mode (Reaching or Avoiding)
    - Displaying task-specific instructions

    This class is designed to run as a standalone pre-experiment setup
    before trial execution begins. It uses PsychoPy for visual input
    and output handling.

    Attributes
    ----------
    win : visual.Window
        The PsychoPy window used for rendering prompts and instructions.
    participant_id : str
        The ID entered by the participant.
    mode : str
        The selected experimental mode ('Reaching' or 'Avoiding').

    Methods
    -------
    run()
        Runs the complete setup routine and returns participant data.
    collect_id()
        Prompts the user to enter their Participant ID.
    select_mode()
        Allows user to select 'Reaching' or 'Avoiding' mode.
    show_instructions()
        Displays task-specific instructions based on selected mode.
    """
    



   
    def __init__(self, window):
        """
        Initialize the Experimental_Setup class.

        Parameters
        ----------
        window : visual.Window
            A PsychoPy window instance for displaying text and shapes.
        """
        self.win = window
        self.participant_id = ""
        self.mode = None

    def run(self) -> dict:
        """
        Runs the full setup: ID entry, mode selection, and instructions.

        Returns
        -------
        dict
            Dictionary containing participant ID, mode, and data directory path.
        """
        
        self.collect_id()
        self.select_mode()
        self.show_instructions()
        return {
            "participantID": self.participant_id,
            "mode": self.mode.lower(),
            "participant_dir": f"data/{self.participant_id}"
        }

    def collect_id(self):
        """
        Prompts the participant to enter their Participant ID using the keyboard.
        Displays the typed characters in real-time. Pressing ENTER finalizes input.
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
        Allows the participant to select the experiment mode by pressing
        the LEFT arrow (for Reaching) or RIGHT arrow (for Avoiding).
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
        Displays task-specific instructions based on the selected mode.
        Waits for the participant to press SPACE before continuing.
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
