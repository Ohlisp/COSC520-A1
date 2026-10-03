# COSC 520 Assignment 1

This project compares five ways to check whether a login name exists: linear
search, binary search, a hash table, a Bloom filter, and a cuckoo filter.

Each implementation supports insertion and lookup. All except the Bloom filter
also support deletion. Bloom and cuckoo filters can return false positives.

## Project layout

```text
demo.py          Example operations for all five implementations
src/             Implementations and the shared LoginChecker interface
  benchmark.py   Measure construction and lookup times
tests/           Unit tests for each implementation
flake.nix        Nix development environment and test runner
```

## Setup

Run these commands from the project root. Choose either setup below.

### Nix

With Nix and flakes enabled:

```sh
nix develop
```

This provides Python, dependencies, and the import path. You can also run the
tests directly with `nix run .#test`.

### Python virtual environment

Use Python 3.14. In a macOS or Linux shell:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pytest mmh3 bitarray
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
```

## Dataset

Download the 8 GB [dataset from Dropbox](https://www.dropbox.com/scl/fi/6vi0r3ohnt3ik9ca0o10b/data-1b.txt?rlkey=dl24g3ele5ircnczvzz58p24y&dl=0)
and save it as `data.txt` in the project root.

## Tests and demo

After either setup:

```sh
python -m pytest tests
python demo.py
```

## Benchmark

Benchmark all five implementations using `data.txt`:

```sh
python src/benchmark.py --limit 100000
```

This compares sizes of 100, 1,000, 10,000, and 100,000. Results are saved to
`benchmark-results.csv`, with lookup times in microseconds.

Run `python src/benchmark.py --help` for more options.
