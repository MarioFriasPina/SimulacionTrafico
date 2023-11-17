from mesa.visualization import CanvasGrid, ChartModule, BarChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider

from model import RoombaModel
from miCanvasGrid import MiCanvasGrid

# The colors of the portrayal will depend on the cell's condition.
COLORS = {"RoombaAgent": "#00FF00", "OffRoombaAgent": "#AAAAAA",
          "TrashAgent": "#0000FF", "ObstacleAgent": "#000000",
          "VISITED": "#333333", "NOT_VISITED": "#AAAAAA"}

#Calculate the color depending on the charge
def calculate_color(charge):
    green = 255
    red = 255

    if charge > 50:
        red = int(( (charge - 50) / (100 - 50) ) * (0 - 255) + 255)
    else:
        green = int(( (charge - 0) / (50 - 0) ) * (255 - 0) + 0)
    return ("#{:02X}{:02X}00".format(red, green))

#Returns the minimum value in a list, bigger than 0
def my_min(values):
    min_value = 99
    for each in values:
        if each > 0 and each < min_value:
            min_value = each
    return min_value

# The portrayal is a dictionary that is used by the visualization server to
# generate a visualization of the given agent.
def roomba_simulation(agent):
    if agent is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 1}
    
    if agent.type == "TrashAgent":
        portrayal["Layer"] = 2
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5

    (x, y) = agent.pos
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[agent.type]

    if agent.type == "RoombaAgent":
        portrayal["Color"] = calculate_color(agent.charge)

    return portrayal

def heatmap(agent, x, y):
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0, "x": x, "y": y}
    if agent.map[(x, y)] == 0:
        portrayal["Color"] = "#FFFFFF"
    elif agent.map[(x, y)] == -1:
        portrayal["Color"] = "#000000"
    elif agent.map[(x, y)] == -2:
        portrayal["Color"] = "#AAAAAA"
    elif agent.map[(x, y)] == 100:
        portrayal["Color"] = "#0000FF"
    else:
        portrayal["Color"] = calculate_color(agent.map[(x, y)])
    return portrayal

# The chart will plot the number of dirty spots left
trash_chart = ChartModule(
    [{"Label": "TrashAgent", "Color": "#00FF00"}]
)

# The chart will plot the number of on and off roombas
roomba_chart = ChartModule(
    [{"Label": "RoombaAgent", "Color": "#0000FF"}, {"Label": "OffRoombaAgent", "Color": "#FF0000"}]
)

#The chart that will plot the number of moves by agent
moves = BarChartModule(
    [{"Label":"MovesRealized", "Color":"#FF0000"}], 
    scope="agent", sorting="ascending", sort_by="MovesRealized")

#The chart that will plot the number of tiles cleaned by agent
cleans = BarChartModule(
    [{"Label":"TilesCleaned", "Color":"#0000FF"}], 
    scope="agent", sorting="ascending", sort_by="TilesCleaned")

height = 25
width = 25

model_params = {
    "height": height,
    "width": width,
    "obstacle_density": Slider("Obstacle density", 0.1, 0.01, 1.0, 0.01),
    "trash_density": Slider("Trash density", 0.1, 0.01, 1.0, 0.01),
    "roombas": Slider("Number of Roombas", 1, 1, 10, 1),
    "max_time": Slider("Maximum Steps", 1000, 200, 5000, 100),
}

# The portrayal method will fill each cell with a representation of the agent
# that is in that cell.
canvas_element = CanvasGrid(roomba_simulation, width, height, 500, 500)

#Heatmap con la vista de un roomba
heatmap_canvas = MiCanvasGrid(heatmap, width, height, 500, 500)

# The modular server is a special visualization server that allows multiple
# elements to be displayed simultaneously, and for each of them to be updated
# when the user interacts with them.
server = ModularServer(
    RoombaModel, [canvas_element, heatmap_canvas, trash_chart, roomba_chart, moves, cleans], "Roomba", model_params
)

server.launch()