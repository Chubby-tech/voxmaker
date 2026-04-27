import os
import subprocess

def generate_audio(text: str, output_path: str, voice: str = "en_US-lessac-medium", length_scale: float = 1.0):
    """
    Uses Piper TTS to generate audio.
    """
    # Ensure model is downloaded in the project's root folder, regardless of where script is run
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(project_root, "models")
    model_path = os.path.join(model_dir, f"{voice}.onnx")
    
    if not os.path.exists(model_path):
        os.makedirs(model_dir, exist_ok=True)
        print(f"\nDownloading Piper voice model '{voice}' (only happens once)...")
        subprocess.run(["python3", "-m", "piper.download_voices", voice, "--download-dir", model_dir], check=True)
    
    # Piper TTS command.
    cmd = [
        "piper",
        "--model", model_path,
        "--output_file", output_path,
        "--length_scale", str(length_scale)
    ]
    
    # We pipe the text to it
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=text.encode('utf-8'))
    
    if process.returncode != 0:
        raise RuntimeError(f"TTS Failed: {stderr.decode()}")
        
    return output_path
