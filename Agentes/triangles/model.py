import mesa
from mesa import Model, DataCollector
from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation 

from agent import TriangleCell

class Triangle(Model):
    """
        Simple Triangle formation model.

        Attributes:
            height, width: Grid size.
            density: What fraction of grid cells have the ON state.
    """

    def __init__(self, height=100, width=100, density=0.65):
        """
        Create a new triangle formation model.
        
        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have the ON state.
        """

        # Set up model objects
        # SimultaneousActivation is a Mesa object that runs all the agents at the same time. 
        # This is necessary in this model because the next state of each cell depends on the current state of all its neighbors -- before they've changed.
        # This activation method requires that all the agents have a step() and an advance() method. 
        # The step() method computes the next state of the agent, and the advance() method sets the state to the new computed state.
        self.schedule = SimultaneousActivation(self)
        self.grid = SingleGrid(height, width, torus=False)

        # A datacollector is a Mesa object for collecting data about the model.
        # We'll use it to count the number of cells in each condition each step.
        self.datacollector = DataCollector(
            {
                "ON": lambda m: self.count_type(m, "ON"),
                "OFF": lambda m: self.count_type(m, "OFF"),
                "OFF_INACTIVE": lambda m: self.count_type(m, "OFF_INACTIVE"),
                "ON_INACTIVE": lambda m: self.count_type(m, "ON_INACTIVE"),
            }
        )

        # Place the states in each cell with Prob = density
        # coord_iter is an iterator that returns positions as well as cell contents.
        for contents, (x, y) in self.grid.coord_iter():
            
            new_tree = TriangleCell((x, y), self)
            # Activate all cells in the first row, and turn on some depending on density
            if y == height - 1:
                new_tree.condition = "OFF"
                if self.random.random() < density:
                    new_tree.condition = "ON"
                
            self.grid.place_agent(new_tree, (x, y))
            self.schedule.add(new_tree)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # Halt if no active cells
        if self.count_type(self, "OFF") == 0:
            self.running = False


    # staticmethod is a Python decorator that makes a method callable without an instance.
    @staticmethod
    def count_type(model, tree_condition):
        """
        Helper method to count cells in a given condition in a given model.
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count