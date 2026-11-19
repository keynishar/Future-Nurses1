"""
Career Venture Lab — Stage 1 Business Dashboard
Team: Future Nurses | Course: Precalculus | Pathway: NUR-2 | Level: Advanced
"""

from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
import sys
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import (
    compute_capacity,
    compute_fixed_monthly_cost,
    compute_variable_unit_cost,
    create_default_snapshot,
    export_snapshot_json,
    precalc_average_cost,
    precalc_composed_price_model,
    precalc_seasonal_trig_series,
    simulate_month_step,
    validate_and_import_snapshot,
)

st.set_page_config(
    page_title="Future Nurses | NUR-2 Business Dashboard",
    page_icon="🩺",
    layout="wide",
)

# Initialize session state
if "snapshot" not in st.session_state:
    st.session_state["snapshot"] = create_default_snapshot(
        team_id="Future Nurses",
        selected_level="Advanced",
    )

snap = st.session_state["snapshot"]

# === PERSISTENT TOP BANNER & SIDEBAR MATH SKILLS PANEL ===
st.title("🩺 Nurse-Led Health Education Studio (NUR-2)")
st.caption(
    f"Team: **{snap['team_id']}** | Math Class: **{snap['course']}** | "
    f"Approved Difficulty: **{snap['selected_level']}** | "
    f"Saved File Version: **{snap['snapshot_id']} (v{snap['state_version']})**"
)
st.info(
    "**Simulation Guardrail:** This is a fictional nonclinical health and wellness education business "
    "(workshops and info sessions only). It does not model medical diagnosis, treatment, or real patient data."
)

with st.sidebar:
    st.header("📐 Math & Challenge Level")
    st.markdown(
        "**Active Course:** Precalculus  \n"
        "**Business Model:** NUR-2 (Health Education Workshops)  \n"
        "**Current Version:** `v" + str(snap["state_version"]) + "`"
    )
    level_choice = st.selectbox(
        "Difficulty Level (Teacher-Approved)",
        options=["Foundation", "Applied", "Advanced"],
        index=["Foundation", "Applied", "Advanced"].index(snap["selected_level"]),
        help="Switching levels updates the equations, graphs, and math questions on the Math Screen.",
    )
    if level_choice != snap["selected_level"]:
        snap["selected_level"] = level_choice
        for k in snap["level_by_skill"]:
            snap["level_by_skill"][k] = level_choice
        st.rerun()

    st.divider()
    st.subheader("🧭 Build Stages")
    st.success("✅ **Stage 1 Active:** Control Screen, Math, Receipt Book & Save File")
    st.markdown(
        "- 🔒 **Stage 2:** 4 AI Team Helpers, Business Reports & Ad Studio\n"
        "- 🔒 **Stage 3:** Other School Subjects & Practice Quiz Maker\n"
        "- 🔒 **Stage 4 (Optional):** Practice Online Shop"
    )

    st.divider()
    st.subheader("💾 Quick Save File")
    st.download_button(
        label="⬇️ Download Saved Business File (.json)",
        data=export_snapshot_json(snap),
        file_name=f"future_nurses_nur2_v{snap['state_version']}.json",
        mime="application/json",
        use_container_width=True,
    )

# Compute live preview metrics from current inputs (What-If Preview)
var_unit = float(compute_variable_unit_cost(snap["cost_lines"]))
fixed_month = float(compute_fixed_monthly_cost(snap["cost_lines"]))
cap_info = compute_capacity(
    staff_hours=snap["inputs"]["staff_hours"],
    hours_per_unit=snap["inputs"]["hours_per_unit"],
    venue_seats=snap["inputs"]["venue_seats"],
)
_, preview_step, _ = simulate_month_step(
    snap,
    sim_date=snap["simulation_date"],
    run_id="LIVE-PREVIEW",
    commit_to_ledger=False,
)

# === NAVIGATION TABS ===
tab_overview, tab_inputs, tab_math, tab_ops_ledger, tab_save_tests = st.tabs(
    [
        "1. Overview",
        "2. Starting Money & Bills",
        "3. Precalculus Math Screen",
        "4. Workshop Limits & Receipt Book",
        "5. Save / Load & Stage 1 Tests",
    ]
)

