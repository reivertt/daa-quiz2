class ProgressManager:
    def load_progress(self):
        print("[ProgressManager] load_progress() called")
        return 1
    def save_progress(self, max_level_unlocked):
        print(f"[ProgressManager] save_progress({max_level_unlocked}) called")
        pass
    def reset_progress(self):
        print("[ProgressManager] reset_progress() called")
        pass