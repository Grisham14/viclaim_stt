import os
import subprocess
import sys
import gc 
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import librosa
import assemblyai as aai


def detect_language(audio_file, processor, model, device):
    # Load the audio
    audio, sr = librosa.load(audio_file, sr=16000)  # Ensure 16kHz sampling rate

    # Preprocess with Whisper processor
    input_features = processor.feature_extractor(audio, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    detected_lang_token_id = model.detect_language(input_features)
    
    detected_lang = 'en' 
    detected_lang_raw = processor.tokenizer.decode([detected_lang_token_id.item()])
    if detected_lang_raw:
        detected_lang = detected_lang_raw.replace('<|', '').replace('|>', '')
        
    print(f"Detected Language: {detected_lang}")
    return detected_lang


def transcribe(audio_file: str):
    print(f'is cuda available: {torch.cuda.is_available()}')
    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda' 
    elif torch.backends.mps.is_available():
        device = "mps"
        
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    whisper = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        dtype=torch_dtype,
        device=device,
    )

    transcription_result = whisper(
        audio_file, 
        return_timestamps="word", # word level timestamps
        # return_timestamps=True, # sentence level timestamps
    )
    
    return transcription_result


def transcribe_assembly_ai(audio_file: str):
    """
    Transcribe a local audio file with AssemblyAI and return:
      {
        "text": <full transcript>,
        "words": [{"word": ..., "start": ms, "end": ms, "confidence": float}, ...],
        "segments": [{"text": ..., "start": ms, "end": ms, "speaker": id_or_None}, ...]
      }

    Notes:
      - Timestamps are in MILLISECONDS (AssemblyAI convention).
      - Provide ASSEMBLYAI_API_KEY via environment variable.
      - `audio_file` can be a local path; the SDK handles upload.
    """
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set ASSEMBLYAI_API_KEY in your environment.")
    aai.settings.api_key = api_key

    # Configure transcription (adjust as needed)
    config = aai.TranscriptionConfig(
        punctuate=True,
        format_text=True,
        speaker_labels=False,  # set True if you want diarization + utterances
        # language_code="en",   # optionally force a language code
    )

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file, config=config)

    if transcript.status != aai.TranscriptStatus.completed:
        # `transcript.error` often includes a human-readable message
        raise RuntimeError(f"Transcription failed: {transcript.status} - {transcript.error}")

    # Build a Whisper-like structure you can consume elsewhere
    transcription_data = {
        "chunks": [
            {
                "text": " " + w.text,
                "timestamp": [
                    float(w.start) / 1000.0,         # ms
                    float(w.end) / 1000.0
                ],
                "confidence": w.confidence,
            }
            for w in (transcript.words or [])
        ],
    }
    return transcription_data