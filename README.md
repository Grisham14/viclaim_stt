# viclaim_stt

#### Windows
```bash
py -3.10 -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
python ./dataset_functions/dataset_parser.py path_to_your_csv_file.csv
python ./dataset_functions/dataset_parser.py ./data/csv_raw/single_annotator_dataset.csv
```


#### Mac
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ./dataset_functions/dataset_parser.py path_to_your_csv_file.csv
python ./dataset_functions/dataset_parser.py ./data/csv_raw/single_annotator_dataset.csv
```