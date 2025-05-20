#!/usr/bin/env python3
"""
parse_and_plot_gem5_stats.py

Usage (either style):

  # 1) Directly on the command line:
  ./parse_and_plot_gem5_stats.py \
    --runs width4 width8 width12 \
    --stats sim_seconds sim_insts ipc numCycles \
    [--base-dir m5out] [--save-plots --plots-dir my_plots] [--output-csv collected.csv]

  # 2) From text files:
  ./parse_and_plot_gem5_stats.py \
    --runs-file runs.txt \
    --stats-file stats.txt \
    [--base-dir m5out] [--save-plots --plots-dir my_plots] [--output-csv collected.csv]

Options:
  --base-dir     Directory containing subfolders for each run (default: m5out)
  --runs / --runs-file  
                 Either list run names on the CLI or load them from a text file
  --stats / --stats-file
                 Either list stat names on the CLI or load them from a text file
  --save-plots   If set, saves plots instead of displaying them
  --plots-dir    Directory under which to save PNGs (default: plots)
  --output-csv   Path to write the collected statistics CSV (default: collected_stats.csv)
"""

import os
import re
import argparse
import pandas as pd
import matplotlib.pyplot as plt

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
    runs_group = p.add_mutually_exclusive_group(required=True)
    runs_group.add_argument('--runs', nargs='+',
                            help="Run names (subfolder names under base-dir)")
    runs_group.add_argument('--runs-file', metavar='FILE',
                            help="Text file with one run name per line")
    stats_group = p.add_mutually_exclusive_group(required=True)
    stats_group.add_argument('--stats', nargs='+',
                             help="Stat names to extract (exactly as in stats.txt)")
    stats_group.add_argument('--stats-file', metavar='FILE',
                             help="Text file with one stat name per line")
    p.add_argument('--save-plots', action='store_true',
                   help="Save plots as PNGs instead of displaying them")
    p.add_argument('--plots-dir', default='plots',
                   help="Directory under which to save PNGs (default: plots)")
    p.add_argument('--output-csv', default='collected_stats.csv',
                   help="Write collected statistics to this CSV file (default: collected_stats.csv)")
    args = p.parse_args()

    runs  = load_list_from_file(args.runs_file) if args.runs_file else args.runs
    stats = load_list_from_file(args.stats_file) if args.stats_file else args.stats

    rows, idx = [], []
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

    df = pd.DataFrame(rows, index=idx)
    df.index.name = 'Run'
    print("\nCollected statistics:\n")
    print(df)

    # Write CSV for Excel
    df.to_csv(args.output_csv)
    print(f"✓ Saved collected stats to '{args.output_csv}'")

    # Plot each stat
    if args.save_plots:
        os.makedirs(args.plots_dir, exist_ok=True)
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
            outname = os.path.join(args.plots_dir, f"{stat}.png")
            plt.savefig(outname)
            print(f"→ Saved {stat} plot to '{outname}'")
        else:
            plt.show()

if __name__ == '__main__':
    main()
