# compare lookup times for the five data structures

import argparse
import csv
import math
import random
import time
from collections.abc import Callable
from itertools import islice
from pathlib import Path

from binary_search import BinarySearch
from bloom_filter import BloomFilter
from cuckoo_filter import CuckooFilter
from hash_table import HashTable
from linear_search import LinearSearch

DEFAULT_DATA_PATH = Path("data.txt")
DEFAULT_OUTPUT_PATH = Path("benchmark-results.csv")
DEFAULT_DATASET_LIMIT = 100_000
DEFAULT_WARMUPS = 3
DEFAULT_RUNS = 10
DEFAULT_RANDOM_SEED = 520
QUERY_TAIL_RATIO = 0.10

CheckerFactory = Callable[[list[str]], object]


# load up to the row limit from a text or CSV file
def load_data(path: Path, column: str, limit: int) -> list[str]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    with path.open(newline="", encoding="utf-8") as data_file:
        values: list[str] = []
        reader = csv.reader(data_file)
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError(f"{path} does not contain any data rows")

        if len(first_row) == 1:
            rows = reader
            if first_row[0] != column:
                values.append(first_row[0])
            for row in islice(rows, limit - len(values)):
                if len(row) != 1 or row[0] == "":
                    raise ValueError(f"{path} must contain one string per row")
                values.append(row[0])
        else:
            try:
                column_index = first_row.index(column)
            except ValueError as error:
                raise ValueError(
                    f"{path} must contain a '{column}' column"
                ) from error
            for row in islice(reader, limit):
                if len(row) <= column_index or row[column_index] == "":
                    raise ValueError(f"{path} contains an empty '{column}' value")
                values.append(row[column_index])

    if not values:
        raise ValueError(f"{path} does not contain any data rows")
    return values


# get the constructors for each data structure
def checker_factories() -> dict[str, CheckerFactory]:
    return {
        "linear": LinearSearch,
        "binary": BinarySearch,
        "hash": HashTable,
        "bloom": BloomFilter,
        "cuckoo": lambda items: CuckooFilter(
            items,
            capacity=max(8, math.ceil(len(items) / 0.80)),
        ),
    }


# warm up the checker and average lookup time in microseconds
def measure_lookup(
    checker: object,
    query: str,
    warmups: int = DEFAULT_WARMUPS,
    runs: int = DEFAULT_RUNS,
) -> float:
    if warmups < 0:
        raise ValueError("warmups cannot be negative")
    if runs < 1:
        raise ValueError("runs must be at least 1")

    check = checker.check
    elapsed_ns = 0
    for _ in range(runs):
        for _ in range(warmups):
            check(query)
        start = time.perf_counter_ns()
        check(query)
        elapsed_ns += time.perf_counter_ns() - start
    return elapsed_ns / runs / 1_000


# compare lookup times for all structures using the same query
def benchmark(
    data: list[str],
    query: str,
    warmups: int = DEFAULT_WARMUPS,
    runs: int = DEFAULT_RUNS,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for datatype, factory in checker_factories().items():
        checker = factory(data)
        results.append(
            {
                "datatype": datatype,
                "dataset_size": len(data),
                "average_time_us": measure_lookup(
                    checker, query, warmups, runs
                ),
                "warmups": warmups,
                "runs": runs,
                "query": query,
            }
        )
    return results


# run the benchmark for each dataset size
def benchmark_sizes(
    data: list[str],
    sizes: tuple[int, ...],
    warmups: int = DEFAULT_WARMUPS,
    runs: int = DEFAULT_RUNS,
    datatype: str | None = None,
    seed: int = DEFAULT_RANDOM_SEED,
) -> list[dict[str, object]]:
    if not sizes:
        raise ValueError("sizes cannot be empty")
    if any(size < 1 for size in sizes):
        raise ValueError("sizes must contain only positive integers")
    if any(size > len(data) for size in sizes):
        raise ValueError(
            "every size must be at most the loaded dataset size"
        )
    factories = checker_factories()
    if datatype is not None:
        if datatype not in factories:
            raise ValueError(f"unsupported datatype: {datatype}")
        factories = {datatype: factories[datatype]}

    results: list[dict[str, object]] = []
    random_generator = random.Random(seed)
    for size in sizes:
        sample = data[:size]
        # pick from all loaded rows so the query can be outside the sample
        query_pool = data
        results.extend(
            benchmark_with_factories(
                sample,
                factories,
                random_generator.choice(query_pool),
                warmups,
                runs,
            )
        )
    return results


# measure build and lookup times for the selected structures
def benchmark_with_factories(
    data: list[str],
    factories: dict[str, CheckerFactory],
    query: str,
    warmups: int,
    runs: int,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for datatype, factory in factories.items():
        construction_start = time.perf_counter()
        checker = factory(data)
        construction_seconds = time.perf_counter() - construction_start
        print(
            f"Built {datatype} for {len(data):,} rows "
            f"in {construction_seconds:.2f} seconds",
            flush=True,
        )
        results.append(
            {
                "datatype": datatype,
                "dataset_size": len(data),
                "construction_seconds": construction_seconds,
                "average_time_us": measure_lookup(
                    checker, query, warmups, runs
                ),
                "warmups": warmups,
                "runs": runs,
                "query": query,
            }
        )
    return results


# use powers of ten from 100, and always include the maximum size
def gradient_sizes(max_size: int) -> tuple[int, ...]:
    if max_size < 1:
        raise ValueError("max_size must be at least 1")

    sizes = [
        10**power
        for power in range(2, math.floor(math.log10(max_size)) + 1)
    ]
    sizes = [size for size in sizes if size < max_size]
    if not sizes or sizes[-1] != max_size:
        sizes.append(max_size)
    return tuple(sizes)


# calculate how many extra rows to load for queries
def query_tail_size(existing_size: int) -> int:
    if existing_size < 1:
        raise ValueError("existing_size must be at least 1")
    return max(1, math.ceil(existing_size * QUERY_TAIL_RATIO))


# save the benchmark results to a CSV file
def write_results(path: Path, results: list[dict[str, object]]) -> None:
    if not results:
        raise ValueError("results cannot be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)


# read the options, run the benchmark, and save the results
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark login-checker lookup time using a bounded CSV data load."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--column", default="value")
    parser.add_argument("--limit", type=int, default=DEFAULT_DATASET_LIMIT)
    parser.add_argument(
        "--datatype",
        choices=tuple(checker_factories()),
        help="benchmark only one datatype; omit to benchmark all datatypes",
    )
    parser.add_argument(
        "--sizes",
        help="comma-separated dataset sizes, for example 100,1000,10000",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUPS)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()

    sizes = (
        tuple(int(size) for size in args.sizes.split(","))
        if args.sizes
        else gradient_sizes(args.limit)
    )
    load_start = time.perf_counter()
    data = load_data(
        args.data,
        args.column,
        max(sizes) + query_tail_size(max(sizes)),
    )
    load_seconds = time.perf_counter() - load_start

    print(
        f"Loaded {len(data):,} rows from {args.data} "
        f"in {load_seconds:.2f} seconds",
        flush=True,
    )
    results = benchmark_sizes(
        data,
        sizes,
        args.warmups,
        args.runs,
        args.datatype,
        args.seed,
    )
    write_results(args.output, results)
    print(f"Saved benchmark results to {args.output}")


if __name__ == "__main__":
    main()
