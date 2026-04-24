#!/usr/bin/env python3
"""
Perf Profile Tool for SMT Workload Analysis (adaptado)

Agora gera DERIVED com:
- IPC
- Branches (count e %)
- Floating-point (count e %)
- Load (count e %)
- Store (count e %)
- Integer restante (count e %)
"""

import argparse
import os
import subprocess
import sys
import re
import json

DEFAULT_DURATION = 20

# Event name mappings
EVENT_NAMES = {
    "r103": "FP_ADD_SUB",
    "r203": "FP_MUL",
    "r403": "FP_DIV",
    "r803": "FP_MAC",
    "r0100": "FPU_PIPE_ASSIG_0",
    "r0200": "FPU_PIPE_ASSIG_1",
    "r0400": "FPU_PIPE_ASSIG_2",
    "r0800": "FPU_PIPE_ASSIG_3",
    "r129": "LOAD_DISPATCH",
    "r229": "STORE_DISPATCH",
    "r429": "LOAD_STORE_DISPATCH",
    "r1ae": "INT_REGISTER_STALL",
    "r20ae": "FP_REGISTER_STALL",
    "r2ae": "LOAD_QUEUE_STALL",
    "r4ae": "STORE_QUEUE_STALL",
    "r10ae": "TAKEN_BRANCH_QUEUE_STALL",
    "r1af": "INT_SCHED0_STALL",
    "r2af": "INT_SCHED1_STALL",
    "r4af": "INT_SCHED2_STALL",
    "r8af": "INT_SCHED3_STALL",
    "r40ae": "FP_SCHEDULER_STALL",
    "r20af": "RETIRE_TOKEN_STALL",
    "r8ab": "INT_DISP_IBS_MODE",
    "r4ab": "FP_DISP_IBS_MODE",
}

# Perf events to collect
STANDARD_EVENTS = [
    "instructions",
    "cycles",
    "branches",
    "branch-misses",
    "cache-references",
    "cache-misses",
    "context-switches",
    "cpu-migrations",
    "page-faults",
    "task-clock",
]

# FP events
FP_EVENTS = ["r103", "r203", "r403", "r803", "r0100", "r0200", "r0400", "r0800"]

# Memory events
MEM_EVENTS = ["r129", "r229", "r329"]

# Stall / IBS events
STALL_EVENTS = [
    "r1ae", "r20ae", "r2ae",
    "r1af", "r2af", "r4af", "r8af", "r40ae",
    "r8ab", "r4ab", "r20af"
]

PERF_EVENTS = STANDARD_EVENTS + FP_EVENTS + MEM_EVENTS + STALL_EVENTS

def parse_val(valstr: str) -> int:
    return int(re.sub(r"[^0-9]", "", valstr))

def execute():
    p = argparse.ArgumentParser(description="Profile workload with perf")
    p.add_argument("binary", help="Path to executable")
    p.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    p.add_argument("--cpu", type=int, default=0)
    p.add_argument("--events", help="Comma-separated perf events")
    args = p.parse_args()

    binary_path = args.binary
    duration = args.duration
    cpu = args.cpu

    if not os.path.isfile(binary_path) or not os.access(binary_path, os.X_OK):
        print(f"Error: binary not found/executable: {binary_path}")
        sys.exit(1)

    perf_events = PERF_EVENTS
    if args.events:
        perf_events = [e.strip() for e in args.events.split(",")]

    perf_cmd = ["taskset", "-c", str(cpu), "perf", "stat", "-e", ",".join(perf_events), binary_path, str(duration)]

    print(f"Running: {binary_path}")
    print(f"Duration: {duration}s, CPU: {cpu}")
    print(f"Collecting events: {', '.join([EVENT_NAMES.get(e, e) for e in perf_events])}\n")

    try:
        result = subprocess.run(perf_cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr

        # Replace raw codes with readable names
        for raw_code, name in EVENT_NAMES.items():
            output = output.replace(f"{raw_code}:u", f"{name}:u")
            output = output.replace(f"{raw_code} ", f"{name} ")

        # Parse counters
        counters = {}
        for line in output.splitlines():
            m = re.match(r"\s*([0-9\.,]+)\s+(\S+):u", line)
            if m:
                valstr, name = m.groups()
                counters[name] = parse_val(valstr)

        # ------------------------------------------------------------------
        # DERIVED: IPC e composição de instruções
        # ------------------------------------------------------------------
        instructions = counters.get("instructions", 0)
        cycles = counters.get("cycles", 0)
        branches = counters.get("branches",0)
        load = counters.get("LOAD_DISPATCH",0)
        store = counters.get("STORE_DISPATCH",0)
        FP_total = counters.get("FP_DISP_IBS_MODE", 0)
        INT_total = counters.get("INT_DISP_IBS_MODE", 0) - load - store - branches
        total_dispatch = FP_total + INT_total + load + store + branches

        derived = {}
        derived["IPC"] = instructions / cycles if instructions and cycles else None
        derived["FP_total"] = FP_total
        derived["FP_percent"] = 100 * FP_total / total_dispatch if total_dispatch else None
        derived["INT_rest"] = INT_total
        derived["INT_rest_percent"] = 100 * INT_total / total_dispatch if total_dispatch else None
        derived["Branches"] = branches
        derived["Branches_percent"] = 100*branches/instructions if instructions else None
        derived["Load"] = load
        derived["Load_percent"] = 100*load/instructions if instructions else None
        derived["Store"] = store
        derived["Store_percent"] = 100*store/instructions if instructions else None

        # ------------------------------------------------------------------
        # Organiza counters para PLOT_BUCKETS (stacked bar)
        # ------------------------------------------------------------------
        plot_buckets = {
            "FP": {k: counters.get(k,0) for k in ["FP_ADD_SUB","FP_MUL","FP_DIV","FP_MAC","FP_DISP_IBS_MODE"]},
            "INT": {k: counters.get(k,0) for k in [
                "INT_REGISTER_STALL","INT_SCHED0_STALL","INT_SCHED1_STALL",
                "INT_SCHED2_STALL","INT_SCHED3_STALL","LOAD_QUEUE_STALL",
                "RETIRE_TOKEN_STALL","INT_DISP_IBS_MODE"
            ]},
            "MEM": {
                "Load": load,
                "Store": store,
                "LOAD_STORE_DISPATCH": counters.get("LOAD_STORE_DISPATCH",0),
                "cache-references": counters.get("cache-references",0),
                "cache-misses": counters.get("cache-misses",0)
            },
            "ICACHE": {k: counters.get(k,0) for k in ["IC_HIT","IC_MISS","IC_ACCESS"]}
        }

        data = {
            "workload_name": os.path.basename(binary_path),
            "counters": counters,
            "DERIVED": derived,
            "PLOT_BUCKETS": plot_buckets
        }

        # Cria pasta profiles se não existir
        os.makedirs("profiles", exist_ok=True)
        json_filename = os.path.join("profiles", os.path.basename(binary_path) + ".json")
        with open(json_filename, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Profile saved to {json_filename}")

        print(json.dumps(data, indent=4))
        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    execute()
