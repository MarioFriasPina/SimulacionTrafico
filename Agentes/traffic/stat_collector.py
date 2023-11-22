from model import CityModel

def avg(list):
    return sum(list) / len(list)


max_steps = 10000

steps = []
cleaned = []
moves = []
tiles = []
 
for steps in range(1, 6):
    model = CityModel(steps, max_steps)
    print(f"{steps}:")

    try:
        ret = model.step()
        while ret is None:
            ret = model.step()
    except:
        pass

    