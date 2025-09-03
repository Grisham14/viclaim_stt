import os
import pandas as pd
from src.transcribe import transcribe_audio, yt_to_data
import torch


def map_transcription_chunks_to_sentences(transcription_data, time_start, time_end, offset=0.25):    
    sentence_list = [] 
    chunk_list = [] 
    for chunk in transcription_data['chunks']:
        if (time_start <= chunk["timestamp"][0] and chunk["timestamp"][1] <= time_end) \
            or (time_start >= chunk["timestamp"][0] and time_end <= chunk["timestamp"][1]) \
            or (time_start >= chunk["timestamp"][0] and time_start <= chunk["timestamp"][1]):
            # or (time_start <= chunk["timestamp"][0] and time_end >= chunk["timestamp"][0]):
            chunk_list.append(chunk)
            sentence_list.append(chunk["text"])
            
    sentence = (''.join(sentence_list)).strip()
    
    return sentence


def add_transcriptions(dataset_filepath: str, clip_id: str, output_dir: str, temp_dir: str):
    # load the dataset into pandas dataframe
    df = pd.read_csv(dataset_filepath)

    required_cols = {"clip_id", "sentence_start_millis", "sentence_end_millis"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in dataset: {sorted(missing)}")
    
    # download the youtube clip 
    video_id = yt_to_data.download(clip_id=clip_id, data_folder=temp_dir)

    audio_file = os.path.join(temp_dir, video_id, f"{video_id}.mp3")
    transcription_data = transcribe_audio.transcribe(audio_file)
    transcription_data = transcribe_audio.transcribe_assembly_ai(audio_file)

    # --- Prepare an output copy; default empty strings for 'sentence'
    if "sentence" not in df.columns:
        df["sentence"] = ""

    # --- Compute sentences for rows that match clip_id
    mask = (df["clip_id"] == clip_id)

    # Iterate rows properly (avoid 'for row in df' which yields column names)
    sentences = []
    for row in df.loc[mask].itertuples(index=False):
        # Access by attribute names that match column headers
        time_start = float(getattr(row, "sentence_start_millis")) / 1000.0
        time_end   = float(getattr(row, "sentence_end_millis")) / 1000.0

        # Align transcription to this window
        s = map_transcription_chunks_to_sentences(transcription_data, time_start, time_end)
        sentences.append(s if s is not None else "")

    # Assign back in one go to avoid SettingWithCopy issues
    df.loc[mask, "sentence"] = sentences

    # --- Save expanded dataset
    # Name output file based on clip_id to avoid overwriting your original dataset
    base = os.path.splitext(os.path.basename(dataset_filepath))[0]
    out_path = os.path.join(output_dir, f"{base}__with_sentences__{clip_id}.csv")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df.to_csv(out_path, index=False)
    
