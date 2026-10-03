import csv
from unittest.mock import Mock, call

import pytest

import benchmark


@pytest.mark.parametrize(
    "contents",
    ["alice\nbob\ncharlie\n", "id,value\n1,alice\n2,bob\n3,charlie\n"],
)
def test_load_data_respects_limit(tmp_path, contents):
    path = tmp_path / "data.csv"
    path.write_text(contents, encoding="utf-8")

    assert benchmark.load_data(path, "value", limit=2) == ["alice", "bob"]


@pytest.mark.parametrize(
    ("max_size", "expected"),
    [(50, (50,)), (100, (100,)), (1_000, (100, 1_000)), (2_500, (100, 1_000, 2_500))],
)
def test_gradient_sizes_includes_maximum(max_size, expected):
    assert benchmark.gradient_sizes(max_size) == expected


def test_measure_lookup_averages_microseconds(monkeypatch):
    checker = Mock()
    clock = Mock(side_effect=[1_000, 2_000, 3_000, 6_000])
    monkeypatch.setattr(benchmark.time, "perf_counter_ns", clock)

    average = benchmark.measure_lookup(checker, "alice", warmups=2, runs=2)

    assert average == 2.0
    assert checker.check.call_args_list == [call("alice")] * 6


@pytest.mark.parametrize(("warmups", "runs"), [(-1, 1), (0, 0)])
def test_measure_lookup_rejects_invalid_counts(warmups, runs):
    with pytest.raises(ValueError):
        benchmark.measure_lookup(Mock(), "alice", warmups=warmups, runs=runs)


def test_benchmark_sizes_runs_all_structures():
    data = ["alice", "bob", "charlie"]

    results = benchmark.benchmark_sizes(data, (1, 3), warmups=0, runs=1)

    assert len(results) == 10
    assert {(row["datatype"], row["dataset_size"]) for row in results} == {
        (datatype, size)
        for datatype in ("linear", "binary", "hash", "bloom", "cuckoo")
        for size in (1, 3)
    }
    for row in results:
        assert row["query"] in data
        assert row["warmups"] == 0
        assert row["runs"] == 1
        assert row["average_time_us"] >= 0
        assert row["construction_seconds"] >= 0
    for size in (1, 3):
        assert (
            len({row["query"] for row in results if row["dataset_size"] == size}) == 1
        )


def test_benchmark_sizes_selects_one_datatype():
    results = benchmark.benchmark_sizes(
        ["alice", "bob"], (2,), warmups=0, runs=1, datatype="hash"
    )

    assert len(results) == 1
    assert results[0]["datatype"] == "hash"
    assert results[0]["dataset_size"] == 2


@pytest.mark.parametrize("sizes", [(), (0,), (-1,), (4,)])
def test_benchmark_sizes_rejects_invalid_sizes(sizes):
    with pytest.raises(ValueError):
        benchmark.benchmark_sizes(["alice", "bob", "charlie"], sizes)


def test_write_results_creates_csv(tmp_path):
    path = tmp_path / "output" / "results.csv"
    results = [
        {
            "datatype": "hash",
            "dataset_size": 2,
            "average_time_us": 1.5,
            "query": "alice,smith",
        },
        {
            "datatype": "linear",
            "dataset_size": 2,
            "average_time_us": 2.5,
            "query": "bob",
        },
    ]

    benchmark.write_results(path, results)

    with path.open(newline="", encoding="utf-8") as output_file:
        reader = csv.DictReader(output_file)
        assert reader.fieldnames == list(results[0])
        assert list(reader) == [
            {key: str(value) for key, value in row.items()} for row in results
        ]
