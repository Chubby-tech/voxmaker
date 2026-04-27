# VoxMaker (Advanced Audiobook Generator)

VoxMaker is a powerful, fully-local, command-line application that automatically converts any text document (PDF, DOCX, or TXT) into a highly polished, professional-grade audiobook MP3. 

It leverages the local, high-quality **Piper TTS** engine, meaning it requires no internet connection or paid cloud APIs to generate lifelike voices.

## Features

- **Multi-Format Support:** Automatically reads `.txt`, `.pdf`, and `.docx` files.
- **Intelligent Cleaning:** Strips rogue page numbers, weird formatting symbols, and fixes broken sentences spanning multiple lines.
- **NLP Chunking & Chapter Detection:** Uses `NLTK` to split large books without breaking sentences, and detects chapters to inject cinematic 3-second silences.
- **Dynamic Pacing:** Uses `textstat` to analyze the complexity of paragraphs. It reads complex paragraphs slower to allow for absorption, and conversational text slightly faster.
- **Background Music Mixing:** Optionally provide a music file. The script will automatically loop it, lower its volume by 20dB, and overlay it underneath the narration.
- **Crash Recovery:** Safely track progress. If you close the terminal or lose power, running the tool again will instantly resume exactly where it left off.
- **Multi-Threaded:** Utilize your multi-core CPU to process chunks simultaneously.

---

## Prerequisites

Before installing VoxMaker, you must ensure you have two things installed on your system:
1. **Python 3.8+** (We recommend Python 3.10 or newer)
2. **FFmpeg** (Required for audio merging and background music)

### Installing FFmpeg

**Windows:**
Open Command Prompt or PowerShell as Administrator and run:
```powershell
winget install ffmpeg
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install ffmpeg
```

**Mac (macOS):**
Using [Homebrew](https://brew.sh/):
```bash
brew install ffmpeg
```

---

## Installation

1. Clone or download this project folder (`audio_maker`) to your local machine.
2. Open your terminal or command prompt and navigate to the project folder:
   ```bash
   cd path/to/audio_maker
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: If you are using Python 3.13 or 3.14, the `audioop-lts` package inside the requirements is strictly necessary to prevent audio processing errors).*

---

## Usage

You can run the application directly by passing your text, PDF, or Word document into the main script.

### Basic Run
```bash
python main.py /path/to/your/book.pdf
```

### Interactive Prompts
VoxMaker is designed to be interactive. If you simply run:
```bash
voxmaker
```
*(Or `python main.py`)*
The application will guide you through:
1. Providing the file path.
2. Selecting a **Male** or **Female** voice.
3. Choosing how many CPU **Workers** you want to use (e.g., `2` or `4` for faster generation).
4. Asking if you want an automated **Intro & Outro** spoken for your book.
5. Asking for an optional **Background Music** file path.

*Note: The very first time you generate audio, it will take a minute or two to automatically download the high-quality AI voice models from the internet. Subsequent runs will use the cached local models.*

### Where are my files?
All generated audiobooks will be saved inside the `audio_maker/workspace/final_audio/` directory.

### Getting Help
If you ever forget what options are available, or just want to start the interactive prompts, you can simply type:
```bash
voxmaker
```
To pull up the built-in manual, type:
```bash
voxmaker --help
```
*(Or use `python main.py` / `python main.py --help` if you haven't set up the global command).*

---

## Making it a Global Command (Linux/Mac)

If you want to be able to run this tool from anywhere on your computer without typing `python path/to/main.py`, you can create a global script!

1. Create a script named `voxmaker` in your local bin directory:
   ```bash
   nano ~/.local/bin/voxmaker
   ```
2. Paste the following into the file (make sure to replace `/path/to/` with the actual path where you saved this project):
   ```bash
   #!/bin/bash
   python3 /path/to/audio_maker/main.py "$@"
   ```
3. Make it executable:
   ```bash
   chmod +x ~/.local/bin/voxmaker
   ```
4. Now, you can run `voxmaker my_book.pdf` from any directory on your computer!
