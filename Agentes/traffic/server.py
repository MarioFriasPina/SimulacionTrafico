from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {}

    if (isinstance(agent, Road)):
        portrayal = {
            "Shape": "arrowHead",
            "Filled": "true",
            "Layer": 0,
            "Color": ["#AAAAAA", "#FFFFFF"],
            "scale": 0.5,
        }
        if agent.direction == 'Up':
            portrayal["heading_y"] = 1
            portrayal["heading_x"] = 0           
        elif agent.direction == 'Down':
            portrayal["heading_y"] = -1
            portrayal["heading_x"] = 0          
        elif agent.direction == 'Left':
            portrayal["heading_x"] = -1
            portrayal["heading_y"] = 0      
        else:
            portrayal["heading_x"] = 1 
            portrayal["heading_y"] = 0
    else:
        portrayal = {"Shape": "rect",
                "Filled": "true",
                "Layer": 1,
                "w": 1,
                "h": 1
                }
    
    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Car)):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5

    return portrayal

width = 0
height = 0
file = 'static/city_files/city2023.txt'

with open(file) as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"file" : file, "N":2}

#print(width, height)
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

server = ModularServer(CityModel, [grid], "Traffic Base", model_params)
                       
server.port = 8521 # The default
server.launch()