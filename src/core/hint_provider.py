class HintProvider:
    def get_path(self, map_data, start_coords, end_coords):
        print(f"[HintProvider] get_path called from {start_coords} to {end_coords}")
        return []