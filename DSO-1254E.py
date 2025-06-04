import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# Set the VISA resource string (this may vary depending on your oscilloscope)
OSCILLOSCOPE_VISA_ADDRESS = "USB0::0x0699::0x0363::C000000::INSTR"  # Example for Tektronix


def read_oscilloscope_waveform():
    # Initialize VISA resource manager
    rm = pyvisa.ResourceManager()

    try:
        # Connect to oscilloscope
        oscilloscope = rm.open_resource(OSCILLOSCOPE_VISA_ADDRESS)
        oscilloscope.timeout = 5000  # in milliseconds

        # Identify instrument
        print("Connected to:", oscilloscope.query("*IDN?"))

        # Set up the waveform parameters
        oscilloscope.write("DATA:SOURCE CH1")  # Use Channel 1
        oscilloscope.write("DATA:ENC RPB")  # Binary encoding
        oscilloscope.write("DATA:WIDTH 1")  # 1 byte per point

        # Get waveform preamble to decode data
        x_increment = float(oscilloscope.query("WFMPre:XINcr?"))
        x_origin = float(oscilloscope.query("WFMPre:XZEro?"))
        y_increment = float(oscilloscope.query("WFMPre:YMUlt?"))
        y_origin = float(oscilloscope.query("WFMPre:YZEro?"))
        y_offset = float(oscilloscope.query("WFMPre:YOFF?"))

        # Request waveform data
        oscilloscope.write("CURVE?")
        raw_data = oscilloscope.read_raw()

        # Strip header (usually the first few bytes indicating length)
        header_len = int(raw_data[1])
        data_start = 2 + header_len
        data = np.frombuffer(raw_data[data_start:], dtype=np.uint8)

        # Convert to voltage and time
        voltages = (data - y_offset) * y_increment + y_origin
        times = np.arange(0, len(voltages)) * x_increment + x_origin

        # Plot waveform
        plt.figure(figsize=(10, 4))
        plt.plot(times, voltages)
        plt.title("Oscilloscope Waveform - Channel 1")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.grid(True)
        plt.show()

        oscilloscope.close()

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    read_oscilloscope_waveform()
