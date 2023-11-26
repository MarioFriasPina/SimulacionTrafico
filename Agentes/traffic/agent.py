from mesa import Agent
try:
    from .myAstar import astar_algo
except:
    from myAstar import astar_algo

class Car(Agent):
    """
    Creates a new random agent.
    Args:
        unique_id: The agent's ID
        model: Model reference for the agent
    """
    def __init__(self, unique_id, model, pos, map):
        super().__init__(unique_id, model)
        self.pos = pos
        self.map = map.map
        self.dest = self.random.choice(map.listDest)
        self.path = astar_algo(self.map, (self.model.grid.width, self.model.grid.height), self.pos, self.dest)
        self.last_pos = None

        #If crash then stop
        #for next_pos in self.model.grid.iter_neighbors(self.pos, True, True, 0):
        #    if isinstance(next_pos, Car) and not next_pos == self:
        #        self.model.crash = self.pos

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """

        if not self.path is None and len(self.path) > 1:
            #Dont move into a position where you will find another car
            for next_pos in self.model.grid.iter_neighbors(self.path[-2], True, True, 0):
                if isinstance(next_pos, Car):
                    return

            self.path.pop()
            self.last_pos = self.pos
            self.model.grid.move_agent(self, self.path[-1])
        else:
            self.path = astar_algo(self.map, (self.model.grid.width, self.model.grid.height), self.pos, self.dest)

    def change_lane(self, pos):
        """
        Determines if the agent can move to a new lane to create more space
        """
        direction = self.map[pos]
        #last_pos = self.map[self.last_pos]
        self.map[pos] = '#'
        #self.map[self.last_pos] = '#'
        self.path = astar_algo(self.map, (self.model.grid.width, self.model.grid.height), self.pos, self.dest)
        self.map[pos] = direction
        #self.map[self.last_pos] = last_pos

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        #Kill self if reached destination
        if (self.pos == self.dest):
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return

        #Dont move if in red light
        for here in self.model.grid.iter_neighbors(self.pos, True, True, 0):
            if isinstance(here, Traffic_Light) and not here.state:
                return

        #Dont move into a position where you will find another car
        for next_pos in self.model.grid.iter_neighbors(self.path[-2], True, True, 0):
            if isinstance(next_pos, Car):
                self.change_lane(next_pos.pos)
                self.move()
                return

        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

        #Direction that the light is pointing towards
        self.direction = None

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

class Map():
    """
    Creates a map filled with the information of the map
    
    Args:
        grid: Grid with other agents
        w, h: Size of the map 
    """
    def __init__(self, grid, w, h):
        self.grid = grid
        self.map = self.create_map(w, h)
        self.listDest = []
    
    def create_map(self, width, height):
        """
        Create a dictionary of specified size full of zeros
        
        Args:
            width, height: Size of the map
        """
        keys = [(x, y) for x in range(width) for y in range(height)]
        values = [' '] * (width * height)
        return {key: value for key, value in zip(keys, values)}
    
    def change_lights(self):
        """
        Change the traffic lights into the correct direction
        """
        keys = self.map.keys()
        for pos in keys:
            if self.map[pos] == 's' or self.map[pos] == 'S':
                #Left
                if (pos[0] + 1, pos[1]) in keys and self.map[(pos[0] + 1, pos[1])] == '<':
                    self.map[pos] = '<'
                #Right
                elif (pos[0] - 1, pos[1]) in keys and self.map[(pos[0] - 1, pos[1])] == '>':
                    self.map[pos] = '>'
                #Up
                elif (pos[0], pos[1] + 1) in keys and self.map[(pos[0], pos[1] + 1)] == 'v':
                    self.map[pos] = 'v'
                #Down
                elif (pos[0], pos[1] - 1) in keys and self.map[(pos[0], pos[1] - 1)] == '^':
                    self.map[pos] = '^'
                for light in self.grid.iter_neighbors(pos, True, True, 0):
                    if isinstance(light, Traffic_Light):
                        light.direction = self.map[pos]