import heapq

class Node:
    def __init__(self, position, parent=None):
        self.position = position  # (x, y) tuple
        self.parent = parent

        self.g = 0  # cost from start to node
        self.h = 0  # heuristic cost
        self.f = 0  # g + h

    def __lt__(self, other):
        # priority queue comparator via total cost
        return self.f < other.f

    def __eq__(self, other):
        # comparator to check if same position
        return isinstance(other, Node) and self.position == other.position

    def __hash__(self):
        return hash(self.position)

class HintProvider:
    def _heuristic(self, current_pos, end_pos):
        # calculates manhattan distance
        return abs(current_pos[0] - end_pos[0]) + abs(current_pos[1] - end_pos[1])

    def _reconstruct_path(self, end_node):
        # reverses path found to get from start to end node
        path = []
        current = end_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1] 

    def get_path(self, map_data, start_coords, end_coords):
        if not map_data or not map_data[0]:
            print("[HintProvider A*] Error: Map data is empty.")
            return []

        rows = len(map_data)
        cols = len(map_data[0])

        if not (0 <= start_coords[0] < cols and 0 <= start_coords[1] < rows):
            print(f"[HintProvider A*] Error: Start coordinates {start_coords} out of bounds.")
            return []
        if map_data[start_coords[1]][start_coords[0]] == '#':
            print(f"[HintProvider A*] Error: Start coordinates {start_coords} are on a wall.")
            return []

        if not (0 <= end_coords[0] < cols and 0 <= end_coords[1] < rows):
            print(f"[HintProvider A*] Error: End coordinates {end_coords} out of bounds.")
            return []
        if map_data[end_coords[1]][end_coords[0]] == '#':
            print(f"[HintProvider A*] Error: End coordinates {end_coords} are on a wall.")
            return []
            
        if start_coords == end_coords:
            return [start_coords]

        start_node = Node(start_coords)
        end_node = Node(end_coords)

        # nodes that hasnt been visited
        open_set_heap = [] 
        heapq.heappush(open_set_heap, start_node)
        open_set_dict = {start_node.position: start_node.g}

        # nodes that has been visited
        closed_set = set()

        movements = [(0, -1), (0, 1), (-1, 0), (1, 0)] # (dx, dy)

        # main loop
        while open_set_heap:
            current_node = heapq.heappop(open_set_heap)

            if current_node.position in closed_set:
                continue
            
            if current_node.position in open_set_dict and current_node.g > open_set_dict[current_node.position]:
                continue

            if current_node.position in open_set_dict: 
                del open_set_dict[current_node.position]
            closed_set.add(current_node.position)

            if current_node == end_node:
                return self._reconstruct_path(current_node)

            for dx, dy in movements:
                neighbor_pos = (current_node.position[0] + dx, current_node.position[1] + dy)

                if not (0 <= neighbor_pos[0] < cols and 0 <= neighbor_pos[1] < rows):
                    continue

                if map_data[neighbor_pos[1]][neighbor_pos[0]] == '#':
                    continue

                if neighbor_pos in closed_set:
                    continue
                
                tentative_g_cost = current_node.g + 1

                # If neighbor is not in open_set_dict or this path is better
                if neighbor_pos not in open_set_dict or tentative_g_cost < open_set_dict[neighbor_pos]:
                    neighbor_node = Node(neighbor_pos, current_node)
                    neighbor_node.g = tentative_g_cost
                    neighbor_node.h = self._heuristic(neighbor_node.position, end_node.position)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    
                    heapq.heappush(open_set_heap, neighbor_node)
                    open_set_dict[neighbor_pos] = neighbor_node.g

        print(f"[HintProvider A*] No path found from {start_coords} to {end_coords}.")
        return [] # No path found

if __name__ == "__main__":
    hp = HintProvider()

    test_map = [
        ["S", ".", ".", ".", "."],
        [".", "#", "#", "#", "."],
        [".", ".", ".", "E", "."],
        ["#", "#", ".", "#", "#"],
        [".", ".", ".", ".", "."]
    ]
    start = (0, 0) 
    end = (3, 2)   

    print(f"Finding path from {start} to {end} in map:")
    for row in test_map:
        print("".join(row))
    
    path = hp.get_path(test_map, start, end)
    print(path if path else "No path found.")
    
    false_test_map = [
        ["S", ".", "#", "E"],
        [".", ".", "#", "."]
    ]
    false_start = (0,0)
    false_end = (3,0)
    path = hp.get_path(false_test_map, false_start, false_end)
    print(path if path else "No path found.")