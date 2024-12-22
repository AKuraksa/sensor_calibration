import os

def validate_files(files):
    """
    Validate if files exist and return their full paths.

    Parameters:
        files (list): List of file names without extensions.

    Returns:
        list: List of valid file paths.
    """
    paths = [f"./data_parsed/{file.strip()}.csv" for file in files]
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not exist.")
    # Debug: Print validated file paths
    # print(f"Validated file paths: {paths}")
    return paths