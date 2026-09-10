# ==============================================================================
# INPUTS (in USD billions, except rates and per-share counts)
# ==============================================================================
starting_fcff = 46.66                         # Starting FCFF (Year 0) in USD billions
growth_rates = [-0.60, 0.60, 0.40, 0.20, 0.10] # Yearly growth rates for Years 1 to 5 (2026-2030)
wacc = 0.094                                  # Weighted Average Cost of Capital (9.4%)
terminal_growth = 0.025                       # Terminal perpetual growth rate (2.5%)
cash = 81.592                                 # Cash and marketable securities in USD billions
debt = 58.744                                 # Total debt (bond carrying value) in USD billions
shares = 2.574                                # Diluted shares in billions
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