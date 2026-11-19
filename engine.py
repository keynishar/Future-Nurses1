"""
Career Venture Lab - Core Business & Precalculus Engine
Team: Future Nurses | Pathway: NUR-2 (Nurse-Led Health Education Simulation)
Course: Precalculus | Level: Advanced
"""

from __future__ import annotations
import copy
import json
import math
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple

MONEY_QUANT = Decimal("0.01")


def to_money(value: Any) -> Decimal:
    """Convert any numeric input safely into exact 2-decimal USD money."""
    if isinstance(value, Decimal):
        return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def money_float(value: Any) -> float:
    """Convert Decimal money to float strictly for display/charting."""
    return float(to_money(value))


def create_default_snapshot(
    team_id: str = "Future Nurses",
    selected_level: str = "Advanced",
    random_seed: int = 2027,
) -> Dict[str, Any]:
    """Create the initial post-startup business record for NUR-2."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "team_id": team_id,
        "course": "Precalculus",
        "pathway_id": "NUR-2",
        "business_name": "Nurse-Led Health Education Simulation",
        "snapshot_id": "SNAP-NUR2-V1",
        "state_version": 1,
        "simulation_date": "2027-01-01",
        "base_period": "monthly",
        "working_days": 20,
        "currency": "USD",
        "random_seed": random_seed,
        "level_by_skill": {
            "average_cost_rational": selected_level,
            "composed_price_demand_profit": selected_level,
            "seasonal_trig_demand": selected_level,
        },
        "selected_level": selected_level,
        "assumptions": [
            "Fictional nonclinical health and wellness education workshops only (no diagnosis or patient data).",
            "Payment is collected and per-seat expenses apply only to attended workshop seats.",
            "Baseline demand D0 = 80 seats/month at base price p0 = $25/seat.",
            "Seasonal demand extension assumes 12-month cycle peaking in month t=4 (+20%) and dipping in month t=10 (-20%).",
            "Depreciation, taxes, and customer credit are disabled at baseline.",
        ],
        "sources": [
            "Career Venture Lab Student Handbook (NUR-2 Pathway & Precalculus Adapter, Nov 2026)"
        ],
        "offerings": [
            {
                "offering_id": "OFF-NUR-01",
                "name": "General wellness education workshop",
                "unit": "workshop seat",
                "price": 25.00,
                "is_primary": True,
                "active": True,
            },
            {
                "offering_id": "OFF-NUR-02",
                "name": "Caregiver information session",
                "unit": "workshop seat",
                "price": 25.00,
                "is_primary": False,
                "active": False,
            },
            {
                "offering_id": "OFF-NUR-03",
                "name": "First-aid awareness demonstration",
                "unit": "workshop seat",
                "price": 25.00,
                "is_primary": False,
                "active": False,
            },
        ],
        "funding": {
            "owner_contribution": 6000.00,
            "grant_funding": 0.00,
            "loan_balance": 0.00,
            "equipment_assets": 1500.00,
            "pre_opening_expense": 500.00,
            "opening_inventory": 0.00,
            "opening_cash": 4000.00,
            "current_cash": 4000.00,
            "retained_earnings": -500.00,
            "funding_date": "2027-01-01",
            "loan_terms": "No active loan at startup (0% APR)",
        },
        "inputs": {
            "base_price": 25.00,
            "D0": 80,
            "staff_hours": 30.0,
            "hours_per_unit": 0.5,
            "venue_seats": 60,
            "no_show_rate": 0.0,
            "satisfaction_mean": 4.0,
            "requested_demand": 80,
            "marketing_spend": 0.00,
            "refund_amount": 0.00,
            "new_owner_cash": 0.00,
            "loan_proceeds": 0.00,
            "loan_principal_repayment": 0.00,
            "interest_expense": 0.00,
            "additional_capex": 0.00,
        },
        "cost_lines": {
            "variable_per_seat": {
                "educator_delivery": 2.00,
                "materials": 2.00,
                "cleaning_consumables": 1.00,
            },
            "monthly_fixed": {
                "venue": 250.00,
                "scheduling_software": 100.00,
                "accessibility_support": 200.00,
                "admin_insurance_assumption": 150.00,
            },
        },
        "capacity": {
            "staff_capacity": 60,
            "venue_capacity": 60,
            "effective_capacity": 60,
            "limiting_factor": "Balanced (Staff = 60, Venue = 60)",
        },
        "processed_run_ids": [],
        "ledger": [
            {
                "transaction_id": "TXN-INIT-001",
                "run_id": "INIT-STARTUP",
                "date": "2027-01-01",
                "event_type": "STARTUP_FINANCING",
                "category": "Owner Contribution & Startup Setup",
                "amount": 4000.00,
                "quantity": 1,
                "unit_price": 4000.00,
                "offering_id": "N/A",
                "campaign_id": "N/A",
                "financing_type": "Owner Equity ($6,000) - Gear ($1,500) - Setup ($500)",
                "state_version": 1,
                "notes": "Post-startup spendable cash ready for Month 1.",
            }
        ],
        "campaigns": [],
        "decisions": [],
        "created_at": now_iso,
    }


def compute_variable_unit_cost(cost_lines: Dict[str, Any]) -> Decimal:
    return sum((to_money(v) for v in cost_lines["variable_per_seat"].values()), Decimal("0.00"))


def compute_fixed_monthly_cost(cost_lines: Dict[str, Any]) -> Decimal:
    return sum((to_money(v) for v in cost_lines["monthly_fixed"].values()), Decimal("0.00"))


def compute_capacity(
    staff_hours: float,
    hours_per_unit: float,
    venue_seats: int,
    capacity_override: Optional[int] = None,
) -> Dict[str, Any]:
    """Calculate maximum workshop seats allowed by staff time and room seats."""
    if capacity_override is not None:
        eff = max(0, int(capacity_override))
        return {
            "staff_capacity": math.floor(staff_hours / hours_per_unit) if hours_per_unit > 0 else 0,
            "venue_capacity": int(venue_seats),
            "effective_capacity": eff,
            "limiting_factor": "Fixture Test Override",
        }

    if hours_per_unit <= 0:
        raise ValueError("hours_per_unit must be greater than 0.")
    if staff_hours < 0 or venue_seats < 0:
        raise ValueError("staff_hours and venue_seats must be nonnegative.")

    staff_cap = math.floor(float(staff_hours) / float(hours_per_unit))
    venue_cap = int(venue_seats)
    eff = min(staff_cap, venue_cap)

    if staff_cap < venue_cap:
        bottleneck = f"Educator Hours ({staff_cap} seats max)"
    elif venue_cap < staff_cap:
        bottleneck = f"Room Seats ({venue_cap} seats max)"
    else:
        bottleneck = f"Balanced ({eff} seats max)"

    return {
        "staff_capacity": staff_cap,
        "venue_capacity": venue_cap,
        "effective_capacity": eff,
        "limiting_factor": bottleneck,
    }


def simulate_month_step(
    snapshot: Dict[str, Any],
    sim_date: str,
    run_id: str,
    requested_demand: Optional[int] = None,
    capacity_override: Optional[int] = None,
    marketing_override: Optional[float] = None,
    commit_to_ledger: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
    """
    Run one deterministic monthly simulation step for NUR-2.
    Returns (updated_snapshot, step_summary, was_duplicate_run).
    """
    state = copy.deepcopy(snapshot)

    if commit_to_ledger and run_id in state.get("processed_run_ids", []):
        return state, {"duplicate": True, "run_id": run_id}, True

    inp = state["inputs"]
    price = to_money(inp["base_price"])
    req = int(inp["requested_demand"] if requested_demand is None else requested_demand)
    if req < 0:
        raise ValueError("Requested demand cannot be negative.")

    no_show = float(inp["no_show_rate"])
    if not (0.0 <= no_show <= 1.0):
        raise ValueError("No-show rate must be between 0 and 1.")

    cap_info = compute_capacity(
        staff_hours=float(inp["staff_hours"]),
        hours_per_unit=float(inp["hours_per_unit"]),
        venue_seats=int(inp["venue_seats"]),
        capacity_override=capacity_override,
    )
    eff_cap = cap_info["effective_capacity"]

    booked = min(req, eff_cap)
    unserved_demand = max(0, req - booked)
    attended = math.floor(booked * (1.0 - no_show))
    no_show_seats = booked - attended
    sold = attended

    var_unit = compute_variable_unit_cost(state["cost_lines"])
    fixed_cost = compute_fixed_monthly_cost(state["cost_lines"])
    marketing = to_money(inp["marketing_spend"] if marketing_override is None else marketing_override)
    refunds = to_money(inp.get("refund_amount", 0.0))

    gross_revenue = to_money(price * Decimal(sold))
    net_revenue = to_money(gross_revenue - refunds)
    variable_expense = to_money(var_unit * Decimal(sold))
    total_operating_expense = to_money(variable_expense + fixed_cost + marketing)
    operating_profit = to_money(net_revenue - total_operating_expense)

    interest = to_money(inp.get("interest_expense", 0.0))
    net_profit = to_money(operating_profit - interest)

    # Financing & Capital Equipment cash items (never counted as sales revenue or operating expense)
    new_owner_cash = to_money(inp.get("new_owner_cash", 0.0))
    loan_cash = to_money(inp.get("loan_proceeds", 0.0))
    principal = to_money(inp.get("loan_principal_repayment", 0.0))
    capex = to_money(inp.get("additional_capex", 0.0))

    opening_cash = to_money(state["funding"]["current_cash"])
    ending_cash = to_money(
        opening_cash
        + net_revenue
        - variable_expense
        - fixed_cost
        - marketing
        - interest
        - principal
        - capex
        + new_owner_cash
        + loan_cash
    )

    hours_used = float(sold) * float(inp["hours_per_unit"])
    staff_hours_avail = float(inp["staff_hours"])
    utilization_pct = (hours_used / staff_hours_avail * 100.0) if staff_hours_avail > 0 else 0.0

    summary = {
        "duplicate": False,
        "run_id": run_id,
        "date": sim_date,
        "mode": "Fixture Override Mode" if capacity_override is not None else "Normal Resource Mode",
        "price": money_float(price),
        "requested": req,
        "effective_capacity": eff_cap,
        "limiting_factor": cap_info["limiting_factor"],
        "booked": booked,
        "unserved_demand": unserved_demand,
        "no_show_seats": no_show_seats,
        "attended": attended,
        "sold": sold,
        "revenue": money_float(net_revenue),
        "variable_per_unit": money_float(var_unit),
        "variable_expense": money_float(variable_expense),
        "fixed_expense": money_float(fixed_cost),
        "marketing_expense": money_float(marketing),
        "total_expense": money_float(total_operating_expense),
        "operating_profit": money_float(operating_profit),
        "interest_expense": money_float(interest),
        "net_profit": money_float(net_profit),
        "opening_cash": money_float(opening_cash),
        "ending_cash": money_float(ending_cash),
        "utilization_pct": round(utilization_pct, 1),
        "accessibility_cost": money_float(to_money(state["cost_lines"]["monthly_fixed"]["accessibility_support"])),
    }

    if commit_to_ledger:
        new_version = int(state["state_version"]) + 1
        state["state_version"] = new_version
        state["snapshot_id"] = f"SNAP-NUR2-V{new_version}"
        state["simulation_date"] = sim_date
        state["capacity"] = cap_info
        state["funding"]["current_cash"] = money_float(ending_cash)
        state["funding"]["loan_balance"] = money_float(
            to_money(state["funding"]["loan_balance"]) + loan_cash - principal
        )
        state["funding"]["owner_contribution"] = money_float(
            to_money(state["funding"]["owner_contribution"]) + new_owner_cash
        )
        state["funding"]["equipment_assets"] = money_float(
            to_money(state["funding"]["equipment_assets"]) + capex
        )
        state["funding"]["retained_earnings"] = money_float(
            to_money(state["funding"]["retained_earnings"]) + net_profit
        )
        state["processed_run_ids"].append(run_id)

        tx_base = len(state["ledger"]) + 1
        state["ledger"].append(
            {
                "transaction_id": f"TXN-{new_version:03d}-{tx_base:03d}",
                "run_id": run_id,
                "date": sim_date,
                "event_type": "WORKSHOP_SALES",
                "category": "Attended Workshop Seats",
                "amount": money_float(net_revenue),
                "quantity": sold,
                "unit_price": money_float(price),
                "offering_id": "OFF-NUR-01",
                "campaign_id": "N/A",
                "financing_type": "Operating Revenue",
                "state_version": new_version,
                "notes": f"Requested={req}, Booked={booked}, Attended={attended}, Unserved={unserved_demand}",
            }
        )
        state["ledger"].append(
            {
                "transaction_id": f"TXN-{new_version:03d}-{tx_base + 1:03d}",
                "run_id": run_id,
                "date": sim_date,
                "event_type": "OPERATING_EXPENSE",
                "category": "Variable + Fixed + Marketing Expenses",
                "amount": -money_float(total_operating_expense),
                "quantity": sold,
                "unit_price": money_float(var_unit),
                "offering_id": "OFF-NUR-01",
                "campaign_id": "CAMP-FIXTURE" if marketing > 0 else "N/A",
                "financing_type": "Operating Expense",
                "state_version": new_version,
                "notes": f"Var=${money_float(variable_expense):.2f}, Fixed=${money_float(fixed_cost):.2f}, Ad=${money_float(marketing):.2f}",
            }
        )
        if loan_cash > 0 or principal > 0 or new_owner_cash > 0 or capex > 0 or interest > 0:
            net_fin = new_owner_cash + loan_cash - principal - capex - interest
            state["ledger"].append(
                {
                    "transaction_id": f"TXN-{new_version:03d}-{tx_base + 2:03d}",
                    "run_id": run_id,
                    "date": sim_date,
                    "event_type": "FINANCING_AND_CAPEX",
                    "category": "Loans / Equity / Gear Purchases",
                    "amount": money_float(net_fin),
                    "quantity": 1,
                    "unit_price": money_float(net_fin),
                    "offering_id": "N/A",
                    "campaign_id": "N/A",
                    "financing_type": "Financing / Capital Asset",
                    "state_version": new_version,
                    "notes": f"LoanIn={loan_cash}, PrincipalOut={principal}, Interest={interest}, CapEx={capex}, OwnerIn={new_owner_cash}",
                }
            )

    return state, summary, False


# === PRECALCULUS MATHEMATICAL FUNCTIONS ===

def precalc_average_cost(s: int | float, fixed_cost: float, variable_cost: float) -> Optional[float]:
    """Foundation: Average cost A(s) = F/s + v for 0 < s <= capacity. Undefined at s = 0."""
    if s <= 0:
        return None
    return (float(fixed_cost) / float(s)) + float(variable_cost)


def precalc_composed_price_model(
    p: float,
    p0: float,
    D0: int,
    capacity: int,
    fixed_cost: float,
    variable_cost: float,
) -> Dict[str, Any]:
    """
    Applied: Function composition on 0 <= p <= 2*p0.
    q(p) = max(0, 2*D0 - (D0/p0)*p)
    s(p) = min(capacity, q(p))
    R(p) = p * s(p)
    C(s(p)) = F + v * s(p)
    P(p) = R(p) - C(s(p))
    """
    slope = float(D0) / float(p0)
    raw_demand = max(0.0, 2.0 * float(D0) - slope * float(p))
    continuous_sales = min(float(capacity), raw_demand)
    integer_sales = math.floor(continuous_sales)

    cont_rev = float(p) * continuous_sales
    cont_cost = float(fixed_cost) + float(variable_cost) * continuous_sales
    cont_profit = cont_rev - cont_cost

    int_rev = float(p) * integer_sales
    int_cost = float(fixed_cost) + float(variable_cost) * integer_sales
    int_profit = int_rev - int_cost

    breakpoint_p = float(p0) * (2.0 - (float(capacity) / float(D0))) if D0 > 0 else None

    return {
        "price": round(float(p), 2),
        "raw_demand_continuous": round(raw_demand, 2),
        "realized_sales_continuous": round(continuous_sales, 2),
        "realized_sales_integer": integer_sales,
        "revenue_continuous": round(cont_rev, 2),
        "cost_continuous": round(cont_cost, 2),
        "profit_continuous": round(cont_profit, 2),
        "revenue_integer": round(int_rev, 2),
        "cost_integer": round(int_cost, 2),
        "profit_integer": round(int_profit, 2),
        "capacity_breakpoint_price": round(breakpoint_p, 2) if breakpoint_p is not None else None,
    }


def precalc_seasonal_trig_series(
    D0: int,
    capacity: int,
    price: float,
    fixed_cost: float,
    variable_cost: float,
    amplitude: float = 0.20,
) -> List[Dict[str, Any]]:
    """
    Advanced: Seasonal trigonometric demand model D(t) = D0 * (1 + 0.20 * sin(2*pi*(t - 1)/12))
    for month index t = 1..12 (peak at t=4 -> 1.2*D0, minimum at t=10 -> 0.8*D0).
    """
    month_names = [
        "Month 1 (Jan)", "Month 2 (Feb)", "Month 3 (Mar)", "Month 4 (Apr - Peak)",
        "Month 5 (May)", "Month 6 (Jun)", "Month 7 (Jul)", "Month 8 (Aug)",
        "Month 9 (Sep)", "Month 10 (Oct - Low)", "Month 11 (Nov)", "Month 12 (Dec)",
    ]
    rows = []
    for t in range(1, 13):
        seasonal_demand_cont = float(D0) * (1.0 + amplitude * math.sin(2.0 * math.pi * (t - 1) / 12.0))
        seasonal_demand_int = round(seasonal_demand_cont)
        realized_sales_int = min(int(capacity), seasonal_demand_int)
        unserved = max(0, seasonal_demand_int - realized_sales_int)
        rev = float(price) * realized_sales_int
        cost = float(fixed_cost) + float(variable_cost) * realized_sales_int
        profit = rev - cost
        rows.append(
            {
                "month_index": t,
                "month_label": month_names[t - 1],
                "seasonal_demand_continuous": round(seasonal_demand_cont, 2),
                "seasonal_demand_rounded": seasonal_demand_int,
                "capacity_limit": int(capacity),
                "realized_sales": realized_sales_int,
                "unserved_demand": unserved,
                "projected_revenue": round(rev, 2),
                "projected_cost": round(cost, 2),
                "projected_profit": round(profit, 2),
            }
        )
    return rows


# === SNAPSHOT EXPORT & VALIDATION ===

def export_snapshot_json(snapshot: Dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2)


def validate_and_import_snapshot(
    raw_json: str,
    expected_team_id: str,
    current_state_version: int,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate imported JSON snapshot.
    Rejects wrong team_id, wrong pathway, missing required fields, or stale state_version.
    """
    try:
        data = json.loads(raw_json)
    except Exception as exc:
        return False, f"Invalid JSON file format: {exc}", None

    required_keys = [
        "team_id", "course", "pathway_id", "snapshot_id", "state_version",
        "simulation_date", "currency", "funding", "inputs", "cost_lines", "ledger",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"Rejected: Saved file is missing required fields: {', '.join(missing)}.", None

    if data.get("team_id") != expected_team_id:
        return (
            False,
            f"Rejected: Team ID mismatch (file belongs to '{data.get('team_id')}', expected '{expected_team_id}').",
            None,
        )

    if data.get("pathway_id") != "NUR-2":
        return (
            False,
            f"Rejected: Pathway mismatch (file is '{data.get('pathway_id')}', expected 'NUR-2').",
            None,
        )

    imported_ver = int(data.get("state_version", 0))
    if imported_ver < current_state_version:
        return (
            False,
            f"Rejected: Stale version detected (file is v{imported_ver}, current dashboard is v{current_state_version}).",
            None,
        )

    if float(data["funding"].get("current_cash", -1)) < 0:
        return False, "Rejected: Negative cash balance is not valid.", None

    return True, f"Loaded snapshot {data['snapshot_id']} (Version {imported_ver}) successfully.", data