# ---------------------------------------------------------
# TAB 1: OVERVIEW
# ---------------------------------------------------------
with tab_overview:
    st.subheader("Business Health Snapshot (Plain-English Summary)")
    st.markdown(
        "The top row shows your **actual saved bank balance**, while the preview below shows what would happen "
        "in a single month using your current sliders (**What-If Preview — not yet recorded in your receipt book**)."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Spendable Cash in Bank (Saved)",
        f"${snap['funding']['current_cash']:,.2f}",
        help="Actual cash available after startup gear and recorded months.",
    )
    c2.metric(
        "Max Seats Per Month (Capacity)",
        f"{cap_info['effective_capacity']} seats",
        help=f"Limited by: {cap_info['limiting_factor']}",
    )
    c3.metric(
        "What-If Monthly Profit",
        f"${preview_step['operating_profit']:,.2f}",
        delta=f"{preview_step['attended']} attended seats @ ${snap['inputs']['base_price']:.2f}",
    )
    c4.metric(
        "Unserved Requests (Turned Away)",
        f"{preview_step['unserved_demand']} seats",
        help="Customers who wanted a seat when the room or educator schedule was already full.",
    )

    st.divider()
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("#### 📊 What-If Monthly Money Breakdown (Starts at $0)")
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    name="Amount ($ USD)",
                    x=["Money Earned (Revenue)", "Per-Seat Bills", "Monthly Fixed Bills", "Ad Spend", "Operating Profit"],
                    y=[
                        preview_step["revenue"],
                        preview_step["variable_expense"],
                        preview_step["fixed_expense"],
                        preview_step["marketing_expense"],
                        preview_step["operating_profit"],
                    ],
                    marker_color=["#1f4e78", "#5b9bd5", "#7f7f7f", "#ed7d31", "#2e75b6"],
                    text=[
                        f"${preview_step['revenue']:,.0f}",
                        f"${preview_step['variable_expense']:,.0f}",
                        f"${preview_step['fixed_expense']:,.0f}",
                        f"${preview_step['marketing_expense']:,.0f}",
                        f"${preview_step['operating_profit']:,.0f}",
                    ],
                    textposition="outside",
                )
            ]
        )
        fig_bar.update_layout(
            yaxis_title="Dollars ($ USD)",
            yaxis=dict(rangemode="tozero"),
            height=360,
            margin=dict(t=30, b=30),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption(
            f"Label: What-If Projection | Snapshot: {snap['snapshot_id']} | "
            f"Assumptions: Price=${snap['inputs']['base_price']:.2f}, Requested={snap['inputs']['requested_demand']}, "
            f"Capacity={cap_info['effective_capacity']} seats | Generated: {datetime.now().strftime('%Y-%m-%d')}"
        )

    with col_right:
        st.markdown("#### 🗺️ How Your Business Pieces Connect")
        st.markdown(
            """
            1. **Starting Money & Bills** sets your cash, ticket price, educator hours, and room seats.
            2. **Workshop Limits** caps sign-ups at your smallest limit (educator hours or 60 room seats) and subtracts no-shows.
            3. **Precalculus Math Screen** tests how ticket prices and busy/slow seasons change profit.
            4. **Receipt Book** records each approved month once so nothing gets counted twice.
            5. **Save File** lets you download your progress and reload it after refreshing.
            """
        )
        st.warning(
            f"**Current Bottleneck (Slowest Limit):** {cap_info['limiting_factor']}  \n"
            f"**Educator Time Used:** {preview_step['utilization_pct']}% of {snap['inputs']['staff_hours']} hrs/month"
        )

# ---------------------------------------------------------
# TAB 2: STARTING MONEY & BILLS (INPUTS & FUNDING)
# ---------------------------------------------------------
with tab_inputs:
    st.subheader("Editable Workshop Inputs, Bills & Starting Money")
    st.markdown(
        "Adjust any number below to test how your Nurse-Led Health Education Studio behaves. "
        "Remember: **changing inputs here updates your What-If Preview**. To record an official month into your "
        "receipt book, use Tab 4."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 1. Workshop Ticket Price, Demand & Room Limits")
        snap["inputs"]["base_price"] = st.number_input(
            "Workshop Ticket Price ($ per seat)",
            min_value=1.0,
            max_value=500.0,
            value=float(snap["inputs"]["base_price"]),
            step=1.0,
        )
        snap["inputs"]["D0"] = st.number_input(
            "Baseline Monthly Demand at Base Price (D0 seats)",
            min_value=0,
            max_value=1000,
            value=int(snap["inputs"]["D0"]),
            step=5,
        )
        snap["inputs"]["requested_demand"] = st.slider(
            "Customers Requesting Seats This Month",
            min_value=0,
            max_value=200,
            value=int(snap["inputs"]["requested_demand"]),
            step=1,
        )
        snap["inputs"]["staff_hours"] = st.number_input(
            "Educator Productive Hours Available / Month",
            min_value=0.0,
            max_value=500.0,
            value=float(snap["inputs"]["staff_hours"]),
            step=1.0,
        )
        snap["inputs"]["hours_per_unit"] = st.number_input(
            "Educator Hours Needed per Seat",
            min_value=0.1,
            max_value=10.0,
            value=float(snap["inputs"]["hours_per_unit"]),
            step=0.1,
        )
        snap["inputs"]["venue_seats"] = st.number_input(
            "Maximum Room Seats Available / Month",
            min_value=0,
            max_value=500,
            value=int(snap["inputs"]["venue_seats"]),
            step=5,
        )
        snap["inputs"]["no_show_rate"] = st.slider(
            "Booked Seat No-Show Rate (0.00 = everyone shows up, 0.20 = 20% miss class)",
            min_value=0.0,
            max_value=1.0,
            value=float(snap["inputs"]["no_show_rate"]),
            step=0.05,
        )

    with col_b:
        st.markdown("#### 2. Per-Seat Bills & Regular Monthly Bills")
        v_lines = snap["cost_lines"]["variable_per_seat"]
        v_lines["educator_delivery"] = st.number_input(
            "Educator Delivery Cost ($ per attended seat)",
            min_value=0.0,
            value=float(v_lines["educator_delivery"]),
            step=0.5,
        )
        v_lines["materials"] = st.number_input(
            "Workshop Handouts & Materials ($ per attended seat)",
            min_value=0.0,
            value=float(v_lines["materials"]),
            step=0.5,
        )
        v_lines["cleaning_consumables"] = st.number_input(
            "Room Cleaning & Supplies ($ per attended seat)",
            min_value=0.0,
            value=float(v_lines["cleaning_consumables"]),
            step=0.5,
        )
        st.caption(f"**Total Per-Seat Cost:** ${float(compute_variable_unit_cost(snap['cost_lines'])):.2f} / seat")

        f_lines = snap["cost_lines"]["monthly_fixed"]
        f_lines["venue"] = st.number_input(
            "Monthly Room Rental ($/month)",
            min_value=0.0,
            value=float(f_lines["venue"]),
            step=10.0,
        )
        f_lines["scheduling_software"] = st.number_input(
            "Scheduling Software ($/month)",
            min_value=0.0,
            value=float(f_lines["scheduling_software"]),
            step=10.0,
        )
        f_lines["accessibility_support"] = st.number_input(
            "Accessibility & Translation Support ($/month — required explicit line)",
            min_value=0.0,
            value=float(f_lines["accessibility_support"]),
            step=10.0,
        )
        f_lines["admin_insurance_assumption"] = st.number_input(
            "Admin & Insurance Assumption ($/month)",
            min_value=0.0,
            value=float(f_lines["admin_insurance_assumption"]),
            step=10.0,
        )
        snap["inputs"]["marketing_spend"] = st.number_input(
            "Own-Business Advertising Spend ($/month)",
            min_value=0.0,
            value=float(snap["inputs"]["marketing_spend"]),
            step=10.0,
        )
        st.caption(f"**Total Fixed Monthly Bills:** ${float(compute_fixed_monthly_cost(snap['cost_lines'])):.2f} / month")

    st.divider()
    st.markdown("#### 3. Startup Money & Optional Loans (Separated from Sales Revenue)")
    st.caption(
        "Accounting Rule: Loans and owner cash add to your bank balance, NOT sales revenue. "
        "Buying big equipment reduces cash, while paying loan interest counts as an expense."
    )
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Owner Startup Contribution", f"${snap['funding']['owner_contribution']:,.2f}")
    fc2.metric("Startup Equipment Assets", f"${snap['funding']['equipment_assets']:,.2f}")
    fc3.metric("Pre-Opening Setup Cost", f"${snap['funding']['pre_opening_expense']:,.2f}")
    fc4.metric("Active Loan Balance", f"${snap['funding']['loan_balance']:,.2f}")

    lc1, lc2, lc3, lc4 = st.columns(4)
    snap["inputs"]["loan_proceeds"] = lc1.number_input("New Loan Received ($)", min_value=0.0, value=float(snap["inputs"]["loan_proceeds"]), step=100.0)
    snap["inputs"]["loan_principal_repayment"] = lc2.number_input("Loan Principal Repaid ($)", min_value=0.0, value=float(snap["inputs"]["loan_principal_repayment"]), step=100.0)
    snap["inputs"]["interest_expense"] = lc3.number_input("Loan Interest Paid ($)", min_value=0.0, value=float(snap["inputs"]["interest_expense"]), step=10.0)
    snap["inputs"]["additional_capex"] = lc4.number_input("New Equipment Purchase ($)", min_value=0.0, value=float(snap["inputs"]["additional_capex"]), step=100.0)

# ---------------------------------------------------------
# TAB 3: PRECALCULUS MATH SCREEN
# ---------------------------------------------------------
with tab_math:
    active_lvl = snap["selected_level"]
    p0 = float(snap["inputs"]["base_price"])
    D0 = int(snap["inputs"]["D0"])
    cap = int(cap_info["effective_capacity"])
    F = float(compute_fixed_monthly_cost(snap["cost_lines"]))
    v = float(compute_variable_unit_cost(snap["cost_lines"]))

    st.subheader(f"Precalculus Math Screen — {active_lvl} Level")

    # Transfer Check Box (required by handbook p. 6)
    with st.expander("🧠 Transfer Check: Predict Before You Move a Slider", expanded=True):
        tc1, tc2 = st.columns(2)
        user_pred = tc1.text_input(
            "Step 1: Type your prediction before changing inputs (e.g., 'At $35 per seat, demand drops below 60 so the room is no longer full'):",
            key="transfer_prediction",
        )
        tc2.markdown(
            "**Step 2: Check against the graph & table below.**  \n"
            + (f"Your saved prediction: _{user_pred}_" if user_pred else "_Enter a prediction on the left, then test it below._")
        )

    if active_lvl == "Foundation":
        st.markdown(
            f"""
            **Named Skill:** Average Cost as a Rational Function  
            **Business Question:** How does the cost per workshop seat drop as more people fill our {cap}-seat limit?  
            **Equations:**  
            - Total Monthly Cost: `C(s) = {F:.0f} + {v:.2f}s` (dollars)  
            - Average Cost per Seat: `A(s) = C(s) / s = {F:.0f}/s + {v:.2f}` (dollars per seat)  
            **Practical Domain:** `0 < s <= {cap}` whole seats (`s = 0` is **Undefined** because you cannot divide ${F:.0f} by 0 seats).  
            **Asymptotes:** Vertical asymptote at `s = 0` (cost per seat shoots up toward infinity as attendance nears zero); Horizontal asymptote at `y = ${v:.2f}` (as seats grow, fixed bills per person shrink toward $0, leaving the ${v:.2f} per-seat cost).
            """
        )

        if cap <= 0:
            st.error("Capacity is 0 seats. Increase educator hours or venue seats to view the average cost curve.")
        else:
            seats_list = list(range(1, cap + 1))
            avg_costs = [round(precalc_average_cost(s, F, v), 2) for s in seats_list]
            tot_costs = [round(F + v * s, 2) for s in seats_list]
            df_avg = pd.DataFrame(
                {
                    "Seats Sold (s)": seats_list,
                    "Total Cost C(s) ($)": tot_costs,
                    "Average Cost A(s) ($/seat)": avg_costs,
                }
            )

            selected_s = st.slider("Inspect a specific seat count on the curve & table:", 1, cap, cap)
            sel_avg = precalc_average_cost(selected_s, F, v)

            fig_f = go.Figure()
            fig_f.add_trace(
                go.Scatter(
                    x=seats_list,
                    y=avg_costs,
                    mode="lines+markers",
                    name="Average Cost A(s) ($/seat)",
                    line=dict(color="#1f4e78", width=3),
                )
            )
            fig_f.add_hline(
                y=v,
                line_dash="dash",
                line_color="#595959",
                annotation_text=f"Horizontal Asymptote y = ${v:.2f}/seat",
            )
            fig_f.add_trace(
                go.Scatter(
                    x=[selected_s],
                    y=[round(sel_avg, 2)],
                    mode="markers",
                    name=f"Selected: {selected_s} seats (${sel_avg:.2f}/seat)",
                    marker=dict(size=14, color="#ed7d31", symbol="diamond"),
                )
            )
            fig_f.update_layout(
                title=f"Average Cost per Seat A(s) = {F:.0f}/s + {v:.2f} (A(0) = Undefined)",
                xaxis_title="Attended Workshop Seats (s)",
                yaxis_title="Average Cost ($ per seat)",
                height=380,
            )
            st.plotly_chart(fig_f, use_container_width=True)
            st.caption(
                f"Snapshot: {snap['snapshot_id']} | Equation: A(s) = {F:.0f}/s + {v:.2f} | Domain: 0 < s <= {cap} | "
                f"At capacity s={cap}: A({cap}) = ${precalc_average_cost(cap, F, v):.2f}/seat"
            )

            def highlight_row_f(row):
                return ["background-color: #fff2cc; font-weight: bold" if row["Seats Sold (s)"] == selected_s else "" for _ in row]

            st.dataframe(df_avg.style.apply(highlight_row_f, axis=1), use_container_width=True, height=240)
            st.download_button("⬇️ Download Table (CSV)", df_avg.to_csv(index=False), "nur2_foundation_avg_cost.csv", "text/csv")

    elif active_lvl == "Applied":
        slope = D0 / p0 if p0 > 0 else 0.0
        bp_price = p0 * (2.0 - cap / D0) if D0 > 0 else 0.0
        st.markdown(
            f"""
            **Named Skill:** Function Composition (`Price -> Demand -> Capped Sales -> Profit`)  
            **Business Question:** How does changing our ticket price `p` affect customer sign-ups, our {cap}-seat limit, and monthly profit?  
            **Equations (on price domain `$0 <= p <= ${2*p0:.2f}`):**  
            - Customer Demand: `q(p) = max(0, {2*D0} - {slope:.2f}p)`  
            - Capped Workshop Sales: `s(p) = min({cap}, q(p))`  
            - Composed Revenue & Cost: `R(p) = p * s(p)` and `C(s(p)) = {F:.0f} + {v:.2f} * s(p)`  
            - Capacity Breakpoint Price: `p = ${bp_price:.2f}` (below this price, more than {cap} people want seats, so sales stay capped at {cap}).
            """
        )

        max_p = max(10, int(round(2 * p0)))
        prices = list(range(0, max_p + 1, 5))
        if int(round(p0)) not in prices:
            prices.append(int(round(p0)))
        prices = sorted(set(prices))

        rows_app = [precalc_composed_price_model(float(pr), p0, D0, cap, F, v) for pr in prices]
        df_app = pd.DataFrame(rows_app)

        sel_price = st.slider("Inspect a specific ticket price ($):", min_value=0, max_value=max_p, value=int(round(p0)), step=5)
        sel_detail = precalc_composed_price_model(float(sel_price), p0, D0, cap, F, v)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Demand q(p)", f"{sel_detail['raw_demand_continuous']:.1f} seats")
        m2.metric("Realized Sales s(p)", f"{sel_detail['realized_sales_integer']} whole seats")
        m3.metric("Continuous Profit", f"${sel_detail['profit_continuous']:,.2f}")
        m4.metric("Whole-Seat Profit", f"${sel_detail['profit_integer']:,.2f}")

        fig_a = go.Figure()
        fig_a.add_trace(
            go.Scatter(
                x=df_app["price"],
                y=df_app["profit_continuous"],
                mode="lines+markers",
                name="Composed Profit P(p) (Continuous)",
                line=dict(color="#1f4e78", width=3),
            )
        )
        fig_a.add_trace(
            go.Scatter(
                x=df_app["price"],
                y=df_app["revenue_continuous"],
                mode="lines",
                name="Composed Revenue R(p)",
                line=dict(color="#2e75b6", dash="dash"),
            )
        )
        fig_a.add_hline(y=0, line_color="#000000", line_width=1, annotation_text="Break-Even Line ($0 Profit)")
        if 0 <= bp_price <= max_p:
            fig_a.add_vline(
                x=bp_price,
                line_dash="dot",
                line_color="#ed7d31",
                annotation_text=f"Capacity Corner p=${bp_price:.2f}",
            )
        fig_a.update_layout(
            title="Composed Revenue & Profit vs. Ticket Price (with Capacity Ceiling)",
            xaxis_title="Ticket Price p ($ per seat)",
            yaxis_title="Dollars ($ USD)",
            height=400,
        )
        st.plotly_chart(fig_a, use_container_width=True)
        st.caption(
            f"Snapshot: {snap['snapshot_id']} | Domain: 0 <= p <= {2*p0:.0f} | Breakpoint: p=${bp_price:.2f} | "
            "Note: Smooth curve shows continuous composition; table compares continuous values vs. integer seat sales."
        )

        def highlight_row_a(row):
            return ["background-color: #fff2cc; font-weight: bold" if int(round(row["price"])) == sel_price else "" for _ in row]

        st.dataframe(df_app.style.apply(highlight_row_a, axis=1), use_container_width=True, height=260)
        st.download_button("⬇️ Download Table (CSV)", df_app.to_csv(index=False), "nur2_applied_composition.csv", "text/csv")

    else:  # Advanced
        st.markdown(
            f"""
            **Named Skill:** Seasonal Trigonometric Demand Model with Capacity Clipping  
            **Business Question:** When community workshop demand rises and falls across the 12-month school/calendar year, how often do we hit our {cap}-seat limit, and how does that affect profit?  
            **Equation:** `D(t) = {D0} * (1 + 0.20 * sin(2*pi*(t - 1)/12))` for month `t = 1..12`  
            - **Period:** 12 months | **Peak Month:** `t = 4` (`1.20 * {D0} = {1.2*D0:.1f}` seats) | **Lowest Month:** `t = 10` (`0.80 * {D0} = {0.8*D0:.1f}` seats)  
            - **Realized Sales:** `s(t) = min({cap}, round(D(t)))`  
            **Assumptions & Extrapolation Limits:** Assumes a smooth ±20% seasonal wave around baseline demand `D0 = {D0}` at price `${p0:.2f}`. Real community attendance can shift due to school holidays, weather, or outreach campaigns.
            """
        )

        seasonal_rows = precalc_seasonal_trig_series(D0=D0, capacity=cap, price=p0, fixed_cost=F, variable_cost=v)
        df_adv = pd.DataFrame(seasonal_rows)

        sel_month = st.slider("Inspect a specific month index (t = 1 to 12):", 1, 12, 4)
        sel_m_row = seasonal_rows[sel_month - 1]

        am1, am2, am3, am4 = st.columns(4)
        am1.metric(f"{sel_m_row['month_label']} Demand", f"{sel_m_row['seasonal_demand_continuous']:.1f} seats")
        am2.metric("Realized Sales (Clipped)", f"{sel_m_row['realized_sales']} seats")
        am3.metric("Unserved Demand", f"{sel_m_row['unserved_demand']} seats")
        am4.metric("Projected Monthly Profit", f"${sel_m_row['projected_profit']:,.2f}")

        fig_adv = go.Figure()
        fig_adv.add_trace(
            go.Scatter(
                x=df_adv["month_index"],
                y=df_adv["seasonal_demand_continuous"],
                mode="lines+markers",
                name="Unclipped Seasonal Demand D(t)",
                line=dict(color="#ed7d31", width=3, dash="dash"),
                marker=dict(symbol="circle", size=8),
            )
        )
        fig_adv.add_trace(
            go.Scatter(
                x=df_adv["month_index"],
                y=df_adv["realized_sales"],
                mode="lines+markers",
                name="Capacity-Clipped Sales s(t)",
                line=dict(color="#1f4e78", width=3),
                marker=dict(symbol="square", size=9),
            )
        )
        fig_adv.add_hline(
            y=cap,
            line_dash="dot",
            line_color="#595959",
            annotation_text=f"Capacity Limit ({cap} seats)",
        )
        fig_adv.update_layout(
            title=f"12-Month Seasonal Demand D(t) vs. Capacity-Clipped Sales (D0={D0}, Cap={cap})",
            xaxis_title="Month Index t (1 to 12)",
            yaxis_title="Workshop Seats",
            xaxis=dict(tickmode="linear", dtick=1),
            height=400,
        )
        st.plotly_chart(fig_adv, use_container_width=True)
        st.caption(
            f"Snapshot: {snap['snapshot_id']} | Equation: D(t) = {D0}*(1 + 0.20*sin(2*pi*(t-1)/12)) | "
            f"Peak t=4 ({1.2*D0:.0f} seats), Low t=10 ({0.8*D0:.0f} seats) | Clipped at Capacity = {cap} seats"
        )

        def highlight_row_adv(row):
            return ["background-color: #fff2cc; font-weight: bold" if row["month_index"] == sel_month else "" for _ in row]

        st.dataframe(df_adv.style.apply(highlight_row_adv, axis=1), use_container_width=True, height=280)
        st.download_button("⬇️ Download 12-Month Table (CSV)", df_adv.to_csv(index=False), "nur2_advanced_seasonal.csv", "text/csv")

    st.info(
        "**Interpretation Check:** What changed when you moved the slider? What stayed fixed? "
        "Why does higher seasonal demand in Month 4 (`t=4`) NOT increase profit once our 60-seat limit is reached?"
    )

# ---------------------------------------------------------
# TAB 4: WORKSHOP LIMITS & RECEIPT BOOK (OPERATIONS & LEDGER)
# ---------------------------------------------------------
with tab_ops_ledger:
    st.subheader("Workshop Operations & Dated Receipt Book (Ledger)")
    st.markdown(
        "Use this screen to advance your simulation by one month and record an official entry in your **Receipt Book**. "
        "Each step requires a unique **Run ID** so clicking twice never counts the same month twice."
    )

    col_op1, col_op2 = st.columns([1, 1.3])

    with col_op1:
        st.markdown("#### Record a New Simulation Month")
        next_month_num = len(snap["processed_run_ids"]) + 1
        default_date = f"2027-{min(12, next_month_num):02d}-28"
        default_run_id = f"RUN-NUR2-{next_month_num:03d}"

        step_date = st.text_input("Simulation Date (YYYY-MM-DD)", value=default_date)
        step_run_id = st.text_input("Unique Run ID (Duplicate Protection)", value=default_run_id)

        if st.button("✅ Approve & Record Month in Receipt Book", type="primary", use_container_width=True):
            updated_snap, step_res, is_dup = simulate_month_step(
                snap,
                sim_date=step_date,
                run_id=step_run_id.strip(),
                commit_to_ledger=True,
            )
            if is_dup:
                st.error(f"Duplicate Run Blocked: `{step_run_id}` was already recorded! No new transaction was created.")
            else:
                st.session_state["snapshot"] = updated_snap
                st.success(
                    f"Recorded `{step_run_id}`: Sold {step_res['sold']} seats, Revenue ${step_res['revenue']:,.2f}, "
                    f"Profit ${step_res['operating_profit']:,.2f}, New Cash ${step_res['ending_cash']:,.2f}."
                )
                st.rerun()

    with col_op2:
        st.markdown("#### Current Month Operations Check (What-If Preview)")
        op_df = pd.DataFrame(
            [
                {"Step": "1. Customers Requesting Seats", "Seats": preview_step["requested"], "Notes": "Requested demand (not yet revenue)"},
                {"Step": "2. Maximum Workshop Limit", "Seats": preview_step["effective_capacity"], "Notes": preview_step["limiting_factor"]},
                {"Step": "3. Booked Seats", "Seats": preview_step["booked"], "Notes": f"Unserved demand: {preview_step['unserved_demand']} seats"},
                {"Step": "4. No-Shows Missed", "Seats": preview_step["no_show_seats"], "Notes": f"No-show rate: {snap['inputs']['no_show_rate']*100:.0f}%"},
                {"Step": "5. Attended & Paid Seats (Sold)", "Seats": preview_step["attended"], "Notes": f"Revenue: ${preview_step['revenue']:,.2f}"},
            ]
        )
        st.table(op_df)

    st.divider()
    st.markdown("#### 📒 Dated Receipt Book (Actual Recorded Transactions)")
    df_ledger = pd.DataFrame(snap["ledger"])
    st.dataframe(df_ledger, use_container_width=True)
    st.download_button(
        "⬇️ Export Receipt Book as CSV",
        data=df_ledger.to_csv(index=False),
        file_name=f"future_nurses_ledger_v{snap['state_version']}.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# TAB 5: SAVE / LOAD & STAGE 1 TESTS
# ---------------------------------------------------------
with tab_save_tests:
    st.subheader("Save / Load Business File & Stage 1 Verification Checks")

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("#### 💾 Save or Reset Business State")
        st.download_button(
            label="⬇️ Save Business File (JSON Snapshot)",
            data=export_snapshot_json(snap),
            file_name=f"future_nurses_nur2_v{snap['state_version']}.json",
            mime="application/json",
            use_container_width=True,
        )
        if st.button("🔄 Reset to Post-Startup Baseline ($4,000 Cash)", use_container_width=True):
            st.session_state["snapshot"] = create_default_snapshot(
                team_id="Future Nurses",
                selected_level=snap["selected_level"],
            )
            st.success("Reset to post-startup baseline ($4,000 spendable cash, Version 1).")
            st.rerun()

    with sc2:
        st.markdown("#### 📂 Restore Saved Business File (With Version & Team Checks)")
        uploaded_json = st.file_uploader("Upload a saved Future Nurses JSON file", type=["json"])
        if uploaded_json is not None:
            raw_text = uploaded_json.read().decode("utf-8")
            if st.button("📥 Validate & Load Uploaded File", use_container_width=True):
                ok, msg, restored = validate_and_import_snapshot(
                    raw_text,
                    expected_team_id=snap["team_id"],
                    current_state_version=snap["state_version"],
                )
                if ok and restored is not None:
                    st.session_state["snapshot"] = restored
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    st.markdown("#### ✅ Run Stage 1 Handbook Acceptance Checks")
    st.markdown(
        "Click the button below to verify all required **NUR-2** and **Precalculus** checks against the exact "
        "expected numbers in the Career Venture Lab Student Handbook."
    )

    if st.button("▶️ Run All Stage 1 Verification Checks", type="primary"):
        results = []

        # Check 1: Zero sales & A(0) undefined
        s_zero = create_default_snapshot("Future Nurses")
        _, r_zero, _ = simulate_month_step(s_zero, "2027-01-31", "CHK-ZERO", requested_demand=0, commit_to_ledger=False)
        a_zero = precalc_average_cost(0, 700.0, 5.0)
        results.append(
            {
                "Test": "1. Zero Sales & Division-by-Zero Guard",
                "Expected": "Rev=$0, Var=$0, Profit=-$700, A(0)=None",
                "Actual": f"Rev=${r_zero['revenue']:.0f}, Var=${r_zero['variable_expense']:.0f}, Profit=${r_zero['operating_profit']:.0f}, A(0)={a_zero}",
                "Status": "PASS" if (r_zero["revenue"] == 0 and r_zero["operating_profit"] == -700 and a_zero is None) else "FAIL",
            }
        )

        # Check 2: Demand exceeds capacity (80 requested vs 60 capacity)
        s_cap = create_default_snapshot("Future Nurses")
        _, r_cap, _ = simulate_month_step(s_cap, "2027-01-31", "CHK-CAP", requested_demand=80, commit_to_ledger=False)
        results.append(
            {
                "Test": "2. Demand Exceeds Capacity (80 vs 60)",
                "Expected": "Sold=60, Unserved=20",
                "Actual": f"Sold={r_cap['sold']}, Unserved={r_cap['unserved_demand']}",
                "Status": "PASS" if (r_cap["sold"] == 60 and r_cap["unserved_demand"] == 20) else "FAIL",
            }
        )

        # Check 3: NUR-2 No-show rate = 0.20
        s_ns = create_default_snapshot("Future Nurses")
        s_ns["inputs"]["no_show_rate"] = 0.20
        _, r_ns, _ = simulate_month_step(s_ns, "2027-01-31", "CHK-NS", requested_demand=80, commit_to_ledger=False)
        results.append(
            {
                "Test": "3. NUR-2 No-Show Rate = 20%",
                "Expected": "Booked=60, Attended=48, Rev=$1,200, Var=$240, Profit=$260",
                "Actual": f"Booked={r_ns['booked']}, Attended={r_ns['attended']}, Rev=${r_ns['revenue']:.0f}, Var=${r_ns['variable_expense']:.0f}, Profit=${r_ns['operating_profit']:.0f}",
                "Status": "PASS" if (r_ns["attended"] == 48 and r_ns["revenue"] == 1200 and r_ns["operating_profit"] == 260) else "FAIL",
            }
        )

        # Check 4: 3-Month Fixture Replay
        s_fix = create_default_snapshot("Future Nurses")
        base_dir = Path(__file__).resolve().parent
        fixture_file = base_dir / "sample_data" / "monthly_fixture.csv"
        if not fixture_file.exists():
            fixture_file = base_dir / "monthly_fixture.csv"
        with open(fixture_file, newline="") as f:
            f_rows = list(csv.DictReader(f))
        cash_trail = []
        for row in f_rows:
            s_fix, r_fix, _ = simulate_month_step(
                s_fix,
                sim_date=f"{row['month']}-28",
                run_id=f"FIX-{row['month']}",
                requested_demand=int(row["requested"]),
                capacity_override=int(row["capacity_override"]),
                marketing_override=float(row["ad_cost"]),
                commit_to_ledger=True,
            )
            cash_trail.append(r_fix["ending_cash"])
        results.append(
            {
                "Test": "4. 3-Month Fixture Replay (monthly_fixture.csv)",
                "Expected": "Closing Cash = [$4,500, $4,900, $5,100]",
                "Actual": f"Closing Cash = {[f'${c:,.0f}' for c in cash_trail]}",
                "Status": "PASS" if cash_trail == [4500.0, 4900.0, 5100.0] else "FAIL",
            }
        )

        # Check 5: Precalculus Math Checks (A(60), Seasonal t=4 & t=10)
        a_60 = round(precalc_average_cost(60, 700.0, 5.0), 2)
        seas = precalc_seasonal_trig_series(80, 60, 25.0, 700.0, 5.0)
        d_t4 = seas[3]["seasonal_demand_continuous"]
        d_t10 = seas[9]["seasonal_demand_continuous"]
        results.append(
            {
                "Test": "5. Precalculus Math Checks (A(60), Seasonal t=4 & t=10)",
                "Expected": "A(60)=$16.67, D(4)=96.0, D(10)=64.0",
                "Actual": f"A(60)=${a_60:.2f}, D(4)={d_t4:.1f}, D(10)={d_t10:.1f}",
                "Status": "PASS" if (a_60 == 16.67 and abs(d_t4 - 96.0) < 1e-6 and abs(d_t10 - 64.0) < 1e-6) else "FAIL",
            }
        )

        # Check 6: Duplicate Run & Stale/Wrong-Team Rejection
        _, _, is_dup = simulate_month_step(s_fix, "2027-03-28", "FIX-2027-03", commit_to_ledger=True)
        bad_team, _, _ = validate_and_import_snapshot(export_snapshot_json(s_fix), "Wrong Team", s_fix["state_version"])
        bad_ver, _, _ = validate_and_import_snapshot(export_snapshot_json(s_fix), "Future Nurses", s_fix["state_version"] + 1)
        results.append(
            {
                "Test": "6. Duplicate Run & Stale/Wrong-Team Rejection",
                "Expected": "Duplicate blocked, Wrong team rejected, Stale version rejected",
                "Actual": f"DupBlocked={is_dup}, WrongTeamRejected={not bad_team}, StaleRejected={not bad_ver}",
                "Status": "PASS" if (is_dup and not bad_team and not bad_ver) else "FAIL",
            }
        )

        df_results = pd.DataFrame(results)
        st.table(df_results)
        if all(r["Status"] == "PASS" for r in results):
            st.success("🎉 All 6 Stage 1 acceptance checks PASSED!")
        else:
            st.error("One or more checks failed. Review the table above.")
