import os
import sys
import subprocess
import argparse

# Function to convert audio and video files to 16-bit PCM wav using ffmpeg
def convert_to_wav_ffmpeg(input_path, output_path):
    try:
        # Call ffmpeg to convert to 16-bit PCM WAV
        subprocess.run([
            "ffmpeg", "-i", input_path, output_path
        ], check=True)
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {input_path}: {e}")

# Function to convert all files in a folder
def convert_to_wav(folder_path):
    # Supported file extensions for conversion
    supported_extensions = [".mp3", ".m4a", ".m4v", ".mp4", ".mkv", ".ogg"]
    
    # Create 'wav' folder if it doesn't exist
    wav_folder = os.path.join(folder_path, "wav")
    if not os.path.exists(wav_folder):
        os.makedirs(wav_folder)
    
    # List all files in the folder
    for filename in os.listdir(folder_path):
        # Get the file extension
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Check if the file has a supported extension
        if file_extension in supported_extensions:
            # Define the full path for input and output files
            input_path = os.path.join(folder_path, filename)
            wav_path = os.path.join(wav_folder, os.path.splitext(filename)[0] + ".wav")

            # Convert the file using ffmpeg
            convert_to_wav_ffmpeg(input_path, wav_path)

# Main function to handle command-line arguments
def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Convert audio/video files to 16-bit PCM WAV format.")
    
    # Add the mandatory -f argument for the folder path
    parser.add_argument('-f', '--folder', required=True, help="Folder path containing files to convert")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Check if the folder exists
    folder_path = args.folder
    if os.path.isdir(folder_path):
        convert_to_wav(folder_path)
    else:
        print(f"Error: {folder_path} is not a valid directory")

# Entry point of the script
if __name__ == "__main__":
    main()