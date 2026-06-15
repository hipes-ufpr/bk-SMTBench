from __future__ import annotations

from _bootstrap import ensure_project_root

PROJECT_ROOT = ensure_project_root()

import argparse
import os
import subprocess
import time

from utils import get_unique_smt_groups, read_workloads_from_bin

DEFAULT_ITERATIONS = 3
DEFAULT_DURATION = 10
NICE = -20
RES_SOLO_FOLDER = "solo"
RES_COMB_FOLDER = "comb"


def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[i]
        yield tuple(pool[i] for i in indices)


def execute():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"number of iterations for each test (default {DEFAULT_ITERATIONS})",
    )
    p.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help=f"duration in seconds of each run (default {DEFAULT_DURATION})",
    )
    p.add_argument("--bin", default="./bin", help="bin dir (default ./bin)")
    p.add_argument("--res", default="./res", help="res dir (default ./res)")
    p.add_argument(
        "--identifier",
        help="Experiment identifier. (Just a nametag)",
    )
    args = p.parse_args()

    num_iterations = args.iterations
    duration = args.duration
    experiment_identifier = args.identifier or input("Experiment identifier: ")
    bin_folder = args.bin
    res_folder = args.res

    if not os.path.isdir(bin_folder) or not os.listdir(bin_folder):
        print(f'Missing binaries at {bin_folder}. Maybe you need to run "make"?')
        exit(-1)

    os.makedirs(res_folder, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    experiment_dir = os.path.join(res_folder, f"{experiment_identifier}_{timestamp}")
    experiment_solo_dir = os.path.join(experiment_dir, RES_SOLO_FOLDER)
    experiment_comb_dir = os.path.join(experiment_dir, RES_COMB_FOLDER)
    os.makedirs(experiment_dir, exist_ok=False)
    os.makedirs(experiment_solo_dir, exist_ok=False)
    os.makedirs(experiment_comb_dir, exist_ok=False)
    print(f"Results will be saved in: {experiment_dir}\n")

    version_full_text = subprocess.run(
        ["gcc", "--version"], capture_output=True, text=True
    ).stdout.splitlines()[0]

    cpus = get_unique_smt_groups()
    cpu0, cpu1 = cpus[0]

    lines = [
        f"Experiment identifier: {experiment_identifier}",
        f"Iterations: {num_iterations}",
        f"Duration: {duration}",
        f"Executables folder: {bin_folder}",
        f"Results folder: {res_folder}",
        f"Experiment folder: {experiment_dir}",
        f"GCC version: {version_full_text}",
        f"Using only the physical core: SMT pair = ({cpu0}, {cpu1})",
    ]
    print("\n".join(lines))
    with open(os.path.join(experiment_dir, "info.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Executing experiments...")
    binaries = read_workloads_from_bin(bin_folder, keep_extension=True)
    total_binaries = len(binaries)
    print(f"{total_binaries} executables found..")
    binary_pairs = list(combinations(binaries, 2))
    total_combinations = len(binary_pairs) * num_iterations
    print(f"{total_combinations} binaries combinations..")

    total_planned_executions = total_binaries + total_combinations
    print(f"Total number of planned executions: {total_planned_executions}\n")

    estimated_total_seconds = float(total_planned_executions * float(duration))
    print(f"Estimated total time: ~{estimated_total_seconds / 60:.2f} minutes")

    start_time = time.time()
    current_run = 0

    for it in range(num_iterations):
        for bin in binaries:
            bin_path = os.path.join(bin_folder, bin)

            current_run += 1
            elapsed = time.time() - start_time
            remaining = max(
                0,
                estimated_total_seconds - int(elapsed)
            )

            name = os.path.basename(bin).replace(".out", "")
            result_file = f"{name}_Execution-{it}.res"
            out_path = os.path.join(experiment_solo_dir, result_file)

            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            print(
                (
                    f"[({current_run}/{total_planned_executions}) Estimated remainder: {hrs}h {mins}m {secs}s] "
                    f">> Executing ({bin} @ cpu{cpu0})"
                )
            )

            with open(out_path, "w") as output_file:
                pA = subprocess.Popen(
                    ["nice", "-n", str(NICE), "taskset", "-c", str(cpu0), bin_path, str(duration)],
                    stdout=output_file,
                )

                pA.wait()

    for it in range(num_iterations):
        for binA, binB in binary_pairs:
            binA_path = os.path.join(bin_folder, binA)
            binB_path = os.path.join(bin_folder, binB)

            current_run += 1
            elapsed = time.time() - start_time
            remaining = max(
                0,
                estimated_total_seconds - int(elapsed)
            )

            nameA = os.path.basename(binA).replace(".out", "")
            nameB = os.path.basename(binB).replace(".out", "")
            result_file = f"{nameA}_vs_{nameB}_Execution-{it}.res"
            out_path = os.path.join(experiment_comb_dir, result_file)

            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            print(
                (
                    f"[({current_run}/{total_planned_executions}) Estimated remainder: {hrs}h {mins}m {secs}s] "
                    f">> Executing ({binA} @ cpu{cpu0}) e ({binB} @ cpu{cpu1})"
                )
            )

            with open(out_path, "w") as output_file:
                pA = subprocess.Popen(
                    ["nice", "-n", str(NICE), "taskset", "-c", str(cpu0), binA_path, str(duration)],
                    stdout=output_file,
                )

                pB = subprocess.Popen(
                    ["nice", "-n", str(NICE), "taskset", "-c", str(cpu1), binB_path, str(duration)],
                    stdout=output_file,
                )

                pA.wait()
                pB.wait()
    print("\nExperiments completed!")


if __name__ == "__main__":
    execute()