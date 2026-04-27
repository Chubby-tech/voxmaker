import os
from pydub import AudioSegment

def merge_audio_chunks(chunk_paths: list, output_path: str, bg_music_path: str = None):
    """
    Merges multiple audio files and adds brief silence between them.
    Exports to mp3. Can optionally add background music.
    """
    if not chunk_paths:
        return
        
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=1000) # 1 second silence between chunks
    chapter_silence = AudioSegment.silent(duration=3000) # 3 second silence for chapters
    
    for path in chunk_paths:
        try:
            audio = AudioSegment.from_wav(path)
            # If the filename marks a chapter start, add longer silence
            if "_chapter" in path:
                combined += chapter_silence + audio + silence
            else:
                combined += audio + silence
        except Exception as e:
            print(f"Skipping {path} due to error: {e}")
            
    # Normalize voice volume
    combined = combined.apply_gain(-combined.max_dBFS)
    
    if bg_music_path and os.path.exists(bg_music_path):
        try:
            # Load background music
            if bg_music_path.lower().endswith('.wav'):
                bg_music = AudioSegment.from_wav(bg_music_path)
            elif bg_music_path.lower().endswith('.mp3'):
                bg_music = AudioSegment.from_mp3(bg_music_path)
            else:
                bg_music = AudioSegment.from_file(bg_music_path)
            
            # Loop bg_music to match combined duration
            loops_needed = len(combined) // len(bg_music) + 1
            bg_music_looped = bg_music * loops_needed
            bg_music_looped = bg_music_looped[:len(combined)] # Trim to exact length
            
            # Reduce volume of background music by 20dB
            bg_music_looped = bg_music_looped - 20
            
            # Overlay
            combined = combined.overlay(bg_music_looped)
        except Exception as e:
            print(f"Failed to add background music: {e}")
    
    combined.export(output_path, format="mp3", bitrate="192k")
    return output_path
