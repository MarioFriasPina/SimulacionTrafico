from mesa import Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from agent import RoombaAgent, TrashAgent, ObstacleAgent

class RoombaResults():
    def __init__(self, steps, percentage, moves, tiles):
        self.steps = steps
        self.percentage = percentage
        self.moves = moves
        self.tiles = tiles

        self.percentageclean = 100 - percentage
        self.average_moves = sum(moves)/ len(moves)
        self.average_tiles = sum(tiles)/ len(tiles)

    def __str__(self):
        return "Steps taken: {}, Percentage Cleaned: {}%, Average Moves per agent: {}, Average Tiles Cleaned per agent: {}".format(self.steps, 100 - self.percentage, sum(self.moves)/ len(self.moves), sum(self.tiles)/ len(self.tiles))

class RoombaModel(Model):

    def __init__(self, height=100, width=100, obstacle_density=0.2, trash_density=0.2, roombas=1, max_time=500):

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.max_time = max_time
        self.numTrash = 0
        self.steps = 0

        self.datacollector = DataCollector(
            model_reporters=
            {
                "TrashAgent": lambda m: self.count_type(m, "TrashAgent"),
                "RoombaAgent": lambda m: self.count_type(m, "RoombaAgent"),
                "OffRoombaAgent": lambda m: self.count_type(m, "OffRoombaAgent"),
            },
            agent_reporters=
            {
                "MovesRealized": lambda a: a.moved if isinstance(a, RoombaAgent) else 0,
                "TilesCleaned": lambda a: a.cleanedTiles if isinstance(a, RoombaAgent) else 0
            }
        )
        #Add one roomba in (0,0) if roombas == 1
        if roombas == 1:
            roomba = RoombaAgent((0, 0), self, unique_id=1000)
            self.grid.place_agent(roomba, (0, 0))
            self.schedule.add(roomba)
        #Add multiple roombas
        else:
            for i in range(roombas):
                pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))

                # Add the agent to a random empty grid cell
                pos = pos_gen(self.grid.width, self.grid.height)

                while (not self.grid.is_cell_empty(pos)):
                    pos = pos_gen(self.grid.width, self.grid.height)
                a = RoombaAgent(pos, self, unique_id=i+1000)
                self.grid.place_agent(a, pos)
                self.schedule.add(a)

        #Add obstacles and trash randomly
        for contents, (x, y) in self.grid.coord_iter():
            #Check if roomba already there
            if not self.grid.is_cell_empty((x, y)):
                pass
            elif self.random.random() < obstacle_density:
                obstacle = ObstacleAgent((x, y), self, unique_id=(x + y * width))
                self.grid.place_agent(obstacle, (x, y))
            elif self.random.random() < trash_density:
                trash = TrashAgent((x, y), self, unique_id=(x + y * width))
                self.grid.place_agent(trash, (x, y))
                self.schedule.add(trash)
                self.numTrash += 1

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.steps += 1
        self.datacollector.collect(self)

        #Halt if reached max time
        if self.schedule.steps >= self.max_time:
            self.running = False

        #Halt if no on agent
        if self.count_type(self, "RoombaAgent") == 0:
            self.running = False
            
        #Halt if no trash left
        #if self.count_type(self, "TrashAgent") == 0:
        #    self.running = False

        if self.running is False:
            percentage = self.count_type(self, "TrashAgent") / self.numTrash * 100
            return RoombaResults(self.steps, percentage, self.count_moves(self), self.count_cleans(self))
        
        return None

    # staticmethod is a Python decorator that makes a method callable without an instance.
    @staticmethod
    def count_type(model, agent_type):
        """
        Helper method to count cells in a given condition in a given model.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.type == agent_type:
                count += 1
        return count
    
    @staticmethod
    def count_moves(model):
        """
        Helper method to count cells in a given condition in a given model.
        """
        list = []
        for agent in model.schedule.agents:
            if isinstance(agent, RoombaAgent):
                list.append(agent.moved)
        return list
    
    @staticmethod
    def count_cleans(model):
        """
        Helper method to count cells in a given condition in a given model.
        """
        list = []
        for agent in model.schedule.agents:
            if isinstance(agent, RoombaAgent):
                list.append(agent.cleanedTiles)
        return list