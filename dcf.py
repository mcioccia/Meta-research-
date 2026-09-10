# ==============================================================================
# INPUTS (in USD millions, except rates and per-share counts)
# ==============================================================================
import sys

# Case selector: 'training' or 'meta'. 
# You can change RUN_CASE here, or pass 'meta' / 'training' on the command line:
#   python dcf.py          -> runs the active RUN_CASE
#   python dcf.py training -> runs the training case
#   python dcf.py meta     -> runs the Meta Platforms case
RUN_CASE = "training"
if len(sys.argv) > 1 and sys.argv[1].lower() in ["meta", "company"]:
    RUN_CASE = "meta"
elif len(sys.argv) > 1 and sys.argv[1].lower() == "training":
    RUN_CASE = "training"

if RUN_CASE == "training":
    # --------------------------------------------------------------------------
    # Training Case Inputs
    # --------------------------------------------------------------------------
    starting_fcff = 100.0                         # Starting FCFF (Year 0) in USD millions
    growth_rates = [0.08, 0.06, 0.05, 0.04, 0.03] # Yearly growth rates for Years 1 to 5
    wacc = 0.10                                   # Weighted Average Cost of Capital
    terminal_growth = 0.03                        # Terminal perpetual growth rate
    cash = 50.0                                   # Non-operating cash in USD millions
    debt = 300.0                                  # Total debt in USD millions
    shares = 50.0                                 # Diluted shares in millions

    # Editable lists for Sensitivity Grid
    grid_waccs = [0.09, 0.10, 0.11]
    grid_terminal_growths = [0.02, 0.03, 0.04]

    # Reverse DCF Target & Bisection Search Bounds
    target_share_price = 30.00
    reverse_dcf_lower_bound = -0.05               # -5 percentage points
    reverse_dcf_upper_bound = 0.10                # +10 percentage points

else:
    # --------------------------------------------------------------------------
    # Meta Platforms, Inc. (NASDAQ: META) Inputs
    # --------------------------------------------------------------------------
    starting_fcff = 46.66                         # Starting FCFF (Year 0) in USD billions
    growth_rates = [-0.60, 0.60, 0.40, 0.20, 0.10] # Growth scenario 2026-2030
    wacc = 0.094                                  # WACC 9.4%
    terminal_growth = 0.025                       # Terminal growth 2.5%
    cash = 81.592                                 # Cash & marketable securities in USD billions
    debt = 58.744                                 # Debt carrying value in USD billions
    shares = 2.574                                # Diluted shares in billions

    # Editable lists for Sensitivity Grid (centered on Meta base)
    grid_waccs = [0.084, 0.094, 0.104]
    grid_terminal_growths = [0.015, 0.025, 0.035]

    # Reverse DCF Target & Bisection Search Bounds
    target_share_price = 653.69                   # Today's market price
    reverse_dcf_lower_bound = -0.05               # -5 percentage points
    reverse_dcf_upper_bound = 0.30                # +30 percentage points (brackets $653.69)
# ==============================================================================

# Validation
if terminal_growth >= wacc:
    raise SystemExit(
        f"Error: Terminal growth rate ({terminal_growth:.4f}) must be strictly less "
        f"than WACC ({wacc:.4f}) for the Gordon Growth Model to converge."
    )

# 1. Five explicit years FCFF (annual end-of-year convention)
fcff = []
current_fcff = starting_fcff
for g in growth_rates:
    current_fcff *= (1.0 + g)
    fcff.append(current_fcff)

# 2. Present value of the five explicit FCFF
pv_explicit = sum(cf / ((1.0 + wacc) ** (i + 1)) for i, cf in enumerate(fcff))

# 3. Terminal value at the end of Year 5 (Gordon Growth Model using Year 6 FCFF)
fcff_6 = fcff[-1] * (1.0 + terminal_growth)
tv_5 = fcff_6 / (wacc - terminal_growth)

# 4. Present value of the terminal value (discounted 5 years)
pv_tv = tv_5 / ((1.0 + wacc) ** 5)

# 5. Enterprise value
ev = pv_explicit + pv_tv

# 6. Equity value (EV + cash - debt)
equity_val = ev + cash - debt

# 7. Value per diluted share
val_per_share = equity_val / shares

# 8. Present value of the terminal value as a share of enterprise value
tv_share_ev = pv_tv / ev

# Print twelve labelled lines to four decimals
print(f"FCFF Year 1: {fcff[0]:.4f}")
print(f"FCFF Year 2: {fcff[1]:.4f}")
print(f"FCFF Year 3: {fcff[2]:.4f}")
print(f"FCFF Year 4: {fcff[3]:.4f}")
print(f"FCFF Year 5: {fcff[4]:.4f}")
print(f"Present value of the five explicit FCFF: {pv_explicit:.4f}")
print(f"Terminal value at Year 5: {tv_5:.4f}")
print(f"Present value of the terminal value: {pv_tv:.4f}")
print(f"Enterprise value: {ev:.4f}")
print(f"Equity value: {equity_val:.4f}")
print(f"Value per diluted share: {val_per_share:.4f}")
print(f"Present value of the terminal value as a share of enterprise value: {tv_share_ev:.4f}")


