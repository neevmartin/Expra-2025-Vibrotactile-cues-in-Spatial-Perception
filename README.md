# Expra 2025: Vibrotactile Cues in Spatial Perception

This project investigates the effect of vibrotactile kinesthetic feedback on spatial perception, specifically in goal-directed reaching and avoiding tasks. The experiment is built using PsychoPy for visual stimulus and control, and an Arduino for vibrotactile feedback.

## Overview
The experiment consists of several phases (Pre-Test, Training, Post-Test, Recap) across two primary tasks:
- **Reaching**: Goal-directed movement towards a target.
- **Avoiding**: Movement while avoiding obstacles/targets.

Feedback is provided via vibrotactile actuators controlled by an Arduino, with different mappings (Direct vs. Reversed) between distance and vibration intensity.

## Tech Stack
- **Language**: Python 3.x
- **Frameworks/Libraries**:
  - `PsychoPy`: Visual stimulation and experimental control.
  - `pyfirmata2`: Communication with Arduino for vibration control.
  - `PyYAML`: Configuration management.
  - `pandas`, `matplotlib`, `numpy`: Data analysis and plotting.
  - `Jupyter Notebook`: Data preprocessing and analysis.

## Requirements
### Hardware
- **Arduino Board**: Used to control vibrotactile actuators via PWM.
- **Vibrotactile Actuators**: Connected to PWM-capable pins on the Arduino.
- **Input Device**: Tablet/Stylus or Mouse (configured in the GUI).

### Software/Packages
Install dependencies using the provided `requirements.txt`:
```powershell
pip install -r requirements.txt
```
Dependencies include:
- `psychopy`
- `pyfirmata2`
- `pyyaml`
- `pandas`
- `matplotlib`
- `ipykernel` (for notebooks)

## Setup & Run

### 1. Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (or use a dedicated virtual environment).

### 2. Running the Experiment
The main entry point is `Experiment_Code/main.py`.
```powershell
python Experiment_Code/main.py
```
- Use the `-d` flag for **Debug Mode** (skips hardware initialization and runs in a window):
  ```powershell
  python Experiment_Code/main.py -d
  ```

### 3. Hardware Configuration
Ensure your Arduino is flashed with the **StandardFirmata** (or similar) to work with `pyfirmata2`. The `VibrationController` automatically detects the Arduino port.

## Scripts & Notebooks
- **`Experiment_Code/main.py`**: Main entry point for the experiment.
- **`Experiment_Code/data_analysis/`**:
  - `preprocessing.ipynb`: Initial data cleaning and preparation.
  - `main.ipynb`: Core analysis and plotting of results.
  - `trajectory_plotting.ipynb`: Visualization of participant movement trajectories.

## Project Structure
- `Experiment_Code/`: Core experiment logic and data analysis.
  - `src/`: Source code (experiment logic, config loaders, IO).
  - `resources/`: Config files (`.yaml`) and instruction slides.
  - `data_analysis/`: Jupyter notebooks and helper scripts for analysis.
- `Example Codes/`: Reference implementations for Arduino and PsychoPy.
- `Experimental Material/`: Documentation, consent forms, and setup diagrams.
- `Literature/`: Relevant scientific papers.
- `Slides/`: Course/Project presentation slides.

## Configuration & Env Vars
Experiment parameters are managed via YAML files in `Experiment_Code/resources/configs/`:
- `reaching.yaml`: Configuration for reaching-focused sessions.
- `avoiding.yaml`: Configuration for avoiding-focused sessions.

Parameters include `target_values`, `scan_time`, and `subgroups` (mapping types and phases).

## Tests
- `Experiment_Code/src/config/config_loader_tester.py`: Tests the YAML configuration loading and trial sequence generation.
- `Experiment_Code/src/io/test.ipynb`: Interactive testing of IO components.

## License
TODO: Add license information.

---
*Based on the ExPra SoSa 2025 project.*
