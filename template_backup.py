"""Резервное копирование и восстановление шаблонов генерации матриц.

Шаблон — JSON-файл в templates/ с параметрами генерации матрицы.
Копии — ZIP-архивы в backups/, журнал — backups/manifest.json.

CLI:
    python -m template_backup --backup
    python -m template_backup --restore [--archive path] [--force] [--skip-invalid]
    python -m template_backup --list
"""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from logger_module import setup_logger

log = setup_logger()

TEMPLATES_DIR = Path("templates")
BACKUPS_DIR = Path("backups")
MANIFEST_PATH = BACKUPS_DIR / "manifest.json"
MAX_COPIES = 10
REQUIRED_FIELDS = ("version", "name", "n", "kind", "lo", "hi", "seed")


# -----------------------------------------------------
# Вспомогательные функции

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _template_hash(data: dict) -> str:
    """SHA-256 от содержимого шаблона без поля 'hash'."""
    payload = {k: v for k, v in data.items() if k != "hash"}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _validate_template(data: dict) -> tuple[bool, str]:
    """Проверяет поля и контрольную сумму. Возвращает (ok, причина)."""
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False, f"нет поля '{field}'"
    if data.get("kind") not in ("int", "float"):
        return False, f"недопустимый kind={data.get('kind')}"
    if not isinstance(data.get("n"), int) or data["n"] <= 0:
        return False, f"n={data.get('n')} должно быть > 0"
    expected = _template_hash(data)
    if data.get("hash") != expected:
        return False, "hash не совпадает"
    return True, ""


def _load_manifest() -> list[dict]:
    if not MANIFEST_PATH.is_file():
        return []
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log.error("manifest.json повреждён, начинаю новый: %s", e)
        return []


def _save_manifest(entries: list[dict]) -> None:
    entries = entries[-100:]                      # не более 100 записей
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# -----------------------------------------------------
# 1. Резервное копирование

def backup_templates(templates_dir: Path = TEMPLATES_DIR,
                     backups_dir: Path = BACKUPS_DIR,
                     prefix: str = "templates",
                     max_copies: int = MAX_COPIES) -> Path | None:
    """Создаёт ZIP-архив всех шаблонов. Возвращает путь к архиву или None."""
    log.info("Бэкап: старт, source=%s", templates_dir)
    if not templates_dir.is_dir():
        log.error("Бэкап: каталог %s не существует", templates_dir)
        return None

    files = sorted(templates_dir.glob("*.json"))
    if not files:
        log.warning("Бэкап: в %s нет шаблонов, копия не создаётся", templates_dir)
        return None

    # Шаг 2: валидация (не блокирует создание копии)
    invalid: list[str] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ok, reason = _validate_template(data)
            if not ok:
                invalid.append(f.name)
                log.error("Бэкап: шаблон '%s' невалиден: %s", f.name, reason)
        except (json.JSONDecodeError, OSError) as e:
            invalid.append(f.name)
            log.error("Бэкап: не удалось прочитать '%s': %s", f.name, e)

    # Шаг 3: имя архива
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backups_dir.mkdir(parents=True, exist_ok=True)
    archive = backups_dir / f"{prefix}_{stamp}.zip"
    counter = 1
    while archive.exists():
        archive = backups_dir / f"{prefix}_{stamp}_{counter}.zip"
        counter += 1

    # Шаг 4: упаковка
    try:
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, arcname=f.name)
                log.debug("Бэкап: упакован '%s'", f.name)
    except OSError as e:
        log.error("Бэкап: ошибка записи архива: %s", e)
        archive.unlink(missing_ok=True)
        return None

    # Шаг 5: контроль результата
    sha = _sha256_file(archive)
    size = archive.stat().st_size
    log.info("Бэкап: создан '%s' (%d файлов, %d байт, sha=%s…)",
             archive.name, len(files), size, sha[:12])

    # Шаг 6: журнал
    manifest = _load_manifest()
    manifest.append({
        "file": archive.name,
        "created": datetime.now().isoformat(timespec="seconds"),
        "files": len(files),
        "invalid": invalid,
        "sha256": sha,
        "size": size,
    })
    _save_manifest(manifest)

    # Шаг 7: ротация
    archives = sorted(backups_dir.glob(f"{prefix}_*.zip"),
                      key=lambda p: p.stat().st_mtime)
    if len(archives) > max_copies:
        for old in archives[: len(archives) - max_copies]:
            known = {e["file"] for e in manifest}
            if old.name in known:
                old.unlink()
                log.info("Бэкап: удалён старый архив '%s' (ротация)", old.name)

    return archive


# -----------------------------------------------------
# 2. Восстановление

