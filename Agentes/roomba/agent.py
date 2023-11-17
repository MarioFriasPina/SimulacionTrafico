from mesa import Agent
from myAstar import astar_algo

#Check if position is a valid move
def check_obstacles(grid, position, visited):
    #Check out of bounds
    if (grid.out_of_bounds(position)):
        return False

    for here in grid.iter_neighbors(position, True, True, 0):
            if here.type == "ObstacleAgent" or here.type == "OffRoombaAgent":
                visited[position] = -1
                return False       
            if (here.type == 'RoombaAgent'):
                return False
    return True

#Checks if the specified position is a valid move when exploring
def check_collision_exploration(grid, position, visited):
    #Check out of bounds
    if (grid.out_of_bounds(position)):
        return False
    #Check if position is invalid
    if (not visited[position] == 0):
        return False

    #Check obstacles
    return check_obstacles(grid, position, visited)

#Returns the biggest value in map from position
def find_biggest_valid(pos, map, map_size):
    best = 0
    next = (0,0)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for move in moves:
        new = (pos[0] + move[0], pos[1] + move[1])
        if 0 <= new[0] < map_size[0] and 0 <= new[1] < map_size[1]:
            if (map[new] > best):
                best = map[new]
                next = new
    return next


#Returns the closest empty space from a position
def find_closest_empty(pos, known, grid):
    distance = 100000000000000
    position = (-1, -1)

    for key in known.keys():
        # Do something with key and value
        if (grid.out_of_bounds(key)):
            pass
        elif known[key] == 0 and ((key[0] - pos[0]) ** 2) + ((key[1] - pos[1]) ** 2) < distance:
            distance = ((key[0] - pos[0]) ** 2) + ((key[1] - pos[1]) ** 2)
            position = key
    return position

#Merges two maps from two agents keeping the not-zeros
def merge_maps(map1, map2, width, height):
    keys = [(x, y) for x in range(width) for y in range(height)]
    for key in keys:
        if (map1[key] == 0 and map2[key] != 0):
            map1[key] = map2[key]
    return map1

#Changes the charge of the agent when it does a costly action
def do_action(self):
    self.charge -= 1
    if self.charge < 0:
        self.charge = 0

#Create a dictionary of specified size full of zeros
def create_dictionary(width, height):
    keys = [(x, y) for x in range(width) for y in range(height)]
    values = [0] * (width * height)
    return {key: value for key, value in zip(keys, values)}

#Find all invalid positions from current position
def find_all_invalid(map, position, visited, map_size):

    stack = [position]
    #found_pos = (-1, -1)

    while stack:
        pos = stack.pop()
        visited[pos] = 1

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for move in moves:
            new = (pos[0] + move[0], pos[1] + move[1])
            #Inbound and not visited
            if 0 <= new[0] < map_size[0] and 0 <= new[1] < map_size[1] and visited[new] == 0:
                #If wall dont append, but visit
                if map[new] == -1:
                    visited[new] = 1
                elif map[new] == 0:
                    return new
                else:
                    stack.append(new)

    #check_position(map, position, visited, map_size)

    #Change unreachable squares to -1
    keys = [(x, y) for x in range(map_size[0]) for y in range(map_size[1])]
    for key in keys:
        if (map[key] == 0 and visited[key] == 0):
            map[key] = -2
    return (-1, -1)

