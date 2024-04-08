# Auto-Random-Maze-Generator-and-Solver
Pseudorandom (deterministric, i.e., maze will  always start and end at the same two points) maze generator + solver. To solve the maze, currently it just brute force's the maze pretty much. However the end goal of this project is to implement the A* pathfinding algorithm successfully. 

TODO:
- Docs
- Add A* (fix beta vs)
- Optimize/speed improve maze drawing/generation.
- Refactor a lotta shit. All of it to be more specific...
  - Im lazy + works for me so...
    - Too ez

## Usage
```bash
python3 maze.py
```

###### Requirements
- `tkinter`
- `random`
- `time`
- `threading`

###### Mazes being drawn at random 
![image](https://github.com/supaaasuge/Auto-Random-Maze-Generator-and-Solver/assets/158092262/28b9a7a6-b4a0-447f-b95b-ea697c522e1a)


![image](https://github.com/supaaasuge/Auto-Random-Maze-Generator-and-Solver/assets/158092262/025f26b0-0e13-4593-8759-548e57eebe68)

##### Maze's being solved
![image](https://github.com/supaaasuge/Auto-Random-Maze-Generator-and-Solver/assets/158092262/a50370b0-da35-4af7-8f86-2b298297aa32)
- Note red dots are for path's it's determined as incorrect/dead-ends.
- Blue notes are progess... basically.
  - As you can see it isn't efficient by any means. At the moment, this version just brute forces the maze...  
