import os
import re
import shutil

def extract_turbine_id(folder_name: str) -> str:
    """
    Extract turbine ID from source folder name.

    Converts folder names like:
        'Signals_WTG_656_10k'  →  'WTG656'
        'Signals_WTG_513_10k'  →  'WTG513'

    Parameters:
    folder_name(str) : name of the source turbine folder.

    Returns:
    str : turbine ID matching the data- folder naming convention.
    """
    match = re.search(r"WTG_(\d+)", folder_name, re.IGNORECASE)
    if match:
        return f"WTG{match.group(1)}"
    return None


def extract_sensor_num(filename: str) -> int | None:
    """
    Extract sensor number from signal filename.

    Expected filename format:
        <start>_<end>_<duration>_<conditions>.<sensor><type><resampling><span>.<lor>.cms

    Parameters:
    filename(str) : signal filename.

    Returns:
    int or None : sensor number, or None if parsing fails.
    """
    try:
        parts = filename.split("_")
        other = parts[3].split(".")
        return int(other[1])
    except Exception:
        return None


def add_new_signals(new_signals_root: str, sorted_root: str) -> int:
    """
    Add new signal files into existing sorted data- folders.

    Walks through source turbine folders (e.g. Signals_WTG_656_10k/Signals_10k/),
    maps each to the corresponding data-WTG656/ folder in sorted_root,
    and copies files into the correct sensor subfolder.
    Skips files that already exist.

    Parameters:
    new_signals_root(str) : root folder containing new turbine signal folders
    sorted_root(str)      : root folder containing existing data- folders

    Returns:
    int : total number of newly copied files.
    """
    existing = {}
    for entry in os.scandir(sorted_root):
        if entry.is_dir() and entry.name.startswith("data-"):
            turbine_id = entry.name[len("data-"):]
            existing[turbine_id] = entry.path

    print(f"Found existing turbine folders: {list(existing.keys())}\n")

    total = 0

    for entry in os.scandir(new_signals_root):
        if not entry.is_dir():
            continue

        turbine_id = extract_turbine_id(entry.name)

        if turbine_id is None:
            print(f"[SKIP] Cannot parse turbine ID from: {entry.name}")
            continue

        if turbine_id not in existing:
            print(f"[SKIP] No matching data- folder for turbine: {turbine_id}")
            continue

        dest_turbine_root = existing[turbine_id]
        print(f"Processing: {entry.name}  →  {os.path.basename(dest_turbine_root)}")

        source_dir = entry.path
        for sub in os.scandir(entry.path):
            if sub.is_dir():
                source_dir = sub.path
                break

        copied = 0
        skipped = 0
        errors = 0

        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)

            if not os.path.isfile(file_path):
                continue

            sensor_num = extract_sensor_num(filename)

            if sensor_num is None:
                print(f"  [ERROR] Cannot parse sensor from: {filename}")
                errors += 1
                continue

            dest_folder = os.path.join(dest_turbine_root, str(sensor_num))

            if not os.path.isdir(dest_folder):
                print(f"  [SKIP] Sensor folder does not exist: {dest_folder}")
                errors += 1
                continue

            dest_path = os.path.join(dest_folder, filename)

            if os.path.exists(dest_path):
                skipped += 1
                continue

            shutil.copy(file_path, dest_path)
            copied += 1

        print(f"  copied: {copied}  |  skipped (already exist): {skipped}  |  errors: {errors}")
        total += copied

    print(f"\nDONE. Total new files copied: {total}")
    return total


if __name__ == "__main__":
    NEW_SIGNALS_ROOT = "new_signals"
    SORTED_ROOT = "signals-by-sensors"

    add_new_signals(NEW_SIGNALS_ROOT, SORTED_ROOT)
