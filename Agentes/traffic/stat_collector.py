from model import CityModel

import requests
import json

def avg(list):
    return sum(list) / len(list)


def send_info(reached_cars):
    #Call the validation server
    url = "http://52.1.3.19:8585/api/"
    endpoint = "attempts"
    data = {"year" : 2023, "classroom" : 301, "name" : "Equipo 8- Mario y Shaul", "num_cars": reached_cars}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)

    print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
    print("Response:", response.json())

max_steps = 1000
current_step = 0
file = 'static/city_files/city2023.txt'

#for tries in range(1, 100):
steps = 2
model = CityModel(file, steps, max_steps)
print(f"{steps}:")

try:
    ret = model.step()
    while ret is None:
        current_step += 1
        ret = model.step()
except:
    print("Error")
    pass

distances = ret[0]
time_alive = ret[1]

#send_info(len(distances))

print(f"Agents that reached: {len(distances)}")
print(f"Average distance: {avg(distances)}")
print(f"Average time alive: {avg(time_alive)}")