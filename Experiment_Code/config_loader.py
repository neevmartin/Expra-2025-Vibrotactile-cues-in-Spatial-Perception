"""
Experiment Configuration Manager for Psychophysical Tasks
========================================================

This module provides the `ExperimentConfig` class, which loads and manages
trial configurations for psychophysical experiments involving reaching or
avoiding tasks following vibration stimuli.

Configurations are loaded from YAML files and define randomized trial sequences
based on experiment mode (e.g., 'reaching', 'avoiding') and mapping (e.g., 'direct', 'reversed').

Example:
    config = ExperimentConfig(mode="avoiding", mapping="reversed")

    trial = config.get_next_trial()

    print(trial["distance"], trial["intensity"])

Attributes:
    trial_sequence (List[Dict]): List of generated trials. Each trial has keys:
        - phase (str)
        - task (str)
        - block (int)
        - repetition (int)
        - distance (float)
        - intensity (float)

Typical Trial Structure:
    {
        "phase": "Training",
        "task": "avoiding",
        "block": 2,
        "repetition": 5,
        "distance": 63.6,
        "intensity": 36.4
    }

YAML Configuration Format:
    target_values:
        distances: [float, float, ...]

        intensities: [float, float, ...]
    subgroups:
        direct:
            mapping_type: "direct"

            phases:
                - name: "Training"
                - task: "reaching"
                - blocks: 2
                - repetitions: 3
        reversed:
            mapping_type: "reversed"

            phases:
                ...

Access Methods:
    - get_next_trial(): Get the next trial and advance index
    - get_current_trial(): Most recently returned trial
    - get_current_phase(): Phase of the upcoming trial
    - get_current_task(): Task of the upcoming trial
    - get_all_trials(): Return all generated trials
    - get_completed_trials(): Return trials already completed
    - get_remaining_trials(): Return trials yet to run
    - get_trial_index(): Return index of next trial
    - reset_trials(): Reset index to rerun trials from start

Author:
-------
Martin Neev, TU Darmstadt/Expra 2025 Vibrotactile Cues in Spatial Perception

Date: 21.05.2025
"""
import yaml
import os
import random


