import yaml
import os
import random

class ExperimentConfig:
    """
    Class to manage loading and accessing experimental configuration data
    for psychophysical reaching/avoiding tasks following vibration stimulus.

    It supports two mapping types:
      - 'direct': intensity increases with distance
      - 'reversed': intensity decreases with distance

    The configuration is stored in a YAML file per mode (e.g., 'reaching.yaml', 'avoiding.yaml').
    """

    def __init__(self, mode: str, mapping: str, config_dir: str = "configs"):
        """
        Initialize the ExperimentConfig object.

        Args:
            mode (str): Experimental mode ('reaching' or 'avoiding').
            mapping (str): Mapping type ('direct' or 'reversed').
            config_dir (str): Path to the directory containing YAML config files.
        """
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
        Trials are randomized within each repetition of each block.
        """
        self.trial_sequence = []

        mapping_type = self.get_mapping_type()
        default_distances = self.get_target_distances()
        default_intensities = self.get_target_intensities()

        if mapping_type == "reversed":
            default_intensities = list(reversed(default_intensities))

        for phase in self.get_phases():
            task = phase["task"]
            phase_name = phase["name"]
            blocks = phase["blocks"]
            repetitions = phase["repetitions"]
            d_list = phase.get("target_distances", default_distances)
            i_list = phase.get("intensity_levels", default_intensities)

            for b in range(blocks):
                for r in range(repetitions):
                    # Create trials for this repetition
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
                    # Shuffle order within this repetition
                    random.shuffle(repetition_trials)
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
        if self.current_index == 0:
            return None
        return self.trial_sequence[self.current_index - 1]

    def get_all_trials(self):
        """
        Return the full trial sequence (including upcoming and completed).
        """
        return self.trial_sequence

    def get_completed_trials(self):
        """
        Return the list of completed trials (up to the current index).
        """
        return self.trial_sequence[:self.current_index]

    def get_remaining_trials(self):
        """
        Return the list of trials yet to be completed.
        """
        return self.trial_sequence[self.current_index:]

    def get_trial_index(self):
        """
        Return the current index (next trial number to be fetched).
        """
        return self.current_index

    def reset_trials(self):
        """Reset the trial index to the beginning (e.g., for a rerun or test)."""
        self._trial_index = 0

