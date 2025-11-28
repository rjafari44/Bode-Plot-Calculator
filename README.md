# BodePlotCalculator
#### A simple python script that will accept user input for the gain constant, poles and zeros within the distributed polynomial for graphing the Bode phase and magnitude plots.

--- 

### How to run

For inputting, you have to ensure it is in Ax^2 + Bx + C format. So distribution may be necessary depending on the transfer function. For example, if you have a transfer function H(s) = 10(s+5)/((s+10)(s+40)), it needs to be distributed to get 10s+50/(s^2+50s+400). You will then take the coefficients of the numerator and denominator. Input them with a "," (comma) separation into the prompt. so for numerator of this example, it would be (10, 50) and the denominator will be (1, 50, 400). If no A, B, or C term exists, then simply input 0. This is the first Python script that I have written. The white space after the comma is not necessary. I also received help on this code from Kaveh Zare, so check out his work on GitHub!

#### in CLI
```bash
python3 bode_plot.py
```
