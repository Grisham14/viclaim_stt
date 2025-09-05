import os
from typing import Any, Dict, List, Optional
import pandas as pd
from tqdm import tqdm
from src.transcribe import transcribe_audio, yt_to_data


def map_transcription_chunks_to_sentences(transcription_data, time_start, time_end):    
    sentence_list = [] 
    chunk_list = [] 
    for chunk in transcription_data['chunks']:
        if (time_start <= chunk["timestamp"][0] and chunk["timestamp"][1] <= time_end) \
            or (time_start >= chunk["timestamp"][0] and time_end <= chunk["timestamp"][1]) \
            or (time_start >= chunk["timestamp"][0] and time_start <= chunk["timestamp"][1]):
            chunk_list.append(chunk)
            sentence_list.append(chunk["text"])
            
    sentence = (''.join(sentence_list)).strip()
    
    return sentence


def add_transcriptions(
        dataset_filepath: str, 
        temp_dir: str,
        output_filepath: str,
        clips_to_transcribe: Optional[List[str]] = None,
        use_assembly_ai: bool = False
    ):
    # load the dataset into pandas dataframe
    df = pd.read_csv(dataset_filepath)

    required_cols = {"clip_id", "sentence_start_millis", "sentence_end_millis"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in dataset: {sorted(missing)}")

    # if no clips specified → transcribe all
    if clips_to_transcribe is None:
        clips_to_transcribe = df["clip_id"].unique().tolist()

    # prepare an output copy; default empty strings for 'sentence'
    if "sentence" not in df.columns:
        df["sentence"] = ""

    # Counters + per-clip status
    stats = {
        "download_ok": 0,
        "download_fail": 0,
        "transcribe_ok": 0,
        "transcribe_fail": 0,
    }
    failures: List[Dict[str, Any]] = []

    # process each clip
    for clip_id in tqdm(clips_to_transcribe, desc="Processing clips", unit="clip"):
        # download the youtube clip 
        try:
            video_id = yt_to_data.download(clip_id=clip_id, data_folder=temp_dir)
            audio_file = os.path.join(temp_dir, video_id, f"{video_id}.mp3")
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found after download: {audio_file}")
            stats["download_ok"] += 1
        except Exception as e:
            stats["download_fail"] += 1
            failures.append({"clip_id": clip_id, "stage": "download", "error": str(e)})
            # skip transcription/mapping for this clip
            continue
        
        # transcribe the audio
        try:
            if use_assembly_ai:
                transcription_data = transcribe_audio.transcribe_assembly_ai(audio_file)
            else:
                transcription_data = transcribe_audio.transcribe(audio_file)
            stats["transcribe_ok"] += 1
        except Exception as e:
            stats["transcribe_fail"] += 1
            failures.append({"clip_id": clip_id, "stage": "transcribe", "error": str(e)})
            # skip mapping for this clip
            continue

        # map transcription to each row (only for this clip)
        mask = (df["clip_id"] == clip_id)
        sentences: List[str] = []

        # iterate rows
        for row in df.loc[mask].itertuples(index=False):
            # access by attribute names that match column headers
            time_start = float(getattr(row, "sentence_start_millis")) / 1000.0
            time_end   = float(getattr(row, "sentence_end_millis")) / 1000.0

            try:
                s = map_transcription_chunks_to_sentences(transcription_data, time_start, time_end)
            except Exception as e:
                # On mapping error, treat as empty sentence but record the failure detail
                s = ""
                failures.append({"clip_id": clip_id, "stage": "mapping", "error": str(e)})

            sentences.append(s if s is not None else "")

        # assign back in one go to avoid SettingWithCopy issues
        df.loc[mask, "sentence"] = sentences

    # keep only rows that actually received a sentence
    df_out = df[df["sentence"].astype(str).str.strip() != ""].copy()
        
    # save expanded dataset
    directory = os.path.dirname(os.path.abspath(output_filepath))
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    df_out.to_csv(output_filepath, index=False)
    

    # final report
    total = len(clips_to_transcribe)
    print("\n========= Transcription Report =========")
    print(f"Total clips requested:        {total}")
    print(f"Downloads:   OK={stats['download_ok']}   FAIL={stats['download_fail']}")
    print(f"Transcribes: OK={stats['transcribe_ok']} FAIL={stats['transcribe_fail']}")
    mapped_rows = (df["sentence"].astype(str).str.strip() != "").sum()
    print(f"Rows with mapped sentences:   {mapped_rows} / {len(df)}")
    print(f"Rows kept in output dataset:  {len(df_out)}")
    if failures:
        print("\nFailures detail (up to first 10 shown):")
        for rec in failures[:10]:
            print(f" - clip_id={rec['clip_id']} | stage={rec['stage']} | error={rec['error']}")
        if len(failures) > 10:
            print(f" ... and {len(failures)-10} more")