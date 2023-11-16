from mesa import Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation 

from agent import RoombaAgent, TrashAgent, ObstacleAgent

class RoombaModel(Model):

    def __init__(self, height=100, width=100, obstacle_density=0.2, trash_density=0.2, roombas=1, max_time=500):

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.max_time = max_time

        self.datacollector = DataCollector(
            {
                "TrashAgent": lambda m: self.count_type(m, "TrashAgent"),
                "RoombaAgent": lambda m: self.count_type(m, "RoombaAgent"),
                "OffRoombaAgent": lambda m: self.count_type(m, "OffRoombaAgent"),
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

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
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