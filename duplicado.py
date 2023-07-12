import os
import hashlib
import shutil
import logging
from pydub import AudioSegment
from mutagen.mp3 import MP3
from pymongo import MongoClient

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    artist = audio.tags.get('TPE1', [None])[0]
    track = audio.tags.get('TIT2', [None])[0]
    return artist, track

def move_duplicate_mp3(source_directories, target_directory):
    client = MongoClient('localhost', 27017)
    db = client['audiodb']
    collection = db['audiofiles']

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    recent_files = []

    for source_directory in source_directories:
        for dirpath, dirnames, filenames in os.walk(source_directory):
            for filename in filenames:
                if filename.endswith('.mp3'):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        audio_hash = get_audio_hash(filepath)
                        bitrate = get_audio_bitrate(filepath)
                        filesize = os.path.getsize(filepath)
                        artist, track = get_audio_tags(filepath)

                        existing_file = collection.find_one({'audio_hash': audio_hash, 'artist': artist, 'track': track})

                        if existing_file is not None:
                            if (bitrate < existing_file['bitrate'] or
                                (bitrate == existing_file['bitrate'] and filesize < existing_file['filesize'])):
                                shutil.move(filepath, os.path.join(target_directory, filename))
                                reason = f"Moved because bitrate is {'lower' if bitrate < existing_file['bitrate'] else 'equal'} and filesize is smaller."
                            else:
                                shutil.move(existing_file['filepath'], os.path.join(target_directory, filename))
                                existing_file['filepath'] = filepath
                                existing_file['bitrate'] = bitrate
                                existing_file['filesize'] = filesize
                                reason = f"Moved because bitrate is {'lower' if existing_file['bitrate'] < bitrate else 'equal'} and filesize is smaller."
                                collection.update_one({'_id': existing_file['_id']}, {"$set": existing_file, "$set": {"reason": reason}})
                        else:
                            document = {'audio_hash': audio_hash, 'filepath': filepath, 'bitrate': bitrate, 'filesize': filesize, 'artist': artist, 'track': track}
                            collection.insert_one(document)
                            reason = "Inserted new file."

                        recent_files.append((filepath, reason))
                        if len(recent_files) > 10:
                            recent_files.pop(0)

                        # Print last 10 processed files
                        print('\033c')  # Clear console
                        for file, reason in recent_files:
                            print(f"{file} - {reason}")
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")

# Example usage:
# move_duplicate_mp3(['/path/to/your/first/mp3/directory', '/path/to/your/second/mp3/directory'], '/path/to/Duplicado')
