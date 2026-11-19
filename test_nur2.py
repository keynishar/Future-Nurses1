"""
Automated Stage 1 Verification Tests (pytest + standalone Python compatible)
Team: Future Nurses | Course: Precalculus | Pathway: NUR-2 | Level: Advanced
"""

import csv
import math
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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


def test_baseline_defaults_and_costs():
    snap = create_default_snapshot(team_id="Future Nurses", selected_level="Advanced")
    assert snap["funding"]["opening_cash"] == 4000.00
    assert snap["funding"]["owner_contribution"] == 6000.00
    assert float(compute_variable_unit_cost(snap["cost_lines"])) == 5.00
    assert float(compute_fixed_monthly_cost(snap["cost_lines"])) == 700.00
    cap = compute_capacity(30.0, 0.5, 60)
    assert cap["effective_capacity"] == 60


def test_three_month_fixture_replay():
    snap = create_default_snapshot(team_id="Future Nurses", selected_level="Advanced")
    fixture_path = ROOT_DIR / "sample_data" / "monthly_fixture.csv"
    if not fixture_path.exists():
        fixture_path = Path(__file__).resolve().parent / "monthly_fixture.csv"
    with open(fixture_path, newline="") as f:
        rows = list(csv.DictReader(f))

    expected = [
        {"sold": 60, "revenue": 1500.00, "total_expense": 1000.00, "profit": 500.00, "ending_cash": 4500.00},
        {"sold": 60, "revenue": 1500.00, "total_expense": 1100.00, "profit": 400.00, "ending_cash": 4900.00},
        {"sold": 45, "revenue": 1125.00, "total_expense": 925.00, "profit": 200.00, "ending_cash": 5100.00},
    ]

    for idx, row in enumerate(rows):
        snap, summary, dup = simulate_month_step(
            snap,
            sim_date=f"{row['month']}-28",
            run_id=f"FIXTURE-{row['month']}",
            requested_demand=int(row["requested"]),
            capacity_override=int(row["capacity_override"]),
            marketing_override=float(row["ad_cost"]),
            commit_to_ledger=True,
        )
        assert not dup
        assert summary["sold"] == expected[idx]["sold"]
        assert summary["revenue"] == expected[idx]["revenue"]
        assert summary["total_expense"] == expected[idx]["total_expense"]
        assert summary["operating_profit"] == expected[idx]["profit"]
        assert summary["ending_cash"] == expected[idx]["ending_cash"]


def test_no_show_rate_20_percent():
    snap = create_default_snapshot(team_id="Future Nurses")
    snap["inputs"]["no_show_rate"] = 0.20
    _, summary, _ = simulate_month_step(
        snap,
        sim_date="2027-01-31",
        run_id="TEST-NOSHOW",
        requested_demand=80,
        commit_to_ledger=False,
    )
    assert summary["booked"] == 60
    assert summary["attended"] == 48
    assert summary["revenue"] == 1200.00
    assert summary["variable_expense"] == 240.00
    assert summary["operating_profit"] == 260.00


def test_zero_sales_and_division_by_zero_guard():
    snap = create_default_snapshot(team_id="Future Nurses")
    _, summary, _ = simulate_month_step(
        snap,
        sim_date="2027-01-31",
        run_id="TEST-ZERO",
        requested_demand=0,
        commit_to_ledger=False,
    )
    assert summary["revenue"] == 0.00
    assert summary["variable_expense"] == 0.00
    assert summary["operating_profit"] == -700.00
    assert precalc_average_cost(0, 700.0, 5.0) is None


def test_loan_accounting_rules():
    snap = create_default_snapshot(team_id="Future Nurses")
    snap["inputs"]["loan_proceeds"] = 1000.00
    _, summary, _ = simulate_month_step(
        snap,
        sim_date="2027-01-31",
        run_id="TEST-LOAN",
        requested_demand=80,
        commit_to_ledger=False,
    )
    assert summary["revenue"] == 1500.00
    assert summary["operating_profit"] == 500.00
    assert summary["ending_cash"] == 5500.00


def test_precalculus_math_checks():
    assert precalc_average_cost(0, 700.0, 5.0) is None
    assert round(precalc_average_cost(60, 700.0, 5.0), 2) == 16.67

    comp = precalc_composed_price_model(p=31.25, p0=25.0, D0=80, capacity=60, fixed_cost=700.0, variable_cost=5.0)
    assert comp["capacity_breakpoint_price"] == 31.25
    assert comp["raw_demand_continuous"] == 60.0

    seasonal = precalc_seasonal_trig_series(D0=80, capacity=60, price=25.0, fixed_cost=700.0, variable_cost=5.0)
    assert math.isclose(seasonal[3]["seasonal_demand_continuous"], 96.0, abs_tol=1e-6)
    assert math.isclose(seasonal[9]["seasonal_demand_continuous"], 64.0, abs_tol=1e-6)


def test_duplicate_run_and_snapshot_validation():
    snap = create_default_snapshot(team_id="Future Nurses")
    snap, _, dup1 = simulate_month_step(snap, "2027-01-31", "RUN-001", commit_to_ledger=True)
    assert not dup1
    ledger_len = len(snap["ledger"])

    snap, _, dup2 = simulate_month_step(snap, "2027-01-31", "RUN-001", commit_to_ledger=True)
    assert dup2
    assert len(snap["ledger"]) == ledger_len

    exported = export_snapshot_json(snap)

    ok_team, _, _ = validate_and_import_snapshot(exported, expected_team_id="Other Team", current_state_version=snap["state_version"])
    assert not ok_team

    ok_stale, _, _ = validate_and_import_snapshot(exported, expected_team_id="Future Nurses", current_state_version=snap["state_version"] + 1)
    assert not ok_stale

    ok_valid, _, restored = validate_and_import_snapshot(exported, expected_team_id="Future Nurses", current_state_version=snap["state_version"])
    assert ok_valid
    assert restored["funding"]["current_cash"] == snap["funding"]["current_cash"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS: {name}")
