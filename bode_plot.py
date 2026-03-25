import matplotlib.pyplot as plt   # Import plotting library for graphs
import numpy as np                # Import numerical library for arrays and math
from scipy import signal          # From the scipy library, just bring in the signal module
import re                         # Import regex library for flexible expression parsing

# This is the complete Transfer function H(s) = 0.2*(s + 10) / (s*(s + 2))
# Inputs can be in factored form:     e.g.  0.2*(s^2 + 3s + 2)(s + 10)  or  0.2(s+10)
# Inputs can be in distributed form:  e.g.  s^5 + 5s^4 + 2s + 1         or  0.2*s + 2
# Factored and distributed forms can be mixed, e.g.  (s^2 + 2s + 5)(s + 1)
# Asterisks for multiplication are optional in all cases


def parse_distributed(expr, scalar=1.0):
    """
    Parse a single distributed polynomial string like s^5 + 5s^4 + 2s + 1
    into a coefficient array in descending power order, e.g. [1, 5, 0, 0, 2, 1].
    An optional scalar is applied to the entire result.
    """

    # Split on + or - boundaries, keeping the sign attached to each term
    terms = re.findall(r'[+-]?[^+-]+', expr)    # Each element is one term like '-3s^2' or '+5'
    parsed = {}     # Map from integer power -> float coefficient

    for term in terms:
        term = term.strip('*')      # Remove any stray asterisks at the edges of the term

        if 's' in term:
            # Term contains 's', so split around it to get the coefficient and exponent
            parts = term.split('s')
            coeff_str = parts[0].strip('*')     # Everything left of 's' is the coefficient

            # Handle cases where coefficient is implicit: '', '+' -> 1, '-' -> -1
            if coeff_str in ('', '+'):  coeff_str = '1'
            if coeff_str == '-':        coeff_str = '-1'

            exp_part = parts[1].lstrip('^') if len(parts) > 1 else ''  # Exponent is after 's^'
            power = int(exp_part) if exp_part else 1                    # Default power of bare 's' is 1

            coeff = float(coeff_str)
        else:
            # No 's' in term, it is a pure constant
            coeff = float(term)
            power = 0

        parsed[power] = parsed.get(power, 0) + coeff   # Accumulate in case of duplicate powers
    
    max_power = max(parsed.keys()) if parsed else 0     # Highest power present in the expression

    # Build array in descending power order and apply the scalar multiplier
    coeffs = np.array([parsed.get(p, 0.0) for p in range(max_power, -1, -1)])
    coeffs *= scalar

    return coeffs   # Return numpy array for use with np.polymul


def parse_expression(expr):
    """
    Parse a polynomial expression string of any order into a coefficient list
    in descending power order, e.g. [1, 2, 0] = s^2 + 2s + 0.
    Accepts factored form, distributed form, or a mix of both.
    Handles optional asterisks and a leading scalar multiplier.
    Examples:
        's^5 + 5s^4 + 3s + 1'          -> distributed, any order
        '(s^2 + 2s + 5)(s + 1)'        -> factored with quadratic inner group
        '0.2(s + 10)(s^3 + s + 4)'     -> scalar * mixed-order factored form
        's(s^2 + 3s + 2)'              -> bare s token times a quadratic group
    """

    expr = expr.replace(" ", "")        # Strip all whitespace for uniform processing
    expr = expr.replace("**", "^")      # Normalize Python exponent ** to caret ^

    # --- Step 1: Extract an optional leading scalar multiplier ---
    # A scalar is a plain number sitting before the first '(' or 's'
    scalar = 1.0
    scalar_match = re.match(r'^([+-]?\d*\.?\d+)\*?(?=[\(s])', expr)
    if scalar_match:
        scalar = float(scalar_match.group(1))   # Store the numeric scalar value
        expr = expr[scalar_match.end():]         # Trim the scalar off the front

    # --- Step 2: Decide between factored and pure distributed form ---
    # If there are no parentheses, the entire expression is one distributed polynomial
    if '(' not in expr:
        return parse_distributed(expr, scalar=scalar).tolist()  # Parse and return immediately

    # --- Step 3: Factored form — tokenise into individual multiplicative factors ---
    # Tokens are: bare 's', 's^n', or a '(...)' group containing any polynomial
    tokens = re.findall(r's\^\d+|s(?!\^)|\([^)]+\)', expr)

    poly = np.array([scalar])       # Running product polynomial, seeded with the scalar

    for token in tokens:
        if token == 's':
            factor = np.array([1.0, 0.0])   # Bare 's' is the polynomial [1, 0] = s^1 + 0

        elif token.startswith('s^'):
            power = int(token[2:])          # Extract integer exponent n from 's^n'
            factor = np.zeros(power + 1)    # Build [1, 0, 0, ..., 0] of length power+1
            factor[0] = 1.0

        else:
            # Parenthesised group — strip the parens and parse the inside as a distributed polynomial
            # This handles any order: (s+1), (s^2+2s+5), (s^3+4s^2+s+2), etc.
            inner = token[1:-1]                         # Remove surrounding parentheses
            factor = parse_distributed(inner, scalar=1.0)   # Parse inner polynomial, scalar applied later

        poly = np.polymul(poly, factor)     # Multiply the running product by this factor

    return poly.tolist()    # Return as plain list for use with scipy.signal


