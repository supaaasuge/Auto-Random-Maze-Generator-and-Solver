# Auto-Random-Maze-Generator-and-Solver

Pseudorandom maze generator + solver. Start & End points always remain the same. To solve the maze, the A* pathfinding algorithm is used.
Once solved, total number of moves and time lapsed will be printed to the terminal, and the fastest posasible path from start to finish will be drawn.

## Usage

```bash
python3 maze.py
```


### Implementation of A* Pathfinding Algorithm

A* algorithm is a widely used pathfinding and graph traversal algorithm that efficiently finds the shortest path from a start node to a goal node. It combines Dijkstra's algorithm and greedy Best-First-Search by using a heuristic to guide its search.

1. __Initialization__:
- The start cell (0, 0) is initialized with g = 0 and f = heuristic(start, goal).
- An open set (priority queue) is initialized with the start cell.
2. __Heuristic Function__:
- The heuristic function used here is the Manhattan distance, calculated as `abs(cell._x1 - goal._x1) + abs(cell._y1 - goal._y1)`.
3. __Main Loop__:
- Algorithm processes cells from the open set until it's empty or the goal is reached.
- For the current cell, its neighbors are evaluated.
- For each neighbor, the tentative cost `g` is calculated as `current+1`.
- If the tentative cost is lower than the neighbor's current cost, the neighbor's cost is updated, and it's added to the open set.
4. __Path Reconstruction__
- Once the goal cell is reach, the path is reconstructed by tracing back from the goal to the start using the `came_from` dictionary.
