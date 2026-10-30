# Диагностика программы: cProfile (время), tracemalloc (память), py-spy (CPU).
#
# py-spy — внешний CLI-инструмент, работает без изменения кода.
# Установка: pip install py-spy

from __future__ import annotations

import cProfile
import io
import pstats
import shutil
import subprocess
import sys
import tracemalloc
from pathlib import Path
from typing import Any, Callable


# ----------------------------------------------------
# 1. cProfile — профиль функций

def profile_cprofile(func: Callable, *args: Any,
                     sort_by: str = "cumulative",
                     top: int = 15) -> pstats.Stats:
    # Профилирует func(*args). sort_by: 'cumulative'|'tottime'|'ncalls'.
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        func(*args)
    finally:
        profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs()
    stats.sort_stats(sort_by).print_stats(top)
    print(f"[cProfile] {getattr(func, '__name__', func)} "
          f"(sort={sort_by}, top={top}):")
    print(stream.getvalue())
    return stats



# ----------------------------------------------------
# 2. tracemalloc — снимки памяти до/после

def diagnose_memory(func: Callable, *args: Any,
                    top: int = 10) -> list[tracemalloc.StatisticDiff]:
    # Сравнивает снимки памяти до и после func(*args).
    #
    # Большой diff → функция создаёт много объектов (возможные утечки/копии).

    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    try:
        func(*args)
    finally:
        after = tracemalloc.take_snapshot()
        tracemalloc.stop()

    diff = after.compare_to(before, "lineno")
    print(f"[tracemalloc] {getattr(func, '__name__', func)} — топ-{top}:")
    for stat in diff[:top]:
        print("  ", stat)
    return diff


#----------------------------------------------------
# 3. py-spy — внешний сэмплирующий профайлер

def run_pyspy(script_path: str, output: str = "profile.svg",
              top: bool = False) -> subprocess.CompletedProcess | None:
    # Запускает `py-spy record` (Flame Graph) или `py-spy top` для скрипта.
    script = Path(script_path)
    if not script.is_file():
        print(f"[py-spy] файл не найден: {script}")
        return None

    if not shutil.which("py-spy"):
        print("[py-spy] не установлен. Установите: pip install py-spy")
        return None

    if top:
        cmd = ["py-spy", "top", "--", sys.executable, str(script)]
    else:
        cmd = ["py-spy", "record", "-o", output, "--",
               sys.executable, str(script)]
    print(f"[py-spy] {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if not top:
        print(f"[py-spy] профиль сохранён: {output}")
    return result


# ----------------------------------------------------
# CLI

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Диагностика программы")
    parser.add_argument("--script", default="main.py",
                        help="скрипт для py-spy")
    parser.add_argument("--cprofile", action="store_true")
    parser.add_argument("--memory", action="store_true")
    parser.add_argument("--pyspy", action="store_true")
    args = parser.parse_args()

    demo = [[float(i + j) for j in range(100)] for i in range(100)]

    if args.cprofile:
        import functions as fns
        profile_cprofile(fns.main_diagonal_sum, demo)
        profile_cprofile(fns.anti_diagonal_sum, demo)

    if args.memory:
        import functions as fns
        diagnose_memory(fns.main_diagonal_sum, demo)
        diagnose_memory(fns.anti_diagonal_sum, demo)

    if args.pyspy:
        run_pyspy(args.script)