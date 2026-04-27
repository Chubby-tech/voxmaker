import json
import os

class ProgressTracker:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.progress_file = os.path.join(workspace_dir, "progress.json")
        self.state = self._load()
        
    def _load(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {"chunks_processed": []}
        
    def save(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.state, f, indent=4)
            
    def is_processed(self, chunk_id: str) -> bool:
        return chunk_id in self.state["chunks_processed"]
        
    def mark_processed(self, chunk_id: str):
        if chunk_id not in self.state["chunks_processed"]:
            self.state["chunks_processed"].append(chunk_id)
            self.save()
