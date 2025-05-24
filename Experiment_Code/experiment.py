from typing import Literal

import psychopy.event
from config_loader import ExperimentConfig
import tablet_input as tablet
import gui

import numpy as np

import psychopy
from psychopy.event import Mouse
from psychopy.visual import Window
from psychopy.clock import Clock

class Experiment:
    window: Window

    debug: bool
    running: bool

    def __init__(self, win_config: dict, debug: bool = False):
        self.window = Window(
            screen=win_config['screenID'],
            size=win_config['resolution'],
            units="pix",
            colorSpace = "rgb255",
            color = (128,128,128),
            fullscr=not win_config['windowed'] # usually reversed is counterintuitive
        )

        self.debug = debug
        self.running = True

        psychopy.core.wait(0.1)

    def run(self):
        self.run_introduction()
        self.run_experiment()
        self.run_outro()
        self.exit()

    def run_introduction(self):
        pass

    def run_experiment(self):
        pass
    
    def run_outro(self):
        pass

    def exit(self):
        self.window.close()
        psychopy.core.quit()

    def handle_keys(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class VibrotactileCueExperiment(Experiment):
    config: ExperimentConfig
    participant: dict

    # Same radius for all points
    RADIUS: int
    # Startpoint
    STARTPOS: list[int, int]
    # Endpoint
    STOPPOS: list[int, int]
    # Reference point: 'reaching' -> targetpoint, 'avoiding' -> obstacle
    MIN_TARGETDIST: list[int, int]
    MAX_TARGETDIST: list[int, int]
    target_pos: list[float, float]

    current_trial: dict
    previous_trial: dict

    state: dict
    text_confirmed: bool
    trial_confirmed: bool

    trial_running: bool

    def __init__(self, win_config: dict, experiment_config: ExperimentConfig, participant: dict, debug: bool = False):
        super().__init__(win_config, debug)

        self.config = experiment_config
        self.participant = participant

        self.current_trial = None
        self.previous_trial = None

        self.state = {
            'explanation': False,
            'feedback'   : False,
            'break'      : False
        }

    def run_experiment(self):
        while len(self.config.get_remaining_trials()) > 0:
            self.current_trial = self.config.get_next_trial()

            self.update_state(self.previous_trial, self.current_trial)

            if self.state['explanation'] == True: 
                if self.current_trial['task'] == 'avoiding':
                    self.init_avoiding_task()
                    self.give_explanation('avoiding')
                elif self.current_trial['task'] == 'reaching':
                    self.init_reaching_task()
                    self.give_explanation('reaching')
            elif self.state['break'] == True:
                self.give_break()

            self.init_trial()
            self.run_trial()

            if self.state['feedback'] == True:
                self.give_feedback()
            
            self.previous_trial = self.current_trial
    
    def run_trial(self):
        while not self.trial_confirmed:
            self.handle_keys()

            if self.trial_confirmation():
                self.trial_confirmed = True

            if self.debug:
                self.draw_debug()

            self.window.flip()
        
        while self.trial_running:
            self.handle_keys()

            self.update_trial()

            if self.debug:
                self.draw_debug()

            self.window.flip()

    def update_trial(self):
        tablet.update_stream(self.window)
        ### TODO: Output
        if self.trial_confirmation():
            self.trial_running = False

    def trial_confirmation(self) -> bool:
        '''Returns the trial condition which indicates the confirmation of the trial.'''
        return self.mouse_released()
    
    def mouse_released(self):
        mouse_pressed = tablet._mouse.getPressed()[0]
        while tablet._mouse.getPressed()[0]:
            psychopy.core.wait(0.01)
        return mouse_pressed

    def handle_keys(self):
        keys = psychopy.event.getKeys()

        for key in keys:
            if key == "q" or key == "escape":
                self.exit()
            if key == "return":
                if self.state['explanation'] or self.state['break']:
                    self.text_confirmed = True

    def update_state(self, previous_trial: dict, current_trial: dict):
        self.state['explanation'] = True if previous_trial == None or previous_trial['task'] != current_trial['task']   else False  
        self.state['feedback']    = True if current_trial['phase'] == 'training' or self.debug                          else False  
        self.state['break']       = True if previous_trial != None and previous_trial['block'] < current_trial['block'] else False  

    def draw_debug(self):
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
        
    def init_trial(self):
        self.init_target(self.current_trial['distance'])

        self.trial_confirmed = False
        self.trial_running = True

        if self.debug:
            tablet.start_stream(self.window, cursor_visible=True, dot_visible=True)
        else:
            tablet.start_stream(self.window)

    def init_reaching_task(self):
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [win_midX, -win_size[1]/4]
        self.STOPPOS   = [win_midX, win_size[1]/4]

        self.MIN_TARGETDIST = self.STARTPOS[1]
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1]

    def init_avoiding_task(self):
        win_size = self.window.size
        win_midX = 0

        self.RADIUS = 10

        self.STARTPOS = [win_midX, -win_size[1]/4]
        self.STOPPOS   = [win_midX, win_size[1]/4]

        self.MIN_TARGETDIST = self.STARTPOS[1]
        self.MAX_TARGETDIST = self.STOPPOS[1] - self.STARTPOS[1]

    def init_target(self, percent_distance):
        relative_distance = percent_distance * .01

        target_posX = self.STARTPOS[0]
        target_posY = self.MIN_TARGETDIST + self.MAX_TARGETDIST * relative_distance

        self.target_pos = [target_posX, target_posY]

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
        psychopy.event.waitKeys(keyList=['return'])

    def run_outro(self):
        gui.draw_centered_text(
           self.window,
           'Thank you for your participation in our study! \n' \
           'Press ENTER to close the experiment window.'
        )
        self.window.flip()
        psychopy.event.waitKeys(keyList=['return'])

    ### State funcs

    def give_feedback(self):
        last_mouse_info = tablet.get_trajectory()[-1]
        last_mouse_pos  = [last_mouse_info[1], last_mouse_info[2]]

        print(last_mouse_pos[1], self.target_pos[1])

        gui.draw_text_feedback(self.window, self.target_pos, last_mouse_pos)
        self.window.flip()

        psychopy.core.wait(2)

    def give_explanation(self, task: Literal['avoiding', 'reaching']):
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
            

    def give_break(self):
        self.text_confirmed = False

        gui.draw_centered_text(self.window, 'Eile mit Weile. \n Press ENTER to continue.')
        self.window.flip()

        while not self.text_confirmed:
            self.handle_keys()