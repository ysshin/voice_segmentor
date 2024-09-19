import os
import sys
import torch
import soundfile as sf
import numpy as np
import argparse
import onnxruntime as ort

# Set ONNX Runtime log severity to ERROR (or FATAL to suppress everything except crashes)
ort.set_default_logger_severity(3)

SAMPLING_RATE = 16000
DEFAULT_MIN_DB_LEVEL = -80.0  # Default dB level if not provided
EXTENSION_MS = 500  # 500 milliseconds

def filter_by_db_level(audio_segment, min_db):
    # Convert PyTorch tensor to NumPy array
    if isinstance(audio_segment, torch.Tensor):
        audio_segment = audio_segment.numpy()

    rms = np.sqrt(np.mean(np.square(audio_segment)))
    db = 20 * np.log10(rms)
    return db >= min_db

def split_wav_by_voice(input_wav, min_db_level):
    # Load the model
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=True,
                                  onnx=True)

    (get_speech_ts, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # Read the audio file
    wav_data = read_audio(input_wav, sampling_rate=SAMPLING_RATE)

    # Detect speech segments
    speech_timestamps = get_speech_ts(
        audio=wav_data,
        model=model,
        sampling_rate=SAMPLING_RATE
    )

    # Extract the original filename without the extension
    original_filename = os.path.splitext(os.path.basename(input_wav))[0]

    # Create output folder with the format: originalfilename_segment_xxxms_yyydb
    abs_min_db_level = abs(int(min_db_level))  # Convert dB level to absolute integer
    output_folder = f"{original_filename}_segment_{EXTENSION_MS}ms_{abs_min_db_level}db"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filtered_timestamps = []
    
    extension_samples = int(EXTENSION_MS * SAMPLING_RATE / 1000)  # Convert ms to samples

    for i, segment in enumerate(speech_timestamps):
        start = segment['start']
        end = segment['end']

        # Adjust start: Only if this segment doesn't overlap with the previous one
        if i > 0:  # Check if there's a previous segment
            previous_end = speech_timestamps[i - 1]['end']
            if start - extension_samples > previous_end:  # No overlap with the previous segment
                start = max(0, start - extension_samples)  # Add EXTENSION_MS earlier, ensuring start is not less than 0
        else:
            # If it's the first segment, just extend it by EXTENSION_MS
            start = max(0, start - extension_samples)

        # Adjust end: Only if this segment doesn't overlap with the next one
        if i < len(speech_timestamps) - 1:  # Check if there's a next segment
            next_start = speech_timestamps[i + 1]['start']
            if end + extension_samples < next_start:  # No overlap with the next segment
                end = min(len(wav_data), end + extension_samples)  # Add EXTENSION_MS after, ensuring end is within audio length
        else:
            # If it's the last segment, extend it by EXTENSION_MS
            end = min(len(wav_data), end + extension_samples)

        # Extract the segment and apply dB filtering
        segment_audio = wav_data[start:end]
        if filter_by_db_level(segment_audio, min_db_level):
            filtered_timestamps.append(segment)
            # Updated to use 4-digit numbering
            segment_filename = f'{output_folder}/{original_filename}_segment_{len(filtered_timestamps):04}.wav'
            sf.write(segment_filename, segment_audio, SAMPLING_RATE)

    print(f"{len(filtered_timestamps)} voice segments above {min_db_level} dB extracted and saved to {output_folder}")

def process_folder(folder, min_db_level):
    # Process all .wav files in the given folder
    for filename in os.listdir(folder):
        if filename.endswith(".wav"):
            input_wav = os.path.join(folder, filename)
            print(f"Processing {input_wav}")
            split_wav_by_voice(input_wav, min_db_level)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process WAV files for speech separation with Sepformer.")
    parser.add_argument("-f", "--folder", help="Folder containing WAV files to process")
    parser.add_argument("input_wav", nargs="?", help="Single WAV file to process (if not using folder)")
    parser.add_argument("--min_db_level", type=float, default=DEFAULT_MIN_DB_LEVEL, help="Minimum dB level for filtering")
    
    args = parser.parse_args()

    if args.folder:
        if not os.path.isdir(args.folder):
            print(f"Error: The specified folder {args.folder} does not exist.")
            sys.exit(1)
        process_folder(args.folder, args.min_db_level)
    elif args.input_wav:
        if not os.path.exists(args.input_wav):
            print("Error: The input WAV file does not exist.")
            sys.exit(1)
        split_wav_by_voice(args.input_wav, args.min_db_level)
    else:
        print("Usage: python script.py <input_wav> or -f <folder> [--min_db_level]")
        sys.exit(1)