def classify_filter(num_coeffs, den_coeffs):
    """
    Classify the filter type based on pole and zero locations derived
    from the numerator and denominator coefficient arrays.
    Supports accurate classification up to 3rd order systems.
    For systems with a denominator order above 3, a warning is printed
    and a generic label is returned — the Bode plot still renders correctly.
    """

    zeros = np.roots(num_coeffs)    # Compute zeros from numerator roots
    poles = np.roots(den_coeffs)    # Compute poles from denominator roots

    has_integrator     = any(abs(p) < 1e-6 for p in poles)           # Pole at s=0 means integrator
    has_differentiator = any(abs(z) < 1e-6 for z in zeros)           # Zero at s=0 means differentiator
    rhp_zeros          = sum(1 for z in zeros if np.real(z) > 1e-6)  # Right-half-plane zeros

    num_order = len(num_coeffs) - 1     # Order of numerator polynomial
    den_order = len(den_coeffs) - 1     # Order of denominator polynomial

    # --- Guard: warn and bail out for anything above 3rd order denominator ---
    if den_order > 3:
        print(f"  Note: Filter classification is only supported up to 3rd order.")
        print(f"        Your denominator is order {den_order} — the Bode plot is still accurate,")
        print(f"        but the filter type label cannot be determined.\n")
        return f"Order Too High To Classify (Den: {den_order}, Num: {num_order})"

    # --- Integrator / Differentiator checks apply at any supported order ---
    if has_integrator and not has_differentiator:
        return "Integrator / Low-Pass"              # Pole at origin causes integration and rolloff

    if has_differentiator and not has_integrator:
        return "Differentiator / High-Pass"         # Zero at origin boosts high frequencies

    if has_integrator and has_differentiator:
        return "Band-Pass (Integrator + Differentiator)"    # Both origin pole and zero

    # --- 1st Order ---
    if den_order == 1:
        if num_order == 0:
            return "First-Order Low-Pass"               # Constant numerator, one pole
        if num_order == 1:
            return "First-Order High-Pass / Shelving"   # Zero and pole at same order

    # --- 2nd Order ---
    if den_order == 2:
        if num_order == 0:
            return "Second-Order Low-Pass"              # Two poles, no zeros, full rolloff
        if num_order == 1:
            return "Second-Order Band-Pass"             # One zero, two poles
        if num_order == 2:
            if rhp_zeros > 0:
                return "Second-Order Notch (Non-Minimum Phase)"  # RHP zero creates notch
            return "Second-Order High-Pass / Notch"     # Numerator and denominator same order

    # --- 3rd Order ---
    if den_order == 3:
        if num_order == 0:
            return "Third-Order Low-Pass"               # Three poles, no zeros, steep rolloff
        if num_order == 1:
            return "Third-Order Low-Pass / Band-Pass"   # One zero softens the rolloff
        if num_order == 2:
            return "Third-Order Band-Pass"              # Two zeros, three poles
        if num_order == 3:
            return "Third-Order High-Pass / Shelving"   # Same order numerator and denominator

    return "Unclassified"                               # Fallback, should not normally be reached


# --- Prompt the user for numerator and denominator expressions ---
print("\nEnter the numerator and denominator as expressions.")
print("  Factored form:     0.2(s + 10)(s^2 + 2s + 5)   or   s(s + 2)")
print("  Distributed form:  s^5 + 5s^4 + 3s + 1         or   0.2s + 2")
print("  Mixed:             (s^2 + 2s + 5)(s + 1)")
print("  Asterisks are optional in all cases.\n")


def prompt_expression(label, example):
    """
    Repeatedly prompt the user for a polynomial expression until it parses
    successfully. Prints a clean error block on failure and asks again.
    """
    while True:
        raw = input(f"{label} [e.g. {example}]: ")      # Display label and example to guide input
        try:
            coeffs = parse_expression(raw)              # Attempt to parse the entered expression
            return coeffs                               # Return on success, exiting the loop
        except Exception:
            print()
            print("  ----------------------------------------")
            print("  Error: could not parse expression.")
            print("  Double-check your typing and try again.")
            print("  ----------------------------------------")
            print()                                     # Clean visual separation before re-prompt


# Prompt for numerator and denominator with automatic retry on bad input
numerator_coeffs   = prompt_expression("Numerator  ", "0.2(s + 10)")           # Get numerator coefficients
denominator_coeffs = prompt_expression("Denominator", "s^3 + 5s^2 + 2s + 1")  # Get denominator coefficients

print(f"\nParsed numerator coefficients:   {numerator_coeffs}")     # Confirm parsed numerator
print(f"Parsed denominator coefficients: {denominator_coeffs}\n")   # Confirm parsed denominator

# Identify the filter type from the coefficient arrays before plotting
filter_type = classify_filter(numerator_coeffs, denominator_coeffs)
print(f"Detected filter type: {filter_type}\n")

# Create the transfer function object from parsed coefficients
system = signal.TransferFunction(numerator_coeffs, denominator_coeffs)

# Generate Bode plot data by computing the frequency response
w, mag, phase = signal.bode(system)

# --- Magnitude Bode Plot ---
plt.figure()                                            # Create figure for magnitude plot
plt.semilogx(w, mag)                                    # Logarithmic x-axis of magnitude vs frequency
plt.title(f'Bode Plot - Magnitude\nFilter Type: {filter_type}')  # Title includes detected filter type
plt.xlabel('Frequency [rad/s]')                         # Label the x-axis
plt.ylabel('Magnitude [dB]')                            # Label the y-axis
plt.grid(True, which="both", ls="-")                    # Grid on all major and minor ticks, solid lines

# --- Phase Bode Plot ---
plt.figure()                                            # Create figure for phase plot
plt.semilogx(w, phase)                                  # Logarithmic x-axis of phase vs frequency
plt.title(f'Bode Plot - Phase\nFilter Type: {filter_type}')      # Title includes detected filter type
plt.xlabel('Frequency [rad/s]')                         # Label the x-axis
plt.ylabel('Phase [degrees]')                           # Label the y-axis
plt.grid(True, which="both", ls="-")                    # Grid on all major and minor ticks, solid lines

plt.show()                                              # Display both plots in pop-up windows
