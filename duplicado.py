from curses import meta
import os
import hashlib
import shutil
import logging
from pydub import AudioSegment
from mutagen.mp3 import MP3
from pymongo import MongoClient
from tqdm import tqdm
# Set up logging
logging.basicConfig(level=logging.INFO)
source_directories = ["/Volumes/Disk 1/Dropbox", "/Volumes/Disk 1/GplayLibrary"]
target_directory = '/Volumes/Disk 1/Duplicado'

def get_audio_hash(mp3_path):
    """Generate a hash for the audio data in an MP3 file."""
    audio = AudioSegment.from_mp3(mp3_path)
    audio_hash = hashlib.sha256(audio.raw_data).hexdigest()
    return audio_hash


def get_audio_bitrate(mp3_path):
    """Get the bitrate of an MP3 file."""
    audio = MP3(mp3_path)
    return audio.info.bitrate


def get_audio_tags(mp3_path):
    """Get the artist and track name from an MP3 file's ID3 tags."""
    audio = MP3(mp3_path)
    artist = audio.tags.get("TPE1", [None])[0]
    track = audio.tags.get("TIT2", [None])[0]
    return artist, track

def generate_metadata(source_directories, db):
    metadata = []

    hashed_files = db['hashedfiles'].find({}, {'filepath': 1})
    hashed_files = [hashed_file['filepath'] for hashed_file in hashed_files]

    print("Generating metadata...")

    for source_directory in source_directories:
        for dirpath, dirnames, filenames in os.walk(source_directory):
            for filename in filenames:
                if filename.endswith('.mp3'):
                    filepath = os.path.join(dirpath, filename)
                    if filepath in hashed_files:
                        continue
                    try:
                        audio_hash = get_audio_hash(filepath)
                        bitrate = get_audio_bitrate(filepath)
                        filesize = os.path.getsize(filepath)
                        artist, track = get_audio_tags(filepath)

                        metadata.append({
                            'audio_hash': audio_hash,
                            'filepath': filepath,
                            'bitrate': bitrate,
                            'filesize': filesize,
                            'artist': artist,
                            'track': track
                        })

                        document = {
                            'audio_hash': audio_hash,
                            'filepath': filepath,
                            'bitrate': bitrate,
                            'filesize': filesize,
                            'artist': artist,
                            'track': track
                        }
                        db['audiofiles'].insert_one(document)

                        print(f"Processed file: {filepath}")
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")

    print("Metadata generation completed.")

    return metadata

def move_duplicate_mp3(metadata, target_directory, db):
    collection = db['audiofiles']

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    progress_bar = tqdm(total=len(metadata), desc="Processing", unit="file")

    for file_data in metadata:
        audio_hash = file_data['audio_hash']
        filepath = file_data['filepath']
        bitrate = file_data['bitrate']
        filesize = file_data['filesize']
        artist = file_data['artist']
        track = file_data['track']

        existing_file = collection.find_one({'audio_hash': audio_hash, 'artist': artist, 'track': track})

        if existing_file is not None:
            if (bitrate < existing_file['bitrate'] or
                (bitrate == existing_file['bitrate'] and filesize < existing_file['filesize'])):
                shutil.move(filepath, os.path.join(target_directory, os.path.basename(filepath)))
                reason = f"Moved because bitrate is {'lower' if bitrate < existing_file['bitrate'] else 'equal'} and filesize is smaller."
            else:
                shutil.move(existing_file['filepath'], os.path.join(target_directory, os.path.basename(filepath)))
                existing_file['filepath'] = filepath
                existing_file['bitrate'] = bitrate
                existing_file['filesize'] = filesize
                reason = f"Moved because bitrate is {'lower' if existing_file['bitrate'] < bitrate else 'equal'} and filesize is smaller."
                collection.update_one({'_id': existing_file['_id']}, {"$set": existing_file, "$set": {"reason": reason}})
        else:
            document = {'audio_hash': audio_hash, 'filepath': filepath, 'bitrate': bitrate, 'filesize': filesize, 'artist': artist, 'track': track}
            collection.insert_one(document)
            reason = "Inserted new file."

        db['hashedfiles'].insert_one({'filepath': filepath})
        progress_bar.set_postfix({'Reason': reason})
        progress_bar.update(1)

    progress_bar.close()


if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    db = client['audiodb']
    metadata = generate_metadata(source_directories, db)
    move_duplicate_mp3(metadata, target_directory, db)
