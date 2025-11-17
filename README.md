# BodePlotCalculator
A simple python script that will take inputs for zeros, poles and gain constant to plot out the magnitude and phase plots of the Bode Plot.
For inputting, you have to ensure it is in Ax^2 + Bx + C format. So distribution may be necessary depending on the transfer function.
For example, if you have a transfer function H(s) = 10(s+5)/((s+10)(s+40)), it needs to be distributed to get 10s+50/(s^2+50s+400). 
You then will take the coefficients of numerator or denominator and input them with a ", " (comma whitespace) separation into the prompt. so for numerator of this example,
it would be (10, 50) and the denominator will be (1, 50, 400). If no A, B, or C term exists, then simply input 0.