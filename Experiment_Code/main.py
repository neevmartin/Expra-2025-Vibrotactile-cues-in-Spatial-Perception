from experiment import VibrotactileCueExperiment
from config_loader import ExperimentConfig
from vibration_controller import VibrationController

def create_participant_folder():
    ...
    return 'some_folder'

def input_params():
    '''Function to handle param input.'''
    params = {}

    params.update({
        'windowed'           : False,
        'resolution'         : [1920, 1080],
        'screenID'           : input('Screen: '),

        'participantID'      : input('Participant ID: '),
        'participant_dir'    : create_participant_folder(),

        'mode'               : input('Mode: '),
        'mapping'            : input('Mapping: '),
        'config_dir'         : 'configs',

        'debug'              : input('Debug: ')
    })

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
        'participant_dir'    : create_participant_folder(),

        'mode'               : 'reaching',
        'mapping'            : 'direct',
        'config_dir'         : 'configs',

        'debug'              : True
    })

    return params

def main():
    '''Starts the experiment.'''
    params =  input_params_example()

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
    #
    # vibration_controller = VibrationController(testing=False)
    # experiment = VibrotactileCueExperiment(
    #     win_config=win_config,
    #     experiment_config=experiment_config,
    #     participant=participant,
    #     vibration_controller=vibration_controller
    #     debug = params['debug']
    # )

    experiment = VibrotactileCueExperiment(
        win_config=win_config,
        experiment_config=experiment_config,
        participant=participant,
        debug = params['debug']
    )

    experiment.run()

if __name__ == '__main__':
    main()