class RoombaAgent(Agent):

    def __init__(self, pos, model, unique_id):
        super().__init__(pos, model)
        self.original_pos = pos
        self.pos = pos
        self.next_pos = None
        self.type = "RoombaAgent"
        self.unique_id = unique_id

        #Heat map with the values to reach each position, with a 100 in a charging station
        #0 is unexplored
        #-1 is obstacle
        #100 - Num is the distance from a charging station
        self.map = create_dictionary(self.model.grid.width, self.model.grid.height)
        self.map[pos] = 100

        #List of the order in which the roomba reached its current tile
        self.journey = [pos]

        #List of the order to move to a found position
        self.path = []

        #Position to go to when dont know where to go
        self.far = self.pos
        #Knows if no new positions are posible
        self.end = False

        #Number of turns stuck
        self.stuck = 0

        #Robots battery
        self.go_charge = False
        self.charge = 100

            #Stats that may be important
        #How many tiles this specific robot cleaned
        self.cleanedTiles = 0
        #How many tiles this specific robot moved
        self.moved = 0

    def step(self):
        if self.type == "OffRoombaAgent":
            return
        
        if self.charge <= 0 or (self.end is True and self.pos == self.original_pos):
            self.type = "OffRoombaAgent"
            self.map[self.pos] = -1
            return

        #If you are at home with less than 100% battery charge
        if self.charge < 100 and self.map[self.pos] == 100:
            self.charge += 5
            if len(self.journey) > 1:
                self.journey = [self.pos]
            if (self.charge >= 100):
                self.charge = 100
                self.go_charge = False
            return

        #Clean trash if inside
        for here in self.model.grid.iter_neighbors(self.pos, True, True, 0):
            if (here.type == 'TrashAgent'):
                here._clean = True
                self.model.grid.remove_agent(here)
                do_action(self)
                self.cleanedTiles += 1
                return

        next_moves = []
        #Add to possible moves if valid
        if (check_collision_exploration(self.model.grid, (self.pos[0] + 0, self.pos[1] - 1), self.map)):
            next_moves.append((self.pos[0], self.pos[1] - 1))
        if (check_collision_exploration(self.model.grid, (self.pos[0] + 1, self.pos[1] + 0), self.map)):
            next_moves.append((self.pos[0] + 1, self.pos[1]))
        if (check_collision_exploration(self.model.grid, (self.pos[0] - 1, self.pos[1] + 0), self.map)):
            next_moves.append((self.pos[0] - 1, self.pos[1]))
        if (check_collision_exploration(self.model.grid, (self.pos[0] + 0, self.pos[1] + 1), self.map)):
            next_moves.append((self.pos[0], self.pos[1] + 1))

        #If you're low on charge go to closest charging station
        if self.charge <= 110 - self.map[self.pos]:
            #Try to fill all the unreachable spaces with -1
            find_all_invalid(self.map, self.pos, create_dictionary(self.model.grid.width, self.model.grid.height), (self.model.grid.width, self.model.grid.height))
            #Find a path to original position
            self.path = astar_algo(self.map, (self.model.grid.width, self.model.grid.height), self.pos, self.original_pos)
            self.go_charge = True

        #Go through known path
        if not self.path is None and len(self.path) > 1 and check_obstacles(self.model.grid, self.path[-2], self.map):
                self.path.pop()
                self.next_pos = self.path[-1]
                self.journey.append(self.next_pos)
                if self.map[self.next_pos] == 0:
                    self.map[self.next_pos] = self.map[self.pos] - 1
        #If you have a possible movement, choose one
        elif len(next_moves) > 0:
            next_move = self.random.choice(next_moves)
            self.next_pos = (next_move)
            self.journey.append(self.next_pos)
            if self.map[self.next_pos] == 0:
                self.map[self.next_pos] = self.map[self.pos] - 1
        #If you cannot move from your current position go to your last position
        elif not self.journey is None and len(self.journey) > 1 and check_obstacles(self.model.grid, self.journey[-2], self.map):
            self.journey.pop()
            self.next_pos = self.journey[-1]
        #If no adjecent or reachable spots find new one
        else:
            #Try to fill all the unreachable spaces with -1
            self.far = find_all_invalid(self.map, self.pos, create_dictionary(self.model.grid.width, self.model.grid.height), (self.model.grid.width, self.model.grid.height))

            self.next_pos = None
            self.path = None
            while self.path is None and not self.end:
                if self.go_charge is True:
                    self.far = self.original_pos
                elif self.far == (-1, -1):
                    self.far = self.original_pos
                    self.end = True
                
                self.path = astar_algo(self.map, (self.model.grid.width, self.model.grid.height), self.pos, self.far)
                if self.path is None:
                    self.map[self.far] = -1

        #Communication
        for here in self.model.grid.iter_neighbors(self.pos, True, True, 2):
            if here.type == 'RoombaAgent' or here.type == 'OffRoombaAgent':
                #Send and recieve visited tiles with other roomba
                map = merge_maps(self.map, here.map, self.model.grid.width, self.model.grid.height)
                self.map = map
                here.map = map
            if here.type == 'ObstacleAgent' or here.type == 'OffRoombaAgent':
                #See up to 2 tiles away
                self.map[here.pos] = -1

        if self.next_pos is not None:
            self.model.grid.move_agent(self, self.next_pos)
            self.stuck = 0
            do_action(self)
            self.next_pos = None
            self.moved += 1
        else:
            self.stuck += 1
            #Got stuck for 5 turns
            if (self.stuck > 5):
                next_moves = []
                #Find empty position and move to it
                for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    node_position = (self.pos[0] + new_position[0], self.pos[1] + new_position[1])
                    if check_obstacles(self.model.grid, node_position, self.map):
                        next_moves.append(node_position)
                self.model.grid.move_agent(self, self.random.choice(next_moves))
                self.stuck = 0
                do_action(self)
                self.moved += 1
                self.next_pos = None

class ObstacleAgent(Agent):
    def __init__(self, pos, model, unique_id):
        super().__init__(pos, model)
        self.pos = pos
        self.type = "ObstacleAgent"

class TrashAgent(Agent):
    def __init__(self, pos, model, unique_id):
        super().__init__(pos, model)
        self.pos = pos
        self.type = "TrashAgent"
        self._clean = False
    
    def step(self):
        if self._clean is not False:
            self.type = "CleanAgent"