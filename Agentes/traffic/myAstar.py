import heapq
import random

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0  # Cost from start node to current node
        self.h = 0  # Heuristic (estimated cost from current node to goal)
        self.f = 0  # Total cost: g + h

    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)

    def __lt__(self, other):
        return self.f < other.f

def astar_algo(maze, maze_size, start, end):
    open_set = []
    closed_set = set()

    start_node = Node(None, start)
    goal_node = Node(None, end)

    heapq.heappush(open_set, start_node)

    while open_set:
        current_node = heapq.heappop(open_set)
        closed_set.add(current_node)

        if current_node == goal_node:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path

        for next_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + next_position[0], current_node.position[1] + next_position[1])

            if (node_position[0] < 0 or node_position[0] >= maze_size[0] or node_position[1] < 0 or node_position[1] >= maze_size[1]):
                continue

            #Movement Logic
            #Obstacle
            if (maze[node_position] == '#'):
                continue

            #Dont go to the corners of the grid
            if node_position[0] == 0 and node_position[1] == 0:
                continue
            if node_position[0] == maze_size[0] and node_position[1] == 0:
                continue
            if node_position[0] == 0 and node_position[1] == maze_size[1]:
                continue
            if node_position[0] == maze_size[0] and node_position[1] == maze_size[1]:
                continue

            #Dont go against direction of traffic
            if (maze[node_position] == 'v' and next_position[0] == 0 and next_position[1] == 1):
                continue
            if (maze[node_position] == '^' and next_position[0] == 0 and next_position[1] == -1):
                continue
            if (maze[node_position] == '>' and next_position[0] == -1 and next_position[1] == 0):
                continue
            if (maze[node_position] == '<' and next_position[0] == 1 and next_position[1] == 0):
                continue

            new_node = Node(current_node, node_position)
            if new_node in closed_set:
                continue

            new_node.g = current_node.g + 1
            # Use Manhattan distance for no diagonal movement
            new_node.h = abs(new_node.position[0] - goal_node.position[0]) + abs(new_node.position[1] - goal_node.position[1])
            new_node.f = new_node.g + new_node.h

            if any(node == new_node and new_node.f >= node.f for node in open_set):
                continue

            heapq.heappush(open_set, new_node)

    return None  # No path found