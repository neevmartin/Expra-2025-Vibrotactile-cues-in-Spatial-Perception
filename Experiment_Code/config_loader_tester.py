import random


from config_loader import ExperimentConfig





def trialStructure(mode):
    mapping = random.choice(["direct", "reversed"])
    config = ExperimentConfig(mode=mode, mapping=mapping)

    print(f"=== Experiment Mode: {mode} | Mapping: {mapping} ===\n")

    trial_num = 1
    while True:
        trial = config.get_next_trial()
        if trial is None:
            print("\nAll trials completed.")
            break

        phase = trial["phase"]
        task = trial["task"]
        block = trial["block"]
        rep = trial["repetition"]
        distance = trial["distance"]
        intensity = trial["intensity"]

        print(
            f"Trial {trial_num:03d} | Phase: {phase} | Task: {task} | "
            f"Block: {block} | Rep: {rep} | Distance: {distance} | Intensity: {intensity}"
        )
        #print(trial)
        trial_num += 1



trialStructure("avoiding")