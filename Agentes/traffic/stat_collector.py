from model import CityModel

def avg(list):
    return sum(list) / len(list)


max_steps = 10000

steps = []
cleaned = []
moves = []
tiles = []
file = 'static/city_files/city2023.txt'
 
for steps in range(2, 6):
    model = CityModel(file, steps, max_steps)
    print(f"{steps}:")

    try:
        ret = model.step()
        while ret is None:
            ret = model.step()
    except:
        pass

    