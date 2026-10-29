"""Validate the reporting packet against existing evidence; never trains."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    register = json.loads((HERE/'evidence.json').read_text())
    for name, digest in register['sources'].items():
        assert sha(ROOT/name) == digest, name
    for name, item in register['figures'].items():
        assert sha(HERE/'figures'/name) == item['sha256']
        assert sha(ROOT/item['source']) == item['sha256']
    links = 0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#')):
                continue
            assert (path.parent/target.split('#')[0]).exists(), (path.name, target)
            links += 1
    report = (HERE/'REPORT.md').read_text(encoding='utf-8')
    assert format(register['baseline']['final_value_mae_m'], '.5f').lstrip('0') in report
    for row in register['final_3d'] + register['development_5']:
        assert format(row['mae'], '.8f').lstrip('0') in report, row['model']
    rows = register['development_5_contacts_vs_reference']
    for name in ['4C', '5U', '5R']:
        row = next(r for r in rows if r['evader'] == name)
        assert row['definite_collision_count'] == 8 and row['joint_queries'] == 628
    assert next(r for r in rows if r['evader'] == 'reference')['definite_collision_count'] == 4
    boot = register['development_5_bootstrap'][0]
    lo, hi = boot['relative_improvement_percent_95_interval']
    assert boot['old'] == '5U' and boot['new'] == '5R' and lo < 0 < hi
    manifest = HERE/'report_manifest.json'
    if manifest.exists():
        for name, digest in json.loads(manifest.read_text())['files'].items():
            assert sha(HERE/name) == digest, name
    result = dict(status='passed',evidence_sources=len(register['sources']),
                  copied_figures=len(register['figures']),local_markdown_links=links,
                  headline_metrics_and_contact_counts=True,training=False)
    print(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    verify()
