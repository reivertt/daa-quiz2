import os
import json

SAVE_FILE = "save_file.json"
DEFAULT_PROGRESS = 1

class ProgressManager:
    def __init__(self, save_file_path=None):
        if save_file_path is None:
            self.save_file_path = SAVE_FILE
        else:
            self.save_file_path = save_file_path
    
    
    def load_progress(self):
        print("[ProgressManager] load_progress() called")
        try:
            with open(self.save_file_path, 'r') as fp:
                data = json.load(fp)
                max_level = data.get('max_level_unlocked', DEFAULT_PROGRESS)
                print(f"[ProgressManager] Progress loaded: Max level unlocked = {max_level}")
                return max_level
        except FileNotFoundError:
            print(f"[ProgressManager] Save file {self.save_file_path} not found, returning default progress.")
            max_level = DEFAULT_PROGRESS
            return max_level        
    
    def save_progress(self, max_level_unlocked):
        print(f"[ProgressManager] save_progress({max_level_unlocked}) called")
        data_to_save = {
            'max_level_unlocked': max_level_unlocked
        }
        try:
            with open(self.save_file_path, 'w') as fp:
                json.dump(data_to_save, fp)
            print(f"[ProgressManager] Progress saved to {self.save_file_path}")
        except Exception as e:
            print(f"[ProgressManager] Error saving progress: {e}")
        

    def reset_progress(self, deletion=False):
        print("[ProgressManager] reset_progress() called")
        if deletion:
            try:
                os.remove(self.save_file_path)
                print(f"[ProgressManager] Save file {self.save_file_path} deleted.")
            except FileNotFoundError:
                print(f"[ProgressManager] Save file {self.save_file_path} not found, nothing to delete.")
        else: 
            self.save_progress(DEFAULT_PROGRESS)

# Example usage (for testing this module independently)
if __name__ == "__main__":
    pm = ProgressManager("test_save_file.json")

    current_max_level = pm.load_progress()
    print(f"   Currently, max level unlocked is: {current_max_level}")

    print("saving progress: 5")
    new_unlocked_level = 5
    pm.save_progress(new_unlocked_level)

    current_max_level = pm.load_progress()
    print(f"   After saving, max level unlocked is: {current_max_level}")

    print("resetting progress:")
    pm.reset_progress()

    print("loading after reset:")
    current_max_level = pm.load_progress()
    print(f"   After reset, max level unlocked is: {current_max_level}")

    pm.reset_progress(True)