from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import json

try:
    from .agent import *
except:
    from agent import *

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
        try:
            dataDictionary = json.load(open("static/city_files/mapDictionary.json"))
        except:
            dataDictionary = json.load(open("traffic/static/city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open(file) as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            self.map = Map(self.grid, self.width, self.height)
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
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, 3)
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
        self.link_traffic_lights()

        #Data Collection
        self.staticagents = len(self.schedule.agents)
        self.maxagents = 0

    def step(self):
        '''Advance the model by one step.'''
        self.steps += 1

        self.agents = len(self.schedule.agents) - self.staticagents

        if (self.agents > self.maxagents):
            self.maxagents = self.agents


        if self.steps % 100 == 0:
            print(f"Step: {self.steps}. Number of agents: {self.agents}. Max agents: {self.maxagents}")

        self.crash = self.find_crashes()
        if self.crash:
            self.running = False
            print(f"Number of agents: {self.agents}. Max agents: {self.maxagents}")
            print(f"Two cars crashed in step {self.steps} at position {self.crash}")
            return 1
        
        if self.steps > self.max:
            print(f"Number of agents: {self.agents}. Max agents: {self.maxagents}")
            print("Stopped because of max steps")
            return 1

        self.schedule.step()

        if self.steps % self.numSteps == 1:
            self.add_cars()

    def link_traffic_lights(self):
        """
        Link the traffic lights
        """
        for link in self.traffic_lights:
            #Only calculate once per link
            if len(link.partners) == 0 and len(link.opposites) == 0:
                link.master = True
                for neighbor in self.grid.get_neighbors(link.pos, False, False, 1):
                    if isinstance(neighbor, Traffic_Light):
                        link.partners.append(neighbor)
                        neighbor.partners.append(link)
                for neighbor in self.grid.get_neighbors(link.pos, True, False, 2):
                    if isinstance(neighbor, Traffic_Light) and neighbor not in link.partners:
                        link.opposites.append(neighbor)
                        neighbor.opposites.append(link)

    def find_crashes(self):
        """
        Find if there are any crashes in the board
        """
        keys = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height)]
        for key in keys:
            if len(self.grid.get_neighbors(key, True, True, 0)) > 2:
                return key
        return False

    def add_cars(self):
        """
        Add cars in corners
        """
        for i in [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]:
            car = Car(f"car_{self.steps}_{i[0] * self.width + i[1]}", self, i, self.map)
            #Only place if there are no cars in the corners
            if len(self.grid.get_neighbors(i, True, True, 0)) < 2:
                self.grid.place_agent(car, i)
                self.schedule.add(car)