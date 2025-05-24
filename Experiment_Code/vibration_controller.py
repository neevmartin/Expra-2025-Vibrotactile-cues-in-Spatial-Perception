from pyfirmata import Arduino
import time
import serial.tools.list_ports
from typing import List, Optional, Dict, Any

class VibrationController:
    """
    Controller for managing vibrotactile actuators on an Arduino board.

    This class provides methods to initialize the Arduino connection, control vibration
    intensity and duration on specified pins, and manage resources safely.

    Attributes:
        testing (bool): If True, skips the Arduino connection process for testing purposes.
        vib_pins (List[int]): PWM-capable pin numbers for vibrators.
        max_volt (float): Maximum voltage allowed for the vibrator.
        power_source (float): Voltage of the power supply.
        voltage_scalar (float): Ratio of max_volt to power_source for PWM scaling.
        board: The pyFirmata Arduino board instance.
        pwm_objects (Dict[int, Any]): Mapping of pin numbers to PWM pin objects.
    """
    
    def __init__(
        self,
        vib_pins: Optional[List[int]] = None,
        max_volt: float = 3,
        power_source: float = 5,
        testing: bool = False
    ) -> None:
        """
        Initialize the VibrationController controller.

        Args:
            vib_pins (Optional[List[int]]): List of PWM-capable pin numbers to which the vibrators are connected.
                If None, defaults to [3, 5, 6, 9, 10, 11] (All PWN capable pins on the board).
            max_volt (float): Maximum voltage allowed for the vibrator (per datasheet). Defaults to 3.
            power_source (float): Voltage of the power source used to drive the vibrators. Defaults to 5.
            testing (bool): If True, skips the Arduino connection process for testing purposes. Defaults to False.

        Raises:
            IOError: If no Arduino device is found among the connected serial ports.
            Exception: If the Arduino connection fails.
        """
        
        self.testing = testing
        self.vib_pins: List[int] = vib_pins if vib_pins is not None else [3, 5, 6, 9, 10, 11]
        self.max_volt: float = max_volt 
        self.power_source: float = power_source 
        self.voltage_scalar: float = self.max_volt / self.power_source # maximum value allowed (0.6)
        self.board: Arduino = None
        self.pwm_objects: Dict[int, Any] = {}
        if not self.testing: 
            self._initialize() # Initialize the board and PWM objects
        else:
            print("[TEST MODE] VibrationController initialized without hardware.")

    def _identify_arduino_port(self) -> str:
        """
        Scan available serial ports to identify the Arduino's port.

        Returns:
            str: The device name of the serial port connected to the Arduino.

        Raises:
            IOError: If no Arduino device is found among the connected serial ports.
        """
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description:
                return port.device
        raise IOError("Arduino not found. Please connect the Arduino board or check the connection.")
    
    def _initialize(self) -> None:
        """
        Initialize the Arduino board connection and set up PWM objects for vibration pins.

        Raises:
            Exception: If the Arduino port cannot be identified or the connection fails.
        """
        
        port = self._identify_arduino_port()
        self.board = Arduino(port)
        time.sleep(1.0) # Allow time for the connection to stabilize
        print(f"Arduino connected on port {port}")
        self.pwm_objects = {pin: self.board.get_pin(f'd:{pin}:p') for pin in self.vib_pins}

    def vibrate(
        self,
        intensity: float = 1,
        duration_sec: float = 1.0,
        pins=None
    ) -> None:
        """
        Activate vibration on specified pins with given intensity and duration.

        Args:
            intensity (float): Strength of vibration (0.0–1.0 or 0–100%). Values above 1 are treated as percentages.
            duration_sec (float): Duration of the vibration in seconds. Defaults to 1.0.
            pins (Optional[List[int]]): List of pin numbers to activate. If None, uses all PWM-capable pins.

        Notes:
            - Intensity is clamped between 0.0 and 1.0.
            - After the specified duration, vibration is stopped by setting intensity to 0.
            - Warns if a specified pin is not configured for PWM.
            - No need to specify pins in our case. Accessing a pin that is not connected to anything will not cause any issues.
        """
        
        pins = self.vib_pins if pins is None else pins
        if intensity > 1:
            intensity = intensity / 100
        intensity = max(0.0, min(intensity, 1.0)) # Makes sure intensity is between 0.0 and 1.0
        # Activate vibration
        if self.testing:
            print(f"[TEST MODE] Vibrate pins {pins} at intensity {intensity} for {duration_sec} seconds.")
            time.sleep(duration_sec) # Simulate vibration duration
            return
        for pin in pins:
            if pin in self.pwm_objects:
                self.pwm_objects[pin].write(intensity * self.voltage_scalar) # Set intensity of the vibration
            else:
                print(f"Warning: Pin {pin} not configured for PWM")
        time.sleep(duration_sec) 
        # Deactivate vibration
        for pin in pins:
            if pin in self.pwm_objects:
                self.pwm_objects[pin].write(0) # Stop vibration

    def close(self) -> None:
        """
        Close the connection to the board if it exists.

        Attempts to safely exit and clean up the board resource. If an exception occurs during
        the exit process, it is silently ignored. After closing, the board reference is set to None.
        """
        
        if self.testing:
            print("[TEST MODE] Closing VibrationController (no hardware).")
            return
        if self.board:
            try:
                self.board.exit()
            except Exception:
                pass
            self.board = None

    def __del__(self) -> None:
        """
        Destructor method that attempts to close resources associated with the object.
        If an exception occurs during the closing process, it is silently ignored.
        """
        
        try:
            self.close()
        except Exception:
            pass
        
    def __enter__(self) -> 'VibrationController':
        """
        Enter the runtime context related to this object.

        Returns:
            VibrationController: The instance itself, allowing use with the 'with' statement.
        """
        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the runtime context and close any resources.

        This method is called when exiting a context managed by the 'with' statement.
        It ensures that resources held by the object are properly released by calling the `close()` method.
        """
        
        self.close()

# Example usage:
if __name__ == "__main__":
    # Context manager ensures cleanup:
    with VibrationController(testing=True) as vibrator:
        vibrator.vibrate(0.8, 2)
    # Alternatively you can just use the normal method:
    vibrator = VibrationController(testing=True)
    vibrator.vibrate(0.8, 2)
    vibrator.close()
# TODO: Test with the actual Arduino board