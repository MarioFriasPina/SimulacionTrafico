from mesa.visualization import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider

from model import Triangle

# The colors of the portrayal will depend on the cell's condition.
COLORS = {"ON": "#0000FF", "ON_INACTIVE": "#FF0000", "OFF": "#FFFFFF", "OFF_INACTIVE": "#AAAAAA"}

# The portrayal is a dictionary that is used by the visualization server to
# generate a visualization of the given agent.
def forest_fire_portrayal(tree):
    if tree is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = tree.pos
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[tree.condition]

    return portrayal

# The canvas element will be 500x500 pixels, with each cell being 10x10 pixels.
# The portrayal method will fill each cell with a representation of the agent
# that is in that cell.
canvas_element = CanvasGrid(forest_fire_portrayal, 50, 50, 500, 500)

# The chart will plot the number of each type of cell over time.
tree_chart = ChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

# The pie chart will plot the number of each type of cell at the current step.
pie_chart = PieChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

# The model parameters will be set by sliders controlling the initial density
model_params = {
    "height": 50,
    "width": 50,
    "density": Slider("Tree density", 0.2, 0.01, 1.0, 0.01),
}

# The modular server is a special visualization server that allows multiple
# elements to be displayed simultaneously, and for each of them to be updated
# when the user interacts with them.
server = ModularServer(
    Triangle, [canvas_element, tree_chart, pie_chart], "Triangle", model_params
)

server.launch()