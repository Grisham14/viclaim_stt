# **ViClaim Dataset and Recreation Code**

Recreate sentence-level transcriptions for the **ViClaim** YouTube dataset using timestamps and state-of-the-art speech-to-text models.

## **About the Project**

This repository contains:

- **`viclaim.csv`** - The dataset containing YouTube video clips and timestamped claims.
- **Code** to **recreate transcriptions** based on the provided timestamps as accurately as possible.

The dataset is based on the paper:

> **ViClaim: A Multilingual Multilabel Dataset for Automatic Claim Detection in Videos**  
> [[Paper Link]](https://arxiv.org/abs/2504.12882)

---

## **Getting Started**

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/viclaim_stt.git
cd viclaim_stt
```

### **2. Create a Virtual Environment**

#### Windows

```bash
py -3.10 -m venv venv
venv\Scripts\activate
```

#### Mac / Linux

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## **Transcribing YouTube Clips**

The main transcription pipeline is implemented in **`src/main.py`**.  
You need to provide:

- The dataset CSV file
- An output path for the transcribed dataset
- A temporary folder for downloaded YouTube videos

### **Example Command**

```bash
python -m src.main \
  --dataset_filepath ./data/viclaim.csv \
  --output_filepath ./temp/dataset/viclaim_transcribed.csv \
  --temp_dir ./temp/videos
```

### **Optional Flags**

- `--clips_to_transcribe clip1 clip2 clip3` - Only transcribe specific clips, if not provided **(default)** will just try to fetch all videos and transcribe.
- `--use_assembly_ai` - Use **AssemblyAI** (runs on third-party server and you need to provide your **"ASSEMBLYAI_API_KEY"** in the **"./env"** file) instead of Whisper (runs on your machine) for transcription.

**Example:**

```bash
python -m src.main \
  --dataset_filepath ./data/viclaim.csv \
  --output_filepath ./temp/dataset/viclaim_transcribed.csv \
  --temp_dir ./temp/videos \
  --clips_to_transcribe qDhk2_p6x90 8dpibof70wo FjjdWORpFK8 \
  --use_assembly_ai
```

## **Debugging / Running in VS Code**

If you use **VS Code**, you can configure `.vscode/launch.json` for easier debugging.  
Below is the equivalent config rewritten as a **bash script**:

```bash
python -m src.main \
  --dataset_filepath "${PWD}/data/viclaim.csv" \
  --output_filepath "${PWD}/temp/dataset/viclaim_transcribed.csv" \
  --temp_dir "${PWD}/temp/videos"
# Uncomment to limit to specific clips:
# --clips_to_transcribe qDhk2_p6x90 8dpibof70wo FjjdWORpFK8
# Uncomment to enable AssemblyAI:
# --use_assembly_ai
```

---

## **Intended Use**

This repository and the **viclaim_stt** project are provided **for research and educational purposes only**.  
The code and dataset are designed to support:

- Reproducing the sentence-level transcriptions for the **ViClaim** dataset
- Research on **claim detection** models
- Advancing methods for **automatic analysis of video content** in academic and scientific contexts

### **Ethical Use**

- **Do NOT** use this project or dataset for **malicious activities**, including but not limited to:

  - Generating or spreading misinformation
  - Harassment or stalking
  - Privacy violations or unauthorized surveillance
  - Any activity prohibited by law

- Always comply with the **terms of service** of any platforms or APIs used (e.g., **YouTube**).
- If you use **AssemblyAI**, **OpenAI Whisper**, or any other transcription service, ensure you follow their usage policies.

### **Disclaimer**

The authors and contributors of this repository **assume no responsibility** for any misuse of the code, dataset, or derived outputs.  
By using this repository, you agree to:

- Use the data and code **responsibly**
- Respect applicable laws and ethical guidelines
- Acknowledge the original **ViClaim** paper when publishing derived work

> If you are unsure whether your intended use is ethical or legally compliant, consult your institution’s guidelines or contact the maintainers.
