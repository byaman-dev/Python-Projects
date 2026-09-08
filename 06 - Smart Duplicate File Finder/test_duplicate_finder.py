import importlib.util
import json
import os
import time
from pathlib import Path

import pytest

MODULE_PATH = Path('/tmp/duplicate_finder.py')
spec = importlib.util.spec_from_file_location('duplicate_finder', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rules(**overrides):
    base = {
        'hashing': {'algorithm': 'sha256', 'chunk_size': 1024},
        'recommendations': {'keep': 'newest'},
        'display': {'groups_per_page': 10},
        'cleanup': {'require_confirmation': True},
        'reporting': {'enabled': True, 'filename': 'duplicate-report.txt'},
    }
    base.update(overrides)
    return base


def write_file(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_scan_folder_recursive(tmp_path):
    write_file(tmp_path / 'a.txt', b'a')
    write_file(tmp_path / 'sub' / 'b.txt', b'b')
    files = mod.scan_folder(tmp_path)
    assert {p.relative_to(tmp_path).as_posix() for p in files} == {'a.txt', 'sub/b.txt'}


def test_group_files_by_size(tmp_path):
    a = write_file(tmp_path / 'a.bin', b'1234')
    b = write_file(tmp_path / 'b.bin', b'abcd')
    c = write_file(tmp_path / 'c.bin', b'12345')
    groups = mod.group_files_by_size([a, b, c])
    assert list(groups.keys()) == [4]
    assert set(groups[4]) == {a, b}


def test_calculate_hash_sha256(tmp_path):
    p = write_file(tmp_path / 'a.txt', b'hello world')
    assert mod.calculate_hash(p) == 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'


def test_calculate_hash_bad_algorithm(tmp_path):
    p = write_file(tmp_path / 'a.txt', b'hello')
    assert mod.calculate_hash(p, 'not-a-real-hash') is None


def test_group_files_by_hash_finds_exact_duplicates(tmp_path):
    a = write_file(tmp_path / 'a.txt', b'same')
    b = write_file(tmp_path / 'b.txt', b'same')
    c = write_file(tmp_path / 'c.txt', b'diff')
    sizes = mod.group_files_by_size([a, b, c])
    dup = mod.group_files_by_hash(sizes, rules())
    assert len(dup) == 1
    only_group = next(iter(dup.values()))
    assert set(only_group) == {a, b}


def test_group_files_by_hash_does_not_treat_same_size_as_duplicate(tmp_path):
    a = write_file(tmp_path / 'a.txt', b'abcd')
    b = write_file(tmp_path / 'b.txt', b'wxyz')
    sizes = mod.group_files_by_size([a, b])
    dup = mod.group_files_by_hash(sizes, rules())
    assert dup == {}


def make_analyzed_group(tmp_path, names=('old.txt', 'new.txt')):
    paths = []
    for name in names:
        paths.append(write_file(tmp_path / name, b'same-content'))
    now = time.time()
    mtimes = [now - 100, now]
    files = []
    for p, m in zip(paths, mtimes):
        os.utime(p, (m, m))
        files.append({'path': p, 'modified_time': m})
    return [{
        'group_number': 1,
        'hash': 'hash',
        'files': files,
        'copy_count': len(files),
        'file_size': paths[0].stat().st_size,
        'potential_space': paths[0].stat().st_size * (len(files) - 1),
    }]


def test_analyze_duplicate_groups_calculates_copy_count_and_space(tmp_path):
    a = write_file(tmp_path / 'a.txt', b'123456')
    b = write_file(tmp_path / 'b.txt', b'123456')
    c = write_file(tmp_path / 'c.txt', b'123456')
    sizes = mod.group_files_by_size([a, b, c])
    dups = mod.group_files_by_hash(sizes, rules())
    analyzed = mod.analyze_duplicate_groups(dups)
    assert len(analyzed) == 1
    assert analyzed[0]['copy_count'] == 3
    assert analyzed[0]['potential_space'] == 12


def test_recommend_newest(tmp_path):
    groups = make_analyzed_group(tmp_path)
    recs = mod.recommend_duplicates(groups, rules())
    assert recs[0]['keep']['path'].name == 'new.txt'
    assert [x['path'].name for x in recs[0]['remove_candidates']] == ['old.txt']


def test_recommend_oldest(tmp_path):
    groups = make_analyzed_group(tmp_path)
    recs = mod.recommend_duplicates(groups, rules(recommendations={'keep': 'oldest'}))
    assert recs[0]['keep']['path'].name == 'old.txt'


def test_recommend_shortest_path(tmp_path):
    short = write_file(tmp_path / 'a.txt', b'x')
    long = write_file(tmp_path / 'this-is-a-much-longer-name.txt', b'x')
    base = time.time()
    files = [
        {'path': long, 'modified_time': base},
        {'path': short, 'modified_time': base + 100},
    ]
    groups = [{
        'group_number': 1, 'files': files, 'copy_count': 2,
        'file_size': 1, 'potential_space': 1, 'hash': 'h'
    }]
    recs = mod.recommend_duplicates(groups, rules(recommendations={'keep': 'shortest_path'}))
    assert recs[0]['keep']['path'] == short


def test_recommendment_does_not_modify_files(tmp_path):
    groups = make_analyzed_group(tmp_path)
    before = {p: p.stat().st_mtime for p in [tmp_path/'old.txt', tmp_path/'new.txt']}
    mod.recommend_duplicates(groups, rules())
    after = {p: p.stat().st_mtime for p in before}
    assert before == after
    assert all(p.exists() for p in before)


def test_format_file_size():
    assert mod.format_file_size(0) == '0.00 B'
    assert mod.format_file_size(1024) == '1.00 KB'
    assert mod.format_file_size(1024**2) == '1.00 MB'
    assert mod.format_file_size(1024**3) == '1.00 GB'


def test_select_recommendation_group_valid_and_invalid(monkeypatch, tmp_path):
    groups = make_analyzed_group(tmp_path)
    recs = mod.recommend_duplicates(groups, rules())
    monkeypatch.setattr('builtins.input', lambda _: '1')
    assert mod.select_recommendation_group(recs) is recs[0]
    monkeypatch.setattr('builtins.input', lambda _: '99')
    assert mod.select_recommendation_group(recs) is None


def test_cleanup_permanent_requires_confirmation_and_deletes_only_selected(tmp_path, monkeypatch):
    keep = write_file(tmp_path / 'keep.txt', b'same')
    dup1 = write_file(tmp_path / 'dup1.txt', b'same')
    dup2 = write_file(tmp_path / 'dup2.txt', b'same')
    rec = {
        'keep': {'path': keep, 'modified_time': keep.stat().st_mtime},
        'remove_candidates': [
            {'path': dup1, 'modified_time': dup1.stat().st_mtime},
            {'path': dup2, 'modified_time': dup2.stat().st_mtime},
        ]
    }
    answers = iter(['1,2', '2', 'DELETE PERMANENTLY'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cleaned = mod.cleanup_duplicates(rec, {'cleanup': {'require_confirmation': True}})
    assert cleaned == [dup1, dup2]
    assert keep.exists()
    assert not dup1.exists()
    assert not dup2.exists()


def test_cleanup_wrong_confirmation_does_not_delete(tmp_path, monkeypatch):
    keep = write_file(tmp_path / 'keep.txt', b'same')
    dup = write_file(tmp_path / 'dup.txt', b'same')
    rec = {
        'keep': {'path': keep, 'modified_time': keep.stat().st_mtime},
        'remove_candidates': [{'path': dup, 'modified_time': dup.stat().st_mtime}],
    }
    answers = iter(['1', '2', 'WRONG'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cleaned = mod.cleanup_duplicates(rec, {'cleanup': {'require_confirmation': True}})
    assert cleaned == []
    assert keep.exists() and dup.exists()


def test_cleanup_invalid_selection_does_not_delete(tmp_path, monkeypatch):
    keep = write_file(tmp_path / 'keep.txt', b'same')
    dup = write_file(tmp_path / 'dup.txt', b'same')
    rec = {
        'keep': {'path': keep, 'modified_time': keep.stat().st_mtime},
        'remove_candidates': [{'path': dup, 'modified_time': dup.stat().st_mtime}],
    }
    monkeypatch.setattr('builtins.input', lambda _: '99')
    assert mod.cleanup_duplicates(rec, {'cleanup': {'require_confirmation': True}}) == []
    assert keep.exists() and dup.exists()


def test_generate_report(tmp_path, monkeypatch):
    report_dir = tmp_path / 'app'
    report_dir.mkdir()
    # generate_report uses __file__ location for output, so isolate a copied module.
    source = MODULE_PATH.read_text(encoding='utf-8')
    module_file = report_dir / 'duplicate_finder.py'
    module_file.write_text(source, encoding='utf-8')
    spec2 = importlib.util.spec_from_file_location('duplicate_finder_report', module_file)
    mod2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)

    a = write_file(tmp_path / 'a.txt', b'same')
    b = write_file(tmp_path / 'b.txt', b'same')
    sizes = mod2.group_files_by_size([a, b])
    dups = mod2.group_files_by_hash(sizes, rules())
    analyzed = mod2.analyze_duplicate_groups(dups)
    recs = mod2.recommend_duplicates(analyzed, rules())
    report = mod2.generate_report([a, b], sizes, analyzed, recs, tmp_path, rules(), [])
    assert report is not None and report.exists()
    text = report.read_text(encoding='utf-8')
    assert 'SMART DUPLICATE FILE FINDER REPORT' in text
    assert 'DUPLICATE GROUPS' in text
    assert 'RECOMMENDATIONS' in text
    assert 'CLEANUP RESULTS' in text


def test_rules_file_loads_valid_json(tmp_path, monkeypatch):
    config = tmp_path / 'rules.json'
    config.write_text(json.dumps({'recommendations': {'keep': 'newest'}}), encoding='utf-8')
    monkeypatch.setattr(mod, '__file__', str(tmp_path / 'duplicate_finder.py'))
    assert mod.load_rules()['recommendations']['keep'] == 'newest'


@pytest.mark.parametrize('bad_json', ['{', 'not json'])
def test_load_rules_invalid_json_returns_empty(tmp_path, monkeypatch, bad_json):
    (tmp_path / 'rules.json').write_text(bad_json, encoding='utf-8')
    monkeypatch.setattr(mod, '__file__', str(tmp_path / 'duplicate_finder.py'))
    assert mod.load_rules() == {}


def test_empty_file_duplicates(tmp_path):
    a = write_file(tmp_path / 'a.txt', b'')
    b = write_file(tmp_path / 'b.txt', b'')
    sizes = mod.group_files_by_size([a, b])
    dups = mod.group_files_by_hash(sizes, rules())
    assert len(dups) == 1


def test_three_identical_files_recovery(tmp_path):
    files = [write_file(tmp_path / f'{i}.txt', b'abc') for i in range(3)]
    sizes = mod.group_files_by_size(files)
    dups = mod.group_files_by_hash(sizes, rules())
    analyzed = mod.analyze_duplicate_groups(dups)
    assert analyzed[0]['copy_count'] == 3
    assert analyzed[0]['potential_space'] == 6


def test_no_duplicates_pipeline(tmp_path):
    files = [write_file(tmp_path / 'a.txt', b'a'), write_file(tmp_path / 'b.txt', b'bb')]
    sizes = mod.group_files_by_size(files)
    dups = mod.group_files_by_hash(sizes, rules())
    analyzed = mod.analyze_duplicate_groups(dups)
    recs = mod.recommend_duplicates(analyzed, rules())
    assert sizes == {}
    assert dups == {}
    assert analyzed == []
    assert recs == []


def test_default_recommendation_strategy_current_behavior(tmp_path):
    groups = make_analyzed_group(tmp_path)
    recs = mod.recommend_duplicates(groups, {})
    assert recs[0]['strategy'] == 'newest', 'Expected newest to be the default strategy'
