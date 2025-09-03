import argparse


def main():
    parser = argparse.ArgumentParser(description="Merge datasets.")
    
    parser.add_argument('--dataset_filepath', type=bool, required=True, default=True, help='')    
    parser.add_argument('--clip_id', type=str, required=True, help='The path to the dataset file.')
    parser.add_argument('--output_dir', type=str, required=True, help='The ouput path to the resulting dataset file.')
    parser.add_argument('--temp_dir', type=str, required=True, help='The ouput path to the resulting dataset file.')

    args = parser.parse_args()

    ts_manager.add_transcriptions(args.data_folder, args.annotator_weights_file, args.output_dir)

if __name__ == "__main__":
    main()