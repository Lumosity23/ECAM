# Creation de class

class Erion:

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def hello(self, msg: str) -> None:
        print(msg)


ma_variable = Erion(10, 3) # execute __init__ et renoie l'objet Erion
yo_yo = Erion(2, 2)


#print(yo_yo.y)
#t = Erion(2,2).hello("Salut Erion")
#print(t)

radius = int(input())
directions = [(x,y) for y in range(-radius, radius) for x in range(-radius, radius + 1)]
print(directions)

assert len(directions) == (radius*2 + 1)**2, f"Must be : {(radius*2 + 1)**2}, but is : {len(directions)}"