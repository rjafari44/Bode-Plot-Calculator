# Bode Plot Calculator
#### A Python script that accepts a transfer function numerator and denominator as expressions, then graphs the Bode magnitude and phase plots. Automatically detects and displays the filter type up to 3rd order.

---

### Features

- Accepts expressions in **factored**, **distributed**, or **mixed** form
- Asterisks for multiplication are **optional**
- Missing terms (e.g. `s^3 + 1` with no middle terms) are **filled in automatically** — no need to enter zeros
- Classifies filter type up to **3rd order** and displays it on both plots
- **Input validation** — if a typo is detected, the script will ask you to re-enter rather than crashing
- Bode plot still generates accurately for systems **above 3rd order**, just without a filter type label

---

### Dependencies

Install with pip inside your virtual environment:

```bash
pip install matplotlib numpy scipy
```

`re` is part of the Python standard library and requires no installation. No specific Python version is required — Python 3.8 or newer works fine.

---

### How to Run

```bash
python3 bode_plot.py
```

---

### Input Format

When prompted, enter the numerator and denominator as plain expressions. The slash between them is not entered — you input each side separately.

**Factored form** — factors in parentheses, multiplied together:
```
0.2(s + 10)(s + 2)
s(s + 2)
(s^2 + 2s + 5)(s + 1)
```

**Distributed form** — fully expanded polynomial:
```
0.2s + 2
s^2 + 2s + 0
s^5 + 5s^4 + 3s + 1
```

**Mixed form** — factored and distributed combined:
```
0.2(s + 10)(s^2 + 3s + 2)
```

Asterisks are optional in all cases — `0.2*(s+10)` and `0.2(s+10)` are treated identically.

---

### Example

For the transfer function:

$$H(s) = \frac{0.2(s + 10)}{s(s + 2)}$$

Enter at the prompts:
```
Numerator   [e.g. 0.2(s + 10)]:         0.2(s + 10)
Denominator [e.g. s^3 + 5s^2 + 2s + 1]: s(s + 2)
```

The script will confirm the parsed coefficients, print the detected filter type, and display both the magnitude and phase Bode plots with the filter type shown as a subtitle.

---

### Filter Classification

The script classifies the filter type based on the order of the denominator polynomial:

| Denominator Order | Classification |
|---|---|
| 1st order | First-Order Low-Pass, High-Pass / Shelving |
| 2nd order | Second-Order Low-Pass, Band-Pass, High-Pass / Notch |
| 3rd order | Third-Order Low-Pass, Band-Pass, High-Pass / Shelving |
| Above 3rd | Plot still generates — filter type label not supported |

Integrators (pole at s=0) and differentiators (zero at s=0) are detected at any order.