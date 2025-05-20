#!/usr/bin/env python3
"""
parse_and_plot_gem5_stats.py

Usage (either style):

  # 1) Directly on the command line:
  ./parse_and_plot_gem5_stats.py \
    --runs width4 width8 width12 \
    --stats sim_seconds sim_insts ipc numCycles \
    [--base-dir m5out] [--save-plots]

  # 2) From text files:
  ./parse_and_plot_gem5_stats.py \
    --runs-file runs.txt \
    --stats-file stats.txt \
    [--base-dir m5out] [--save-plots]

  'runs.txt' and 'stats.txt' should have one name per line. Lines beginning
  with '#' or blank lines are ignored.

Defaults:
  --base-dir m5out
  plots show on screen (omit --save-plots)
"""

import os
import re
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# regex to match "name   value" (int, float, sci-notation, or nan), ignore trailing comments
STAT_LINE_RE = re.compile(
    r'^(?P<name>\S+)\s+'
    r'(?P<value>[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|nan)'
    r'(?:\s+#.*)?$'
)

def parse_stats_file(path, wanted_stats):
    results = {}
    seen = False
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('----') and 'Begin Simulation Statistics' in line:
                if not seen:
                    seen = True
                    continue
                else:
                    break
            if not seen or line.startswith('#'):
                continue
            m = STAT_LINE_RE.match(line)
            if not m:
                continue
            name = m.group('name')
            valstr = m.group('value')
            try:
                val = float(valstr)
            except ValueError:
                val = float('nan')
            if name in wanted_stats:
                results[name] = val
    return results

def load_list_from_file(path):
    items = []
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            items.append(line)
    return items

def main():
    p = argparse.ArgumentParser(
        description="Extract & plot gem5 stats from multiple runs"
    )
    p.add_argument('--base-dir', default='m5out',
                   help="Directory containing subfolders for each run (default: m5out)")
    # runs: either via --runs or --runs-file
    runs_group = p.add_mutually_exclusive_group(required=True)
    runs_group.add_argument('--runs', nargs='+',
                            help="Run names (subfolder names under base-dir)")
    runs_group.add_argument('--runs-file', metavar='FILE',
                            help="Text file with one run name per line")
    # stats: either via --stats or --stats-file
    stats_group = p.add_mutually_exclusive_group(required=True)
    stats_group.add_argument('--stats', nargs='+',
                             help="Stat names to extract (exactly as in stats.txt)")
    stats_group.add_argument('--stats-file', metavar='FILE',
                             help="Text file with one stat name per line")
    p.add_argument('--save-plots', action='store_true',
                   help="Save plots as PNGs instead of displaying them")
    args = p.parse_args()

    # load run names
    if args.runs_file:
        runs = load_list_from_file(args.runs_file)
    else:
        runs = args.runs

    # load stat names
    if args.stats_file:
        stats = load_list_from_file(args.stats_file)
    else:
        stats = args.stats

    # collect data
    rows = []
    idx  = []
    for run in runs:
        stats_path = os.path.join(args.base_dir, run, 'stats.txt')
        if not os.path.isfile(stats_path):
            print(f"[warning] {stats_path} not found, skipping.")
            continue
        data = parse_stats_file(stats_path, stats)
        if not data:
            print(f"[warning] no requested stats in {stats_path}, skipping.")
            continue
        rows.append(data)
        idx.append(run)

    if not rows:
        print("No data collected; exiting.")
        return

    # build DataFrame
    df = pd.DataFrame(rows, index=idx)
    df.index.name = 'Run'
    print("\nCollected statistics:\n")
    print(df)

    # plot each stat
    for stat in stats:
        if stat not in df.columns:
            print(f"[note] stat '{stat}' missing—skipping plot.")
            continue
        plt.figure()
        df[stat].plot(marker='o')
        plt.title(f"{stat} vs. Run")
        plt.xlabel("Run")
        plt.ylabel(stat)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if args.save_plots:
            outdir = "plots"
            os.makedirs(outdir, exist_ok=True)
            plt.savefig(os.path.join(outdir, f"{stat}.png"))
        else:
            plt.show()

if __name__ == '__main__':
    main()
