import os
import shutil

def organize_files_by_sensor(root_dir: str) -> int:
    """
    Sort signal files into folders by sensor number for each turbine.

    parameters:
    root_dir - root directory containing turbine folders

    returns:
    total number of processed (copied) files
    """

    turbine_folders = [
        f for f in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, f)) and not f.startswith("data-")
    ]

    total = 0

    for turbine in turbine_folders:
        turbine_path = os.path.join(root_dir, turbine)
        sorted_path = os.path.join(root_dir, "data-" + turbine)

        os.makedirs(sorted_path, exist_ok=True)

        for i in range(1, 9):
            os.makedirs(os.path.join(sorted_path, str(i)), exist_ok=True)

        print(f"\nprocessing turbine: {turbine}")

        for filename in os.listdir(turbine_path):
            file_path = os.path.join(turbine_path, filename)

            if not os.path.isfile(file_path):
                continue

            try:
                splited_path = filename.split("_")
                other = splited_path[3].split(".")
                sensor_num = int(other[1])

                dest_folder = os.path.join(sorted_path, str(sensor_num))
                dest_path = os.path.join(dest_folder, filename)

                if not os.path.exists(dest_path):
                    shutil.copy(file_path, dest_path)
                    total += 1
                    print(f"{filename} → sensor {sensor_num}")
                else:
                    print(f"skipped (already exists): {filename}")

            except Exception as e:
                print(f"error in {filename}: {e}")

    print(f"\nDONE! total files sorted: {total}")
    return total


def count_files_in_folders(folders: list) -> int:
    """
    Count total number of files in given folders.

    parameters:
    folders - list of folder paths

    returns:
    total number of files
    """

    total = 0

    for folder in folders:
        count = len([
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ])

        print(f"{folder}: {count}")
        total += count

    print(f"\nTOTAL: {total}")
    return total
