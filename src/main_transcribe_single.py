import argparse

from src.transcribe import ts_manager


def main():
    parser = argparse.ArgumentParser(description="Merge datasets.")
    
    parser.add_argument('--dataset_filepath', type=str, required=True, help='The path to the dataset file.')    
    parser.add_argument('--clip_id', type=str, required=True, help='The clip id you want to transcribe.')
    parser.add_argument('--output_dir', type=str, required=True, help='The ouput path to the resulting dataset file.')
    parser.add_argument('--temp_dir', type=str, required=True, help='The temp dir path, where the video data will be stored.')

    args = parser.parse_args()

    ts_manager.add_transcriptions(args.dataset_filepath, args.clip_id, args.output_dir, args.temp_dir)

if __name__ == "__main__":
    main()