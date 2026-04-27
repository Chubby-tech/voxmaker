import os
import sys
import argparse
import concurrent.futures
from tqdm import tqdm

from core.extractor import extract_text
from core.cleaner import clean_text
from core.chunker import chunk_text
from core.tracker import ProgressTracker
from core.tts_engine import generate_audio
from core.audio_proc import merge_audio_chunks

def process_chunk(chunk_id, chunk_content, output_path, voice, length_scale):
    tqdm.write(f" -> Started processing {chunk_id} (this may take a minute)...")
    try:
        generate_audio(chunk_content, output_path, voice, length_scale)
        tqdm.write(f" <- Finished {chunk_id}!")
        return chunk_id, True
    except Exception as e:
        tqdm.write(f"\nError processing {chunk_id}: {e}")
        return chunk_id, False

def main():
    print(r"""
 __      __         __  __       _             
 \ \    / /        |  \/  |     | |            
  \ \  / /____  __ | \  / | __ _| | _____ _ __ 
   \ \/ / _ \ \/ / | |\/| |/ _` | |/ / _ \ '__|
    \  / (_) >  <  | |  | | (_| |   <  __/ |   
     \/ \___/_/\_\ |_|  |_|\__,_|_|\_\___|_|   
                                               
    Advanced Audiobook Generator - Powered by Piper TTS
=========================================================
    """)
    parser = argparse.ArgumentParser(description="Audiobook Maker")
    parser.add_argument("input_file", nargs='?', help="Path to input text/pdf/docx")
    parser.add_argument("--gender", choices=["male", "female"], help="Quickly select voice gender")
    parser.add_argument("--voice", help="Override with a specific Piper voice model")
    parser.add_argument("--workers", type=int, help="Number of parallel TTS workers")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    args = parser.parse_args()

    # Interactive prompts for missing arguments
    if not args.input_file:
        args.input_file = input("\nEnter the path to your input file (TXT/PDF/DOCX): ").strip()
        # Remove quotes if file was dragged and dropped into terminal
        if (args.input_file.startswith("'") and args.input_file.endswith("'")) or (args.input_file.startswith('"') and args.input_file.endswith('"')):
            args.input_file = args.input_file[1:-1]

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    if not args.voice and not args.gender:
        gender_input = input("Which voice gender would you like? (male/female) [default: female]: ").strip().lower()
        args.gender = "male" if gender_input == "male" else "female"
    elif not args.gender:
        args.gender = "female"
        
    if not args.workers:
        workers_input = input("How many workers for parallel processing? (e.g. 1, 2, 4) [default: 2]: ").strip()
        args.workers = int(workers_input) if workers_input.isdigit() else 2

    # New Interactive Prompts
    add_intro_outro = input("Would you like to generate an Intro and Outro? (yes/no) [default: no]: ").strip().lower() == 'yes'
    bg_music_path = input("Provide path to background music (or press Enter to skip): ").strip()
    if bg_music_path and (bg_music_path.startswith("'") or bg_music_path.startswith('"')):
        bg_music_path = bg_music_path[1:-1]

    if args.voice:
        selected_voice = args.voice
    else:
        selected_voice = "en_US-ryan-medium" if args.gender == "male" else "en_US-lessac-medium"

    input_basename = os.path.basename(args.input_file)
    file_name_only, _ = os.path.splitext(input_basename)

    # Force workspace to always be inside the audio_maker folder
    project_root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(args.workspace):
        base_workspace = os.path.join(project_root, args.workspace)
    else:
        base_workspace = args.workspace
        
    book_workspace = os.path.join(base_workspace, file_name_only)
    
    audio_chunks_dir = os.path.join(book_workspace, "audio_chunks")
    final_audio_dir = os.path.join(base_workspace, "final_audio")
    
    os.makedirs(audio_chunks_dir, exist_ok=True)
    os.makedirs(final_audio_dir, exist_ok=True)
    
    tracker = ProgressTracker(book_workspace)
    
    print(f"Extracting text from {args.input_file}...")
    try:
        raw_text = extract_text(args.input_file)
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)
    
    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)
    
    print("Chunking text and analyzing complexity...")
    chunks = chunk_text(cleaned_text)
    
    # Inject Intro and Outro
    if add_intro_outro:
        intro_chunk = {
            "content": f"Welcome to the audiobook presentation of {file_name_only}.",
            "is_chapter_start": True,
            "length_scale": 1.0
        }
        outro_chunk = {
            "content": f"You have reached the end of {file_name_only}. Thank you for listening.",
            "is_chapter_start": True,
            "length_scale": 1.0
        }
        chunks.insert(0, intro_chunk)
        chunks.append(outro_chunk)
        
    print(f"Generated {len(chunks)} chunks.")
    
    pending_chunks = []
    chunk_paths = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i:04d}"
        if chunk.get("is_chapter_start"):
            chunk_id += "_chapter"
            
        output_path = os.path.join(audio_chunks_dir, f"{chunk_id}.wav")
        chunk_paths.append(output_path)
        
        if not tracker.is_processed(chunk_id):
            pending_chunks.append({
                "id": chunk_id,
                "content": chunk["content"],
                "output_path": output_path,
                "length_scale": chunk.get("length_scale", 1.0)
            })
            
    print(f"Chunks pending processing: {len(pending_chunks)}")
    
    if pending_chunks:
        print(f"Generating audio with {args.workers} workers using voice: {selected_voice}...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(process_chunk, c["id"], c["content"], c["output_path"], selected_voice, c["length_scale"]): c 
                for c in pending_chunks
            }
            
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                chunk_id, success = future.result()
                if success:
                    tracker.mark_processed(chunk_id)
                else:
                    print(f"Failed to process {chunk_id}")

    print("Merging audio chunks...")
    final_output = os.path.join(final_audio_dir, f"{file_name_only}.mp3")
    
    # Check if we have chunks to merge
    valid_paths = [p for p in chunk_paths if os.path.exists(p)]
    if valid_paths:
        try:
            merge_audio_chunks(valid_paths, final_output, bg_music_path if bg_music_path else None)
            print(f"Done! Final audiobook saved to {final_output}")
        except Exception as e:
            print(f"Error merging audio: {e}")
    else:
        print("No valid audio chunks found to merge.")

if __name__ == "__main__":
    main()
