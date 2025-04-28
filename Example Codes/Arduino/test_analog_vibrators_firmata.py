# USAGE:
# Set WIN_COM to the port numbe of your connected Arduino
# and VIP_PINS to the pin numbers where your vibrators are conntected.
# Start the script. You can turn on/ off each vibrator in order with the numbers 1, 2, 3, ... in ascending pin number.

from pyfirmata import Arduino, util, pyfirmata
import platform
import time
import keyboard

# import argparse
# parser = argparse.ArgumentParser()
# args = parser.parse_args()

#####
# Set these:
<<<<<<< HEAD:test_analog_vibrators.py
WIN_COM = 9 # number is corresponding to the internal number of your USB-port (displayed in the Arduino IDE at the top after connecting your arduino via USB)
VIB_PINS = [10, 11] # pins from which the vibrators are connected to 
=======
WIN_COM = 6 # number is corresponding to the internal number of your USB-port (displayed in the Arduino IDE at the top after connecting your arduino via USB)
VIB_PINS = [5, 6] # pins from which the vibrators are connected to 
>>>>>>> caf16aaafcd5bb5ad3089ed72e6ac387db427be6:test_analog_vibrators_firmata.py
#####

MAX_VOLT = 3 # maximum voltage allowed for the specific vibrator used - can be found in data sheet of corresponding vibrator
POWER_SOURCE = 5 # power source we are using 

voltage_scalar = MAX_VOLT / POWER_SOURCE # maxmimum value allowed


def main():

    print("Getting Board")

    # Checking the system this script is running on
    if platform.system() == "Windows":
        board = Arduino('COM' + str(WIN_COM))
    else:
        board = Arduino('/dev/ttyACM0')

    # Create a list with all available pins
    vib_pins = []
    for pin in VIB_PINS:
        vib_pins.append(board.get_pin(f'd:{pin}:p')) # this is where the pin is assigned board.get_pin(<digital or analog>:<pinNumber>:<Mode>) -> a = analog, d = digital, piNumber is a scalar, <Mode>: i = input, o = output, p = pulse width mediation
        
    intensities = [0.] * len(vib_pins)

    stepsize = 0.01

    print("Starting control")
    while True:
        try:
            for pin_id in range(len(vib_pins)):
                if keyboard.is_pressed(str(pin_id+1)):
                    print(f"Setting pin {pin_id}")
                    intensities[pin_id] = (1. - intensities[pin_id])

                # set between 0 and 1

                vib_pins[pin_id].write(intensities[pin_id] * voltage_scalar) # this is where the intensity is set for the specified  vibrator, values between 0 and maximum possible value (scaled by voltage_scalar)

            time.sleep(0.1)
        except KeyboardInterrupt:
            for pin_id in range(len(vib_pins)):
                vib_pins[pin_id].write(0.) # this switches the vibrator off (intensity=0)
            print("By")
            break

if __name__ == "__main__":
    main()

