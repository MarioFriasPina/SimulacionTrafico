# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git 

from flask import Flask, request, jsonify
from traffic.model import CityModel
from traffic.agent import Car, Traffic_Light

import requests
import json

# Size of the board:
number_agents = 10
width = 28
height = 28
myModel = None
currentStep = 0

app = Flask("Traffic example")

@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, myModel, number_agents, width, height

    if request.method == 'POST':
        file = request.form.get('file')
        delay = int(request.form.get('delay'))
        currentStep = 0

        #print(request.form)
        #print(number_agents, width, height)
        myModel = CityModel(file, delay)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global myModel

    if request.method == 'GET':
        agentPositions = [{"id": str(a[-1].unique_id), "x": x, "y":1, "z":z, "state": str(a[-1].state)} for a, (x, z) in myModel.grid.coord_iter() if isinstance(a[-1], Car)]

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global myModel

    if request.method == 'GET':
        carPositions = [{"id": str(a[0].direction) + str(a[0].unique_id), "x": x, "y":-1, "z":z, "state": str(a[0].state)} for a, (x, z) in myModel.grid.coord_iter() if isinstance(a[0], Traffic_Light)]

        return jsonify({'positions':carPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, myModel
    if request.method == 'GET':
        myModel.step()
        currentStep += 1

        print(f"Step: {currentStep}. Number of agents: {myModel.agents}. Max agents: {myModel.maxagents}")

        #Call the validation server
        """
        if currentStep < 1005 and currentStep % 100 == 0:
            url = "http://52.1.3.19:8585/api/"
            endpoint = "attempts"
            data = {"year" : 2023, "classroom" : 301, "name" : "Equipo 8- Mario y Shaul", "num_cars": len(myModel.distances)}
            headers = {"Content-Type": "application/json"}

            response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)

            print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
            print("Response:", response.json())
        """

        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=False)