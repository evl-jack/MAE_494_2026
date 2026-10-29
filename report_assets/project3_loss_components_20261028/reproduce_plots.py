import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE
OUT = BASE
OUT.mkdir(parents=True, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(Path(tempfile.gettempdir()) / 'project3_loss_plots_matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10, 'legend.fontsize': 8, 'savefig.dpi': 160})
records = []

def val(row, key):
    try:
        return float(row[key])
    except (KeyError, ValueError, TypeError):
        return np.nan

def load(label, path):
    source = SOURCE / 'histories' / (re.sub(r'[^A-Za-z0-9_-]+', '_', label).strip('_') + '.csv')
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    assert rows, path
    dest = OUT / 'histories' / (re.sub(r'[^A-Za-z0-9_-]+', '_', label).strip('_') + '.csv')
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(raw)
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == digest
    records.append({'run': label, 'source': path, 'copy': dest.relative_to(OUT).as_posix(), 'sha256': digest, 'rows': len(rows), 'first_row': rows[0], 'last_row': rows[-1]})
    return rows

def line(ax, x, y, label, color, style='-'):
    y = np.array(y, dtype=float)
    x = np.array(x, dtype=float)
    y[~np.isfinite(y) | (y <= 0)] = np.nan
    if np.isfinite(y).any():
        ax.plot(x, y, label=label, color=color, linestyle=style, linewidth=1.25)

def panel(ax, label, path, marker=None):
    rows = load(label, path)
    refinement = 'pre_physics_loss' in rows[0]
    sampling = 'additional_step' in rows[0]
    xkey = 'additional_step' if sampling else 'step'
    x = [val(r, xkey) for r in rows]
    if refinement:
        line(ax, x, [val(r, 'pre_physics_loss') for r in rows], 'Physics before update', '#d46a12')
        line(ax, x, [val(r, 'chosen_physics_loss') for r in rows], 'Physics after selected step', '#8c4fa8', '--')
        zero = 'Terminal value loss = 0 by construction'
        xlabel = 'Additional updates from 3A'
    elif sampling:
        line(ax, x, [val(r, 'sampled_vi_mae') for r in rows], 'Sampled physics loss', '#d46a12')
        terminal = [val(r, 'terminal_max_abs') for r in rows]
        assert all(np.isfinite(t) and t == 0 for t in terminal)
        zero = 'Logged terminal maximum error = 0'
        xlabel = 'Additional updates from 4C'
    else:
        terminal = [val(r, 'terminal_mae') for r in rows]
        physics = [val(r, 'pde_mae' if 'pde_mae' in r else 'vi_mae') for r in rows]
        weighted = [val(r, 'terminal_mae') * val(r, 'terminal_weight') for r in rows]
        total = [val(r, 'loss') for r in rows]
        line(ax, x, terminal, 'Terminal MAE (unweighted)', '#2365a1')
        line(ax, x, physics, 'Physics VI MAE', '#d46a12')
        line(ax, x, weighted, 'Weighted terminal contribution', '#22845a', '--')
        if not np.allclose(total, physics, equal_nan=True):
            line(ax, x, total, 'Total training objective', '#666666', ':')
        zero = 'Terminal value loss = 0; total = physics' if all(t == 0 for t in terminal) else None
        xlabel = 'Cumulative optimizer updates'
        phases = [r.get('phase', '') for r in rows]
        if any(p in ('terminal', 'pretrain') for p in phases):
            starts = [xx for xx, p in zip(x, phases) if p not in ('terminal', 'pretrain')]
            if starts:
                ax.axvline(min(starts), color='#aaaaaa', linestyle='--', linewidth=1)
                ax.text(min(starts), .97, ' Physics begins', transform=ax.get_xaxis_transform(), va='top', fontsize=8)
    if marker is not None:
        ax.axvline(marker, color='#aaaaaa', linestyle='--', linewidth=1)
    ax.set_yscale('log')
    lo, hi = ax.get_ylim()
    if zero:
        ax.set_ylim(lo * .55, hi * 1.15)
    ax.set_title(label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Logged loss value (log scale)')
    ax.grid(True, which='major', alpha=.2)
    ax.ticklabel_format(axis='x', style='plain', useOffset=False)
    if zero:
        ax.text(.02, .04, zero, transform=ax.transAxes, fontsize=8, va='bottom', bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='upper right')

def figure(filename, title, runs, ncols=2):
    nrows = (len(runs) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(7*ncols, 3.5*nrows), squeeze=False, constrained_layout=True)
    for ax, run in zip(axes.flat, runs):
        panel(ax, *run)
    for ax in list(axes.flat)[len(runs):]:
        ax.set_visible(False)
    fig.suptitle(title, fontsize=15)
    fig.savefig(OUT / filename)
    plt.close(fig)

figure('experiments_1_2_losses.png', 'Experiments 1–2: separate loss components from saved training logs', [
    ('Experiment 1', 'runs/air3d_cpu_20261022/history.csv'),
    ('2A: lower terminal weight', 'runs/experiment_2_a_loss_20261022/history.csv'),
    ('2B: focused sampling', 'runs/experiment_2_b_sampling_20261022/history.csv'),
    ('2C: longer full-horizon training', 'runs/experiment_2_c_hold_20261022/history.csv', 12000),
])
figure('experiment_3_losses.png', 'Experiment 3: constrained outputs and refinements — no positive terminal loss', [
    ('3A: exact terminal and obstacle', 'runs/experiment_3_a_constraints/history.csv'),
    ('3B: periodic heading', 'runs/experiment_3_b_periodic/history.csv'),
    ('3C: mixed time sampling', 'runs/experiment_3_c_time_sampling/history.csv'),
    ('3D: Adam continuation (+200 endpoint marked)', 'experiments/experiment_3_d_refinement/adam/history.csv', 200),
    ('3D: plain gradient with step selection', 'experiments/experiment_3_d_refinement/plain_gradient/history.csv'),
    ('3D: scaled gradient with step selection', 'experiments/experiment_3_d_refinement/second_moment_scaled/history.csv'),
    ('3E: width 64, longer training', 'runs/experiment_3_e_long64/history.csv', 10000),
    ('3E: width 96', 'runs/experiment_3_e_wide96/history.csv'),
])
figure('experiment_4_losses.png', 'Experiment 4: joint-coordinate terminal and physics losses', [
    ('4A: soft terminal penalty', 'experiments_6d/runs/4A/history.csv'),
    ('4B: exact terminal and obstacle', 'experiments_6d/runs/4B/history.csv'),
    ('4C: continuation of 4B (parent ends at 10000)', 'experiments_6d/runs/4C/history.csv', 10000),
], ncols=3)
figure('experiment_5_losses.png', 'Experiment 5: training losses use different sampling distributions', [
    ('5U: uniform sampling', 'experiments_6d/experiment_5_sampling/runs/5U/history.csv'),
    ('5R: residual-guided sampling', 'experiments_6d/experiment_5_sampling/runs/5R/history.csv'),
])

manifest = {'status':'Charts generated only from existing CSV logs; no training/model/reference evaluation',
            'zero_handling':'Nonpositive values are omitted from log lines; exact terminal zeros are explicitly annotated, never replaced by epsilon.',
            'plotting':'All logged rows plotted without smoothing. Missing components not invented. 3D pre/update-selected values are distinct; Experiment 5 terminal maximum error is not relabeled MAE.',
            'sources':records}
for r in records:
    assert hashlib.sha256((OUT / r['copy']).read_bytes()).hexdigest() == r['sha256']
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'runs':len(records), 'figures':4, 'source_hashes_unchanged':True}))
