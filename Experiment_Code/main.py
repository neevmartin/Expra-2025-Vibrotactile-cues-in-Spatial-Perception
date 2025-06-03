from experiment import VibrotactileCueExperiment
from config_loader import ExperimentConfig
from vibration_controller import VibrationController
from Experimental_Setup import Experimental_Setup
from psychopy.visual import Window
import os

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

def input_params():
    '''Function to handle param input.'''
    params = {}

    params.update({
        'windowed'           : False,
        'resolution'         : [1920, 1080],
        'screenID'           : input('Screen: '),

        'participantID'      : input('Participant ID: '),
        #'participant_dir'    : create_participant_folder(),

        'mode'               : input('Mode: '),
        'mapping'            : input('Mapping: '),
        'config_dir'         : 'configs',

        'debug'              : input('Debug: ')
    })
    
    participant_dir = create_participant_folder(params['participantID'])
    params['participant_dir'] = participant_dir

    return params

def input_params_example():
    '''
    Method to handle dynamic params.
    '''
    params = {}

    params.update({
        'windowed'           : True,
        'resolution'         : [1440, 900],
        'screenID'           : 0,

        'participantID'      : 'abc',
        #'participant_dir'    : create_participant_folder(),

        'mode'               : 'reaching',
        'mapping'            : 'direct',
        'config_dir'         : 'configs',

        'debug'              : True
    })
    participant_dir = create_participant_folder(params['participantID'])
    params['participant_dir'] = participant_dir

    return params

def new_input_params(setup_data: dict) -> dict:
    params = {}
    
    params.update({
        "windowed": False,
        "resolution": [1440,900],
        "screenID": 0,
        "participantID": setup_data['participantID'],
        "participant_dir": create_participant_folder(setup_data['participantID']),
        "mode": setup_data['mode'],
        "mapping": "direct",
        "config_dir": "configs",
        "debug": True
    })
    
    return params

def main():
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
    params = new_input_params(setup_params)
    window.close()

    win_config = {key : params.get(key) for key in [
        'windowed',
        'resolution',
        'screenID'
    ]}
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
    
    vibration_controller = VibrationController(testing=True)
    experiment = VibrotactileCueExperiment(
        win_config=win_config,
        experiment_config=experiment_config,
        participant=participant,
        vibration_controller=vibration_controller,
        debug = params['debug']
    )

    # experiment = VibrotactileCueExperiment(
    #     win_config=win_config,
    #     experiment_config=experiment_config,
    #     participant=participant,
    #     debug = params['debug']
    # )

    experiment.run()

if __name__ == '__main__':
    main()