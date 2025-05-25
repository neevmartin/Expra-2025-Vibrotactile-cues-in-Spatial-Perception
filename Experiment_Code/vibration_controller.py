from pyfirmata2 import Arduino
import time

class VibrationController:
    """
    Controller for managing vibrotactile actuators on an Arduino board.

    This class provides methods to initialize the Arduino connection, control vibration
    intensity and duration on specified pins, and manage resources safely.

    Attributes:
        testing (bool): If True, skips the Arduino connection process for testing purposes.
        max_volt (float): Maximum voltage allowed for the vibrator.
        power_source (float): Voltage of the power supply.
        voltage_scalar (float): Ratio of max_volt to power_source for PWM scaling.
        board (Arduino): The pyFirmata2 Arduino board instance.
    """
    
    def __init__(
        self,
        max_volt: float = 3,
        power_source: float = 5,
        testing: bool = False
    ) -> None:
        """
        Initialize the VibrationController controller.

        Args:
            max_volt (float): Maximum voltage allowed for the vibrator (per datasheet). Defaults to 3.
            power_source (float): Voltage of the power source used to drive the vibrators. Defaults to 5.
            testing (bool): If True, skips the Arduino connection process for testing purposes. Defaults to False.
        """
        
        self.testing = testing
        self.max_volt: float = max_volt 
        self.power_source: float = power_source 
        self.voltage_scalar: float = self.max_volt / self.power_source # maximum value allowed (0.6)
        self.board: Arduino = Arduino(Arduino.AUTODETECT, debug=True) if not testing else None
        print(f"Connected board: {self.board.name if not self.testing else None}.")

    def vibrate(
        self,
        intensity: float = 1,
        duration_sec: float = 1.0,
    ) -> None:
        """
        Activate vibration on specified pins with given intensity and duration.

        Args:
            intensity (float): Strength of vibration (0.0–1.0 or 0–100%). Values above 1 are treated as percentages.
            duration_sec (float): Duration of the vibration in seconds. Defaults to 1.0.

        Notes:
            - Intensity is clamped between 0.0 and 1.0.
            - After the specified duration, vibration is stopped by setting intensity to 0.
        """
        
        pins = [pin for pin in self.board.digital if pin.PWM_CAPABLE] if not self.testing else []  # Get all PWM-capable pins
        print(f"VibrationController: Found {len(pins)} PWM-capable pins.")
        if intensity > 1:
            intensity = intensity / 100
        intensity = max(0.0, min(intensity, 1.0)) # Makes sure intensity is between 0.0 and 1.0
        # Activate vibration
        if self.testing:
            print(f"[TEST MODE] Vibrate at intensity {intensity} for {duration_sec} seconds.")
            time.sleep(duration_sec) # Simulate vibration duration
            return
        for pin in pins:
            pin.write(intensity * self.voltage_scalar) # Set intensity of the vibration
        time.sleep(duration_sec)
        # Deactivate vibration 
        for pin in pins:
            pin.write(0) # Stop vibration

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