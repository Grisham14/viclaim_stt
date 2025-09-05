import argparse

from src.transcribe import ts_manager


def main():
    parser = argparse.ArgumentParser(description="Merge datasets.")
    
    parser.add_argument('--dataset_filepath', type=str, required=True, help='The path to the dataset file.')   
    parser.add_argument('--output_filepath', type=str, required=True, help='The path to the resulting dataset file.')
    parser.add_argument('--temp_dir', type=str, required=True, help='The temp dir path, where the downloaded video data will be stored.')
    parser.add_argument(
        '--clips_to_transcribe',
        nargs='*',               # ← allows zero or more values
        default=None,            # ← if not provided → None
        help='List of clip IDs to transcribe (optional).'
    )    
    parser.add_argument(
        '--use_assembly_ai',
        action='store_true',
        help='Use AssemblyAI for transcription (default: False).'
    )

    args = parser.parse_args()

    use_assembly_ai = False
    if args.use_assembly_ai and isinstance(args.use_assembly_ai, bool):
        use_assembly_ai = args.use_assembly_ai

    ts_manager.add_transcriptions(
        dataset_filepath=args.dataset_filepath, 
        temp_dir=args.temp_dir, 
        output_filepath=args.output_filepath, 
        clips_to_transcribe=args.clips_to_transcribe, 
        use_assembly_ai=use_assembly_ai
    )
    

if __name__ == "__main__":
    main()