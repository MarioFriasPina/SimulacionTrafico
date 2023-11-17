from model import RoombaModel

def avg(list):
    return sum(list) / len(list)

height = 20
width = 20
obstacle = 0.2
trash = 0.1
numRobots = 10
max_steps = 1000

iterations = 1000
fails = 0

steps = []
cleaned = []
moves = []
tiles = []
 
while iterations > 0:
    model = RoombaModel(height, width, obstacle, trash, numRobots, max_steps)

    try:
        ret = model.step()
        while ret is None:
            ret = model.step()

        steps.append(ret.steps)
        cleaned.append(ret.percentageclean)
        moves.append(ret.average_moves)
        tiles.append(ret.average_tiles)
    except:
        fails += 1

    iterations -= 1
    print(iterations)
    
print("{} | {:.2f} | {:.2f}% | {:.2f} | {:.2f} | {}".format(numRobots, avg(steps), avg(cleaned), avg(moves), avg(tiles), fails))
