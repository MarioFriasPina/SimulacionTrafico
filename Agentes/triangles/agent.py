from mesa import Agent

class TriangleCell(Agent):
    """
        A cell agent.
        
        Attributes:
            x, y: Grid coordinates
            condition: Can be "ON", "OFF", "ON_INACTIVE" or "OFF_INACTIVE"
            unique_id: (x,y) tuple.

            unique_id isn't strictly necessary here, but it's good practice to give one to each agent anyway.
    """

    def __init__(self, pos, model):
        """
        Create a new cell.

        Args:
            pos: The cell's coordinates on the grid.
            model: standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "OFF_INACTIVE"
        self._next_condition = None

    def step(self):
        """
        If the cells neighbors have the required conditions turn it on or off

        First, check the neighbors to the sides and down from itself
        """
        if (self.condition == "ON" or self.condition == "OFF"):
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if (neighbor.pos[1] % self.model.grid.height == self.pos[1] % self.model.grid.height):
                    if (neighbor.pos[0] % self.model.grid.height == (self.pos[0] - 1) % self.model.grid.height):
                        left = neighbor
                    elif (neighbor.pos[0] % self.model.grid.height == (self.pos[0] + 1) % self.model.grid.height):
                        right = neighbor
                elif (neighbor.pos[1] % self.model.grid.height == (self.pos[1] -1) % self.model.grid.height and
                      neighbor.pos[0] % self.model.grid.height == self.pos[0] % self.model.grid.height):
                    down = neighbor
            """
            Check the specified conditions
            """
            try:
                if (left.condition != "ON" and self.condition != 'ON' and right.condition == "ON"):
                    down._next_condition = "ON"
                elif (left.condition != "ON" and self.condition == 'ON' and right.condition == "ON"):
                    down._next_condition = "ON"
                elif (left.condition == "ON" and self.condition != 'ON' and right.condition != "ON"):
                    down._next_condition = "ON"
                elif (left.condition == "ON" and self.condition == 'ON' and right.condition != "ON"):
                    down._next_condition = "ON"
                else:
                    down._next_condition = "OFF"
            except:
                if self.condition == 'ON':
                    self._next_condition = "ON_INACTIVE"
                else:
                    self._next_condition = "OFF_INACTIVE"
                return
            """
            Deactivate it when checked to save checking it again
            """
            if self.condition == 'ON':
                self._next_condition = "ON_INACTIVE"
            else:
                self._next_condition = "OFF_INACTIVE"

    
    def advance(self):
        """
        Advance the model by one step.
        """
        if self._next_condition is not None:
            self.condition = self._next_condition