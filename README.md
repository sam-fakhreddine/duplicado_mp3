# Duplicate MP3 Finder

This Python script helps you find duplicate MP3 files in specified directories and moves inferior duplicates to a separate folder called "Duplicado". It compares files based on bitrate, filesize, and location to determine which files are considered duplicates.

## Prerequisites

- Python 3.x
- FFmpeg: FFmpeg is required for audio processing. Make sure it is installed and accessible in the command-line path.
- MongoDB: This script uses MongoDB to store and manage metadata for the MP3 files. If you don't have MongoDB installed, you can set it up locally using the instructions below.

## MongoDB Setup

1. Install MongoDB on your system by following the official installation guide: [MongoDB Installation](https://docs.mongodb.com/manual/installation/).

2. Start the MongoDB service. For example, on Linux, you can use the following command:

```shell
sudo service mongod start
```

3. Connect to MongoDB and create a database and collection for the script. You can use the following commands in the MongoDB shell:

```shell
mongo
use audiodb
db.createCollection('audiofiles')
```

## Setup

1. Clone or download the repository.

2. Set up the `pyproject.toml` file by running the following command:

```shell
poetry install
```

3. Update the MongoDB connection details in the `duplicado.py` file. Modify the following line with your MongoDB connection information:

```python
client = MongoClient('localhost', 27017)
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
- The script uses the `pydub` library for audio processing and the `pymongo` library for connecting to MongoDB. Ensure these dependencies are installed if you intend to use them.

## Limitations

- The script currently supports MP3 files only. It may not work correctly with other audio formats.
- The script uses FFmpeg and FFprobe for audio processing. Make sure these tools are installed and accessible in the command-line path.


Make sure to replace `/path/to/your/first/mp3/directory`, `/path/to/your/second/mp3/directory`, and `/path/to/Duplicado` with the actual paths on your system. Additionally, update the MongoDB connection details in the `duplicado.py` file as instructed in the setup section.