class ExperimentConfig:
    """
    Class to manage loading and accessing experimental configuration data
    for psychophysical reaching/avoiding tasks following vibration stimulus.

    It supports two mapping types:
      - 'direct': vibration intensity increases with distance
      - 'reversed': vibration intensity decreases with distance

    The configuration is stored in a YAML file per mode (e.g., 'reaching.yaml', 'avoiding.yaml').

    Structure:
    ----------
    self.trial_sequence: List[Dict]
        A flat list containing all trials in the experiment.
        Each trial is a dictionary with the following structure:

        {
            "phase": str,        # e.g., "Pre-Test", "Training", "Post-Test"

            "task": str,         # e.g., "reaching" or "avoiding"

            "block": int,        # Block number (1-indexed)

            "repetition": int,   # Repetition number within the block (1-indexed)

            "distance": float,   # Target distance value (e.g., 54.5)

            "intensity": float   # Corresponding intensity (depends on mapping)

        }

    Example trial:
    --------------
        {
            "phase": "Training",

            "task": "avoiding",

            "block": 2,

            "repetition": 5,

            "distance": 63.6,

            "intensity": 36.4  # If mapping is reversed
        }

    Accessing trial parameters:
    ---------------------------
    You can access a trial using `get_next_trial()` or similar methods, and extract parameters like this:


    trial = config.get_next_trial()

    if trial:
        - phase = trial["phase"]
        - task = trial["task"]
        - block = trial["block"]
        - repetition = trial["repetition"]
        - distance = trial["distance"]
        - intensity = trial["intensity"]

    Other access options:
    ---------------------
    - Current trial:        config.get_current_trial()
    - All trials:           config.get_all_trials()
    - Completed trials:     config.get_completed_trials()
    - Remaining trials:     config.get_remaining_trials()
    - Trial index:          config.get_trial_index()
    - Current phase/task:   config.get_current_phase(), config.get_current_task()
    """

    def __init__(self, mode: str, mapping: str, config_dir: str = "configs"):
        """
        Initialize the ExperimentConfig object.

        Args:
            mode (str): Experimental mode ('reaching' or 'avoiding').
            mapping (str): Mapping type ('direct' or 'reversed').
            config_dir (str): Path to the directory containing YAML config files.
        """

        location = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(location, config_dir)
        
        self.mode = mode.lower()
        self.mapping = mapping.lower()
        self.config_path = os.path.join(config_dir, f"{self.mode}.yaml")
        self._load_config()
        self._validate_mapping()
        self._generate_trial_sequence()
        self._trial_index = 0  # Keeps track of progress through trials

    def _load_config(self):
        """Load the YAML configuration file based on the experiment mode."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def _validate_mapping(self):
        """Ensure the specified mapping type exists in the loaded config."""
        if self.mapping not in self.config.get("subgroups", {}):
            raise ValueError(f"Mapping type '{self.mapping}' not found in config for mode '{self.mode}'.")

    def _generate_trial_sequence(self):
        """
    Generate the complete randomized trial sequence.
    ----------
        Trials are randomized within each repetition of each block.

        This method loops through each phase (e.g., Pre-Test, Training, Post-Test),
        retrieves the number of blocks and repetitions, and generates trial dictionaries
        combining distance and intensity levels.

        For each repetition in a block, it creates a full list of trials by zipping
        the target distances and intensities, then shuffles the order of those trials
        to avoid order effects. All trials are then accumulated into a master sequence.
        """
        self.trial_sequence = []

        # Get the mapping type: either 'direct' or 'reversed'
        mapping_type = self.get_mapping_type()

        # Get global default distances and intensities
        default_distances = self.get_target_distances()
        default_intensities = self.get_target_intensities()

        # If reversed mapping is used, reverse the intensity list
        if mapping_type == "reversed":
            default_intensities = list(reversed(default_intensities))

        # Loop over each phase in the config (e.g., Pre-Test, Training, etc.)
        for phase in self.get_phases():
            task = phase["task"]
            phase_name = phase["name"]
            blocks = phase["blocks"]
            repetitions = phase["repetitions"]

            # Use phase-specific values if provided, otherwise fall back to defaults
            d_list = phase.get("target_distances", default_distances)
            i_list = phase.get("intensity_levels", default_intensities)

            # Iterate over blocks in this phase
            for b in range(blocks):
                # Iterate over repetitions within the block
                for r in range(repetitions):
                    # Create a list of trial dictionaries by pairing distance & intensity
                    repetition_trials = [
                        {
                            "phase": phase_name,
                            "task": task,
                            "block": b + 1,
                            "repetition": r + 1,
                            "distance": d,
                            "intensity": i
                        }
                        for d, i in zip(d_list, i_list)
                    ]

                    # Randomize the order of trials for this repetition to prevent bias
                    random.shuffle(repetition_trials)

                    # Add randomized trials to the overall sequence
                    self.trial_sequence.extend(repetition_trials)

    def get_target_distances(self):
        """Return the global list of target distances from the config."""
        return self.config.get("target_values", {}).get("distances", [])

    def get_target_intensities(self):
        """Return the global list of intensity levels from the config."""
        return self.config.get("target_values", {}).get("intensities", [])

    def get_mapping_type(self):
        """Return the mapping type: 'direct' or 'reversed'."""
        return self.config["subgroups"][self.mapping]["mapping_type"]

    def get_phases(self):
        """Return the ordered list of phases for the selected mapping."""
        return self.config["subgroups"][self.mapping]["phases"]

    def get_total_trials(self):
        """Return the total number of trials in the current trial sequence."""
        return len(self.trial_sequence)

    def get_next_trial(self):
        """
        Return the next trial in the sequence and increment the internal index.
        Returns None if all trials are exhausted.

        Returns:
            dict or None: Trial data or None if complete.
        """
        if self._trial_index >= len(self.trial_sequence):
            return None  # All trials completed
        trial = self.trial_sequence[self._trial_index]
        self._trial_index += 1
        return trial

    def get_current_phase(self):
        """
        Return the name of the current phase (based on the upcoming trial).

        Returns:
            str or None: Name of the phase or None if finished.
        """
        if 0 <= self._trial_index < len(self.trial_sequence):
            return self.trial_sequence[self._trial_index]["phase"]
        return None

    def get_current_task(self):
        """
        Return the name of the current task (based on the upcoming trial).

        Returns:
            str or None: Task name or None if finished.
        """
        if 0 <= self._trial_index < len(self.trial_sequence):
            return self.trial_sequence[self._trial_index]["task"]
        return None

    def get_current_trial(self):
        """
        Return the current trial (most recently returned by get_next_trial).
        Returns None if get_next_trial hasn't been called yet.
        """
        if self._trial_index == 0:
            return None
        return self.trial_sequence[self._trial_index - 1]

    def get_all_trials(self):
        """
        Return the full trial sequence (including upcoming and completed).
        """
        return self.trial_sequence

    def get_completed_trials(self):
        """
        Return the list of completed trials (up to the current index).
        """
        return self.trial_sequence[:self._trial_index]

    def get_remaining_trials(self):
        """
        Return the list of trials yet to be completed.
        """
        return self.trial_sequence[self._trial_index:]

    def get_trial_index(self):
        """
        Return the current index (next trial number to be fetched).
        """
        return self._trial_index

    def reset_trials(self):
        """Reset the trial index to the beginning (e.g., for a rerun or test)."""
        self._trial_index = 0
