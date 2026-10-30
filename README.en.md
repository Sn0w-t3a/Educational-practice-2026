# Educational-practice-2026

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](https://docs.pytest.org/)

Educational practice **PM.06 "Information Systems Maintenance"**  
KGB POU KhPET, group **ISP-31s**, period **19.10.2026 — 31.10.2026**

---

## Overview

A console-based Python information system for computing the **sums of the main and anti-diagonal elements** of a square matrix generated from user-supplied parameters. Supports input and output both via console and via file.

The project is accompanied by a complete set of technical documentation, a logging module, a template backup/restore module, and a test suite confirming compliance of key modules with the technical specification.

---

## Features

- **Matrix input:**
  - from keyboard, one number per line;
  - from keyboard, one row = `n` space- or comma-separated numbers;
  - from a text file, with optional first line containing order `n`.
- **Computation:**
  - main diagonal sum `Σ m[i][i]`;
  - anti-diagonal sum `Σ m[i][n−1−i]`.
- **Output:**
  - to console with column alignment;
  - to a text file.
- **Logging:**
  - console at `INFO`+ (concise);
  - `logs/app.log` at `DEBUG`+ (full history with matrix dumps).
- **Template backup/restore:**
  - timestamped ZIP archives;
  - SHA-256 integrity control;
  - `backups/manifest.json` journal;
  - rotation (10 copies retained);
  - atomic replacement and a safety copy before restore.
- **Diagnostics:**
  - `cProfile` for function timing;
  - `tracemalloc` for memory snapshots;
  - `py-spy` for Flame Graphs without modifying code.

---

## Project structure

```
Educational-practice-2026/
├── main.py                  # entry point, menu
├── functions.py             # computation, I/O, validation
├── logger_module.py         # logging to console and file
├── template_backup.py       # template backup/restore
├── diagnostics.py           # cProfile / tracemalloc / py-spy
├── test_functions.py        # pytest tests
├── requirements.txt
├── .gitignore
├── README.md                # Russian version
├── README.en.md             # this file (English version)
├── docs/
│   ├── ТЗ.md                # technical specification (RU)
│   ├── регламент_ТО.md      # maintenance regulation (RU)
│   └── testing.md           # test protocol (RU)
├── templates/               # user templates (not committed)
├── backups/                 # backup archives (not committed)
└── logs/                    # logs (not committed)
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sn0w-t3a/Educational-practice-2026.git
cd Educational-practice-2026
```

### 2. Virtual environment (recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
pytest>=8.0
pytest-cov>=5.0
py-spy>=0.3
```

> Optional for extended diagnostics: `pip install yappi line_profiler memory_profiler scalene`.

---

## Usage

### Main program

```bash
python main.py
```

### Run tests

```bash
pytest test_functions.py -v
```

With coverage:

```bash
pytest test_functions.py --cov=functions --cov-report=term-missing
```

### Backup and restore

```bash
python -m template_backup --backup
python -m template_backup --list
python -m template_backup --restore
python -m template_backup --restore --archive backups/templates_2026-10-28_10-15-00.zip
python -m template_backup --restore --force
python -m template_backup --restore --skip-invalid
```

### Diagnostics

```bash
python diagnostics.py --cprofile --memory
python diagnostics.py --pyspy --script main.py
```

---

## Example output

```
Your matrix:
1  2  3
4  5  6
7  8  9

Main diagonal sum (i == j):        15
Anti-diagonal sum (i + j == 2):    15
```

---

## Testing

30 test cases cover six functions in `functions.py`, including positive, negative, and edge cases (n = 1, negative values, floats).

```
$ pytest test_functions.py -v
======================== 30 passed in 0.42s ========================
```

Full test protocol — in [`docs/testing.md`](docs/testing.md).

---

## Documentation

| Document | Purpose |
|---|---|
| [`docs/ТЗ.md`](docs/ТЗ.md) | Technical specification (RU) |
| [`docs/регламент_ТО.md`](docs/регламент_ТО.md) | Maintenance regulation (RU) |
| [`docs/testing.md`](docs/testing.md) | Test protocol (RU) |
| [`README.md`](README.md) | Russian version of this README |

---

## License

Educational project (KGB POU KhPET, group ISP-31s). Distributed under the MIT License.

---

## Author

**Sn0w-t3a** — student of group ISP-31s, KGB POU KhPET