def restore_templates(archive: Path | None = None,
                      templates_dir: Path = TEMPLATES_DIR,
                      backups_dir: Path = BACKUPS_DIR,
                      force: bool = False,
                      skip_invalid: bool = False) -> dict[str, Any] | None:
    """Восстанавливает шаблоны из архива. Возвращает отчёт или None."""
    if archive is None:
        candidates = sorted(backups_dir.glob("templates_*.zip"),
                            key=lambda p: p.stat().st_mtime)
        if not candidates:
            log.error("Восстановление: в %s нет архивов", backups_dir)
            return None
        archive = candidates[-1]

    archive = Path(archive)
    log.info("Восстановление: старт, source=%s", archive)

    # Шаг 1: источник
    if not archive.is_file() or not zipfile.is_zipfile(archive):
        log.error("Восстановление: '%s' не ZIP или не найден", archive)
        return None

    # Шаг 2: целостность архива
    sha = _sha256_file(archive)
    manifest = _load_manifest()
    record = next((e for e in manifest if e["file"] == archive.name), None)
    if record and record.get("sha256") != sha:
        msg = f"hash архива не совпадает с журналом ({sha[:12]}… vs {record['sha256'][:12]}…)"
        if not force:
            log.error("Восстановление: %s; используйте force=True", msg)
            return None
        log.warning("Восстановление: %s, продолжаю (force=True)", msg)

    # Шаг 3: валидация содержимого в памяти
    valid: dict[str, dict] = {}
    invalid_names: list[str] = []
    try:
        with zipfile.ZipFile(archive) as zf:
            for name in zf.namelist():
                if not name.endswith(".json"):
                    continue
                try:
                    data = json.loads(zf.read(name).decode("utf-8"))
                    ok, reason = _validate_template(data)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    ok, reason = False, str(e)
                if ok:
                    valid[name] = data
                else:
                    invalid_names.append(name)
                    log.error("Восстановление: '%s' невалиден: %s", name, reason)
    except zipfile.BadZipFile as e:
        log.error("Восстановление: архив повреждён: %s", e)
        return None

    if invalid_names and not skip_invalid:
        log.error("Восстановление: %d невалидных шаблонов, прерываю "
                  "(используйте skip_invalid=True)", len(invalid_names))
        return None
    if not valid:
        log.error("Восстановление: в архиве нет валидных шаблонов")
        return None

    # Шаг 4: страховочная копия текущего состояния
    pre_restore = backup_templates(templates_dir, backups_dir,
                                   prefix="pre_restore")
    if templates_dir.is_dir() and any(templates_dir.glob("*.json")) and pre_restore is None:
        log.error("Восстановление: не удалось создать pre_restore, прерываю")
        return None

    # Шаг 5: атомарная замена через временный каталог
    tmp = templates_dir / ".restore_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    try:
        with zipfile.ZipFile(archive) as zf:
            for name, data in valid.items():
                (tmp / name).write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        # удалить старые *.json (не трогая .restore_tmp)
        templates_dir.mkdir(parents=True, exist_ok=True)
        for old in templates_dir.glob("*.json"):
            old.unlink()
        # переместить новые
        for f in tmp.glob("*.json"):
            shutil.move(str(f), str(templates_dir / f.name))
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)

    # Шаг 6: лог
    log.info("Восстановление: завершено, %d файлов из '%s'",
             len(valid), archive.name)
    if invalid_names:
        log.warning("Восстановление: пропущено %d невалидных: %s",
                    len(invalid_names), invalid_names)

    # Шаг 7: сверка
    mismatched = []
    for name in valid:
        try:
            data = json.loads((templates_dir / name).read_text(encoding="utf-8"))
            if _template_hash(data) != data.get("hash"):
                mismatched.append(name)
        except (json.JSONDecodeError, OSError):
            mismatched.append(name)
    if mismatched:
        log.error("Восстановление: сверка не прошла для %s", mismatched)

    return {
        "restored": len(valid),
        "skipped": invalid_names,
        "source": str(archive),
        "pre_restore": str(pre_restore) if pre_restore else None,
    }


# -----------------------------------------------------
# 3. Список архивов

def list_backups(backups_dir: Path = BACKUPS_DIR) -> list[dict]:
    if not backups_dir.is_dir():
        return []
    result = []
    for p in sorted(backups_dir.glob("*.zip"),
                    key=lambda x: x.stat().st_mtime, reverse=True):
        result.append({
            "file": p.name,
            "size": p.stat().st_size,
            "created": datetime.fromtimestamp(p.stat().st_mtime)
                                .isoformat(timespec="seconds"),
        })
    return result


# -----------------------------------------------------
# CLI

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Бэкап шаблонов матриц")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backup", action="store_true")
    group.add_argument("--restore", action="store_true")
    group.add_argument("--list", action="store_true")
    parser.add_argument("--archive", type=str, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-invalid", action="store_true")
    args = parser.parse_args()

    if args.backup:
        path = backup_templates()
        print(f"Архив: {path}" if path else "Бэкап не создан")
    elif args.restore:
        report = restore_templates(
            Path(args.archive) if args.archive else None,
            force=args.force,
            skip_invalid=args.skip_invalid,
        )
        print(report if report else "Восстановление не выполнено")
    elif args.list:
        for item in list_backups():
            print(f"{item['created']}  {item['size']:>8} Б  {item['file']}")