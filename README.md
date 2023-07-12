# Duplicado MP3 Finder

This Python script helps you find duplicate MP3 files in specified directories and moves inferior duplicates to a separate folder called "Duplicado". It compares files based on bitrate, filesize, and location to determine which files are considered duplicates.

## Prerequisites

- Python 3.x
- FFmpeg: FFmpeg is required for audio processing. Make sure it is installed and accessible in the command-line path.

## Setup

1. Clone or download the repository.
2. Install the required Python dependencies by running the following command:

```shell
pip install -r requirements.txt
```

3. Set up the `pyproject.toml` file by running the following command:

```shell
poetry install
```

## Usage

```python
from duplicado import move_duplicate_mp3

# Specify the source directories to search for MP3 files
source_directories = ['/path/to/your/first/mp3/directory', '/path/to/your/second/mp3/directory']

# Specify the target directory where inferior duplicates will be moved
target_directory = '/path/to/Duplicado'

# Move duplicate MP3 files
move_duplicate_mp3(source_directories, target_directory)
```

Replace `/path/to/your/first/mp3/directory`, `/path/to/your/second/mp3/directory`, and `/path/to/Duplicado` with the actual paths on your system.

## Customization

- You can modify the criteria for determining inferior duplicates by adjusting the logic in the `move_duplicate_mp3` function.
- The script uses the `pydub` library for audio processing and the `pymongo` library for connecting to a MongoDB database. Ensure these dependencies are installed if you intend to use them.

## Limitations

- The script currently supports MP3 files only. It may not work correctly with other audio formats.
- The script uses FFmpeg and FFprobe for audio processing. Make sure these tools are installed and accessible in the command-line path.

