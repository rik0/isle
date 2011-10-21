import itertools
import random
import copy
import sys
import pickle

def random_plant(left, top, width, height):
    pos_x = random.randint(left, left+width-1)
    pos_y = random.randint(top, top+height-1)
    PLANTS.add((pos_x, pos_y))

def add_plants():
    random_plant(*JUNGLE)
    random_plant(*BOARD)

def angle(genes, index, x):
    xnu = x - genes[index]
    if xnu < 0:
        return 0
    else:
        return 1 + angle(genes, index+1, xnu)

class Animal(object):
    def __init__(self, x, y, energy, dir, genes):
        self.x = x
        self.y = y
        self.energy = energy
        self.dir = dir
        self.genes = genes

    def move(self):
        if 2 <= self.dir < 5:
            self.x += 1
        elif self.dir not in (1, 5):
            self.x -= 1
        if 0 <= self.dir < 3:
            self.y -= 1
        elif 4 <= self.dir < 7:
            self.y += 1
        self.x %= WIDTH
        self.y %= HEIGHT
        self.energy -= 1

    def turn(self):
        x = random.randint(0, sum(self.genes)-1)
        self.dir += angle(self.genes, 0, x)
        self.dir %= 8

    def eat(self):
        if (self.x, self.y) in PLANTS:
            self.energy += PLANT_ENERGY
            PLANTS.remove((self.x, self.y))

    def reproduce(self):
        if self.energy > REPRODUCTION_ENERGY:
            self.energy >>= 1
            new_animal = copy.deepcopy(self)
            mutation = random.randint(0, 7)
            new_animal.genes[mutation] += random.randint(-1, 1)
            new_animal.genes[mutation] = max(new_animal.genes[mutation], 1)
            ANIMALS.append(new_animal)

    def __repr__(self):
        return 'Animal(x=%(x)s, y=%(y)s, energy=%(energy)s, dir=%(dir)s, genes=%(genes)s)' % vars(self)

def update_world():
    global ANIMALS
    ANIMALS = [animal for animal in ANIMALS if animal.energy > 0]
    for animal in ANIMALS:
        animal.turn()
        animal.move()
        animal.eat()
        animal.reproduce()
    add_plants()

def draw_world(out):
    animal_positions = set((animal.x, animal.y) for animal in ANIMALS)
    for y in xrange(HEIGHT):
        out.write('|')
        for x in xrange(WIDTH):
            if (x, y) in animal_positions:
                out.write('M')
            elif (x, y) in PLANTS:
                out.write('*')
            else:
                out.write(' ')
        out.write('|\n')

def evolution():
    try:
        while 1:
            draw_world(sys.stdout)
            if not ANIMALS:
                print "EXTINCTION"
                break
            command = raw_input('steps> ')
            if command.lower() == 'quit':
                break
            if command.lower() == 'animals':
                for animal in ANIMALS:
                    print animal
                print [sum(x)/float(len(ANIMALS)) for x in itertools.izip(
                            *[animal.genes for animal in ANIMALS])]
                continue
            try:
                steps = int(command)
            except ValueError:
                steps = 1
            for i in xrange(steps):
                update_world()
                if i % 1000 == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()

    finally:
        pickle.dump(
            [animal.genes for animal in ANIMALS],
            file('isle.log', 'wt')
        )

WIDTH, HEIGHT = 100, 30

JUNGLE_X, JUNGLE_Y = 45, 10
JUNGLE_WIDTH, JUNGLE_HEIGHT = 10, 10

JUNGLE = JUNGLE_X, JUNGLE_Y, JUNGLE_WIDTH, JUNGLE_HEIGHT
BOARD = 0, 0, WIDTH, HEIGHT

PLANT_ENERGY = 80
REPRODUCTION_ENERGY = 200

PLANTS = set()
ANIMALS = [
    Animal(
        x=WIDTH>>1,
        y=HEIGHT>>1,
        energy=1000,
        dir=0,
        genes=[random.randint(1, 9) for i in xrange(8)]
    )
]

if __name__ == '__main__':
    evolution()

