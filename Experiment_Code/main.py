from src.experiment.VibrotactileCueExperiment import VibrotactileCueExperiment
from src.config.config_loader import ExperimentConfig
from src.io.vibration_controller import VibrationController
from src.experiment.Experimental_Setup import Experimental_Setup

import src.experiment.ExplanationSlides as explanation_slides

from psychopy.visual import Window
from psychopy import logging
import os, sys

def create_participant_folder(participant_id: str) -> str:
    '''Function to create a participant folder.'''
    main_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(main_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    participant_dir = os.path.join(data_dir, participant_id)
    if not os.path.exists(participant_dir):
        os.makedirs(participant_dir)    
    
    return participant_dir

def get_resource_path(resource_folder: str) -> str:
    """Returns the correct path to the config files"""
    main_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(main_dir, 'resources', resource_folder)


def get_input_params(setup_data: dict, dev_mode=False) -> dict:
    return {
        "windowed": False,
        "resolution": [1080, 1920],
        "screenID": 0,
        "participantID": setup_data['participantID'],
        "participant_dir": create_participant_folder(setup_data['participantID']),
        "mode": setup_data['mode'],
        "mapping": "direct",
        "config_dir": get_resource_path("configs"),
        "slides_dir": get_resource_path("text_slides"),
        "debug": dev_mode
    }

def main(dev_mode = False):
    '''Starts the experiment.'''
    #params =  input_params()
    window = Window(
        size=[960, 540],
        screen=0,
        fullscr=False,
        units='pix',
        colorSpace='rgb255',           
        color=[128, 128, 128],
    )
    setup = Experimental_Setup(
        window
    )

    setup_params = setup.run()
    params = get_input_params(setup_params, dev_mode)
    window.close()

    params["mapping"] = setup_params.get("mapping")

    win_config = {key : params.get(key) for key in [
        'windowed',
        'resolution',
        'screenID'
    ]}
    print(params)
    experiment_config = ExperimentConfig(
        mode=params['mode'], 
        mapping=params['mapping'], 
        config_dir=params['config_dir']
    )
    participant = {key : params.get(key) for key in [
        'participantID',
        'participant_dir'
    ]}

    # Use when Arduino board is connected. 
    
    vibration_controller = VibrationController(testing=dev_mode)
    

    experiment = VibrotactileCueExperiment(
        win_config=win_config,
        experiment_config=experiment_config,
        participant=participant,
        vibration_controller=vibration_controller,
        debug = params['debug'],
        slides=explanation_slides.getSlides(params['slides_dir'])
    )

    # experiment = VibrotactileCueExperiment(
    #     win_config=win_config,
    #     experiment_config=experiment_config,
    #     participant=participant,
    #     debug = params['debug'],
    #     slides=explanation_slides.getSlides(params['slides_dir'])
    # )

    logging.console.setLevel(logging.ERROR)  # Only show errors, not warnings

    experiment.run()
    vibration_controller.close()

if __name__ == '__main__':
    # use the -d flag to 
    main("-d" in sys.argv[1:])
