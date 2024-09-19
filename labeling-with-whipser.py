import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from openpyxl import Workbook
import argparse

# Initialize device and model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# Function to process all .wav files in the folder
def transcribe_wav_files(folder):
    # Normalize folder path to remove trailing slashes and extract folder name
    folder_name = os.path.basename(os.path.normpath(folder))

    # Get all .wav files in the folder, sorted by name
    wav_files = sorted([f for f in os.listdir(folder) if f.endswith('.wav')])

    # Create a new Excel workbook and sheet
    wb = Workbook()
    sheet = wb.active
    sheet.title = folder_name  # Set folder name as sheet name
    sheet.append(["Filename", "Transcription"])  # Add header

    # Process each .wav file
    for wav_file in wav_files:
        wav_path = os.path.join(folder, wav_file)
        print(f"Processing {wav_file}...")

        # Transcribe the wav file
        result = pipe(wav_path, generate_kwargs={"language": "korean"})
        transcription = result["text"]

        # Add filename (without extension) and transcription to the sheet
        sheet.append([os.path.splitext(wav_file)[0], transcription])

    # Save the workbook with the same name as the folder
    excel_filename = f"{folder_name}.xlsx"
    wb.save(excel_filename)
    print(f"Transcriptions saved to {excel_filename}")

# Parse input arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe WAV files in a folder.')
    parser.add_argument('-f', '--folder', required=True, help='Path to the folder containing WAV files')
    
    args = parser.parse_args()

    # Transcribe the files in the provided folder
    transcribe_wav_files(args.folder)