# ==============================================================================
# SENSITIVITY GRID & REVERSE DCF HELPER FUNCTIONS
# ==============================================================================
def calculate_dcf_share_value(f0, g_list, discount_rate, term_g, c_val, d_val, s_count):
    """Calculates value per diluted share. Returns None if terminal growth >= WACC."""
    if term_g >= discount_rate:
        return None
    c_f = f0
    cfs = []
    for g in g_list:
        c_f *= (1.0 + g)
        cfs.append(c_f)
    pv_exp = sum(cf / ((1.0 + discount_rate) ** (i + 1)) for i, cf in enumerate(cfs))
    f_term = cfs[-1] * (1.0 + term_g)
    tv = f_term / (discount_rate - term_g)
    pv_t = tv / ((1.0 + discount_rate) ** len(cfs))
    enterprise_v = pv_exp + pv_t
    equity_v = enterprise_v + c_val - d_val
    return equity_v / s_count


# ==============================================================================
# SENSITIVITY GRID: Value per diluted share for combinations of WACC and g
# ==============================================================================
col_width = 12
header_title = "WACC \\ terminal growth"
print()
print(f"Sensitivity Grid: Value per diluted share ($/share) [{RUN_CASE}]")
grid_header = header_title.ljust(24) + "".join(f"{tg*100:.1f}%".rjust(col_width) for tg in grid_terminal_growths)
print(grid_header)
print("-" * len(grid_header))

for w in grid_waccs:
    row_str = f"{w*100:.1f}%".ljust(24)
    for tg in grid_terminal_growths:
        val = calculate_dcf_share_value(starting_fcff, growth_rates, w, tg, cash, debt, shares)
        if val is None:
            row_str += "Invalid".rjust(col_width)
        else:
            row_str += f"{val:.2f}".rjust(col_width)
    print(row_str)

# ==============================================================================
# REVERSE DCF: Solve for uniform growth rate shift via bisection
# ==============================================================================
print()
print(f"Reverse DCF: Solved uniform growth shift [{RUN_CASE}]")
print(f"Target share price: {target_share_price:.2f}")
print(f"Search bracket bounds: [{reverse_dcf_lower_bound*100:+.2f}%, {reverse_dcf_upper_bound*100:+.2f}%]")

# 1. Refuse any bracket that pushes an annual growth rate to -100% or below
min_annual_rate = min(
    min(g + reverse_dcf_lower_bound for g in growth_rates),
    min(g + reverse_dcf_upper_bound for g in growth_rates)
)
if min_annual_rate <= -1.0:
    print(f"Refused bracket: search bracket pushes an annual growth rate to -100% or below (minimum rate: {min_annual_rate*100:.2f}%).")
else:
    # 2. Evaluate target price feasibility inside the bracket
    val_lower = calculate_dcf_share_value(
        starting_fcff, [g + reverse_dcf_lower_bound for g in growth_rates],
        wacc, terminal_growth, cash, debt, shares
    )
    val_upper = calculate_dcf_share_value(
        starting_fcff, [g + reverse_dcf_upper_bound for g in growth_rates],
        wacc, terminal_growth, cash, debt, shares
    )

    if val_lower is None or val_upper is None:
        print("Invalid model parameters: Gordon Growth model does not converge at bounds.")
    elif target_share_price < val_lower or target_share_price > val_upper:
        print(f"No solution in that bracket: target price ({target_share_price:.2f}) cannot be reached inside bounds [{reverse_dcf_lower_bound*100:+.2f}%, {reverse_dcf_upper_bound*100:+.2f}%]")
        print(f"  (Implied share price range in bracket: {val_lower:.2f} to {val_upper:.2f}; never returning a bound as an answer).")
    else:
        # 3. Bisection search
        low = reverse_dcf_lower_bound
        high = reverse_dcf_upper_bound
        tolerance = 1e-7
        for _ in range(100):
            mid = (low + high) / 2.0
            v_mid = calculate_dcf_share_value(
                starting_fcff, [g + mid for g in growth_rates],
                wacc, terminal_growth, cash, debt, shares
            )
            if abs(v_mid - target_share_price) < tolerance or (high - low) / 2.0 < tolerance:
                break
            if v_mid < target_share_price:
                low = mid
            else:
                high = mid

        solved_shift = (low + high) / 2.0
        print(f"Solved shift on every growth rate: {solved_shift*100:+.2f} percentage points ({solved_shift:+.4f})")

print("Inputs held fixed:")
print(f"  - Starting FCFF: {starting_fcff}")
print(f"  - Base growth rates (Years 1-5): {[f'{g*100:+.1f}%' for g in growth_rates]}")
print(f"  - WACC: {wacc*100:.2f}%")
print(f"  - Terminal perpetual growth rate: {terminal_growth*100:.2f}%")
print(f"  - Cash: {cash}")
print(f"  - Debt: {debt}")
print(f"  - Diluted shares: {shares}")