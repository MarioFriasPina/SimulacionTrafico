from model import CityModel

def avg(list):
    return sum(list) / len(list)


max_steps = 2000
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

    distances = ret[0]
    time_alive = ret[1]

    print(f"Average distance: {avg(distances)}")
    print(f"Average time alive: {avg(time_alive)}")