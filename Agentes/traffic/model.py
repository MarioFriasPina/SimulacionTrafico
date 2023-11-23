from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            file: File for the city map
            N: Number of steps before new arrivals
            max: Number of steps before stopping simulation
    """

    def __init__(self, file, N = 4, max = 10000):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("C:/Users/shaul/OneDrive/Desktop/Tec5/agentes/SimulacionTrafico/Agentes/traffic/city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open(file) as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            self.map = Map(self.width, self.height)
            self.steps = 0
            self.crash = False

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    #Add position to map given to cars
                    self.map.map[(c, self.height - r - 1)] = col
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.map.listDest.append((c, self.height - r - 1))


        self.numSteps = N
        self.max = max
        self.running = True
        self.map.change_lights()

        #Data Collection
        self.staticagents = len(self.schedule.agents)
        self.maxagents = 0

    def step(self):
        '''Advance the model by one step.'''
        self.steps += 1

        if self.steps % self.numSteps == 1:
            self.add_cars()

        self.agents = len(self.schedule.agents) - self.staticagents

        if (self.agents > self.maxagents):
            self.maxagents = self.agents

        print(f"Number of agents: {self.agents}. Max agents: {self.maxagents}")

        if self.crash:
            self.running = False
            print(f"Two cars crashed in step {self.steps} at position {self.crash}")
            return 1
        
        if self.steps > self.max:
            print("Stopped because of max steps")
            return 1

        self.schedule.step()


    def add_cars(self):
        """
        Add cars in corners
        """
        for i in [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]:
            car = Car(f"car_{self.steps}_{i[0] * self.width + i[1]}", self, i, self.map)
            self.grid.place_agent(car, i)
            self.schedule.add(car)