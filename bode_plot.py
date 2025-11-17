import matplotlib.pyplot as plt   # Import plotting library for graphs
import numpy as np                # Import numerical library for arrays and math
from scipy import signal          # From the scipy library, just bring in the signal module

# This is the complete Transfer function H(s) = 0.2*(s + 10)/(s*(s + 2))

# Accept denominator input in a distribtuted Ax^2 + Bx + C format, taking the coefficients as input
numerator_str = input("Numerator: ")
numerator_lst = numerator_str.split(",")
numerator_float = [float(num) for num in numerator_lst]
print(numerator_float)

# Accept denominator input in a distribtuted Ax^2 + Bx + C format, taking the coefficients as input
denominator_str = input("Denominator: ")
denominator_lst = denominator_str.split(",")
denominator_float = [float(num) for num in denominator_lst]
print(denominator_float)


numerator = numerator_float.copy()      # This is essentially the distributed form of the numerator: 0.2*s + 2
denominator = denominator_float.copy()    # Similar to above but for 2nd order polynomial of denominator: s^2 + 2*s + 0

# Create transfer function object
system = signal.TransferFunction(numerator, denominator)    

# Generate Bode plot by computing frequency response of magnitude and phase
w, mag, phase = signal.bode(system)

# Magnitude Bode Plot
plt.figure()                            # Create figure for magnitude plot
plt.semilogx(w, mag)                    # create a logarithmic x-axis of magnitude vs frequency
plt.title('Bode Plot - Magnitude')      # Title the entire plot 
plt.xlabel('Frequency [rad/s]')         # Title the x-axis
plt.ylabel('Magnitude [dB]')            # Title the y-axis
plt.grid(True, which="both", ls="-")    # True enables grid, both is for grid on all major and minor ticks, "-" means solid lines

# Magnitude Phase Plot
plt.figure()                            # Create figure for Phase plot
plt.semilogx(w, phase)                  # create a logarithmic x-axis of Phase vs frequency
plt.title('Bode Plot - Phase')          # Title the entire plot
plt.xlabel('Frequency [rad/s]')         # Title the x-axis
plt.ylabel('Phase [degrees]')           # Title the y-axis
plt.grid(True, which="both", ls="-")    # True enables grid, both is for grid on all major and minor ticks, "-" means solid lines
plt.show()                              # Display the graphs in pop up windows
