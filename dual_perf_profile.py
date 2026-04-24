#!/usr/bin/env python3
"""
Run perf on two workloads simultaneously on the same physical CPU SMT,
collecting all events and mapping raw codes to readable names.
"""

import argparse
import subprocess
import os
import sys
import re
from utils import get_unique_smt_groups

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

DEFAULT_DURATION = 20

def parse_val(valstr: str) -> int:
    return int(re.sub(r"[^0-9]", "", valstr))

def run_perf(binary, cpu, duration):
    perf_cmd = [
        "taskset", "-c", str(cpu),
        "perf", "stat", "-e", ",".join(PERF_EVENTS),
        binary, str(duration)
    ]
    result = subprocess.run(perf_cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr

    # Replace raw codes with readable names
    for raw_code, name in EVENT_NAMES.items():
        output = output.replace(f"{raw_code}:u", f"{name}:u")
        output = output.replace(f"{raw_code} ", f"{name} ")

    return output

def execute_two_binaries(bin1, bin2, duration):
    smt_groups = get_unique_smt_groups()
    if not smt_groups:
        print("No SMT groups found on this system.")
        sys.exit(1)

    # Pick first SMT group
    smt_cpu_ids = smt_groups[0]
    cpu1, cpu2 = smt_cpu_ids[:2]  # two threads of same physical CPU

    print(f"Running workloads on the same physical CPU SMT threads: {cpu1} & {cpu2}")
    print(f"Running:\n  {bin1}\n  {bin2}\nfor {duration}s...\n")

    # Start both binaries
    p1 = subprocess.Popen(
        ["taskset", "-c", str(cpu1), "perf", "stat", "-e", ",".join(PERF_EVENTS), bin1, str(duration)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    p2 = subprocess.Popen(
        ["taskset", "-c", str(cpu2), "perf", "stat", "-e", ",".join(PERF_EVENTS), bin2, str(duration)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    out1, err1 = p1.communicate()
    out2, err2 = p2.communicate()

    # Map raw codes to readable names
    for raw_code, name in EVENT_NAMES.items():
        err1 = err1.replace(f"{raw_code}:u", f"{name}:u").replace(f"{raw_code} ", f"{name} ")
        err2 = err2.replace(f"{raw_code}:u", f"{name}:u").replace(f"{raw_code} ", f"{name} ")

    print(f"\n=== {os.path.basename(bin1)} perf results ===")
    print(err1)

    print(f"\n=== {os.path.basename(bin2)} perf results ===")
    print(err2)

def main():
    parser = argparse.ArgumentParser(description="Run perf on two workloads on same SMT CPU")
    parser.add_argument("binary1", help="Path to first executable")
    parser.add_argument("binary2", help="Path to second executable")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    args = parser.parse_args()

    if not os.path.isfile(args.binary1) or not os.access(args.binary1, os.X_OK):
        print(f"Error: binary not found/executable: {args.binary1}")
        sys.exit(1)
    if not os.path.isfile(args.binary2) or not os.access(args.binary2, os.X_OK):
        print(f"Error: binary not found/executable: {args.binary2}")
        sys.exit(1)

    execute_two_binaries(args.binary1, args.binary2, args.duration)

if __name__ == "__main__":
    main()