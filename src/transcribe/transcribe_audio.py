import os
import subprocess
import sys
import gc 
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import librosa


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


def transcribe(audio_file):
    print(f'is cuda available: {torch.cuda.is_available()}')
    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda' 
    elif torch.backends.mps.is_available():
        device = "mps"
        
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    whisper = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )

    # dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
    # sample = dataset[0]["audio"]

    transcription_result = whisper(
        audio_file, 
        return_timestamps="word", # word level timestamps
        # return_timestamps=True, # sentence level timestamps
    )
    
    return transcription_result