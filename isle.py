import itertools
import random
import copy
import sys
import pickle
import Tkinter as tk


def angle(genes):
    random_seed = random.randint(0, sum(genes) - 1)
    for index, gene in enumerate(genes):
        random_seed -= gene
        if random_seed < 0:
            return index


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
        self.x %= World.WIDTH
        self.y %= World.HEIGHT
        self.energy -= 1

    def turn(self):
        self.dir += angle(self.genes)
        self.dir %= 8

    def eat(self, plants):
        if (self.x, self.y) in plants:
            self.energy += World.PLANT_ENERGY
            plants.remove((self.x, self.y))

    def reproduce(self):
        if self.energy > World.REPRODUCTION_ENERGY:
            self.energy >>= 1
            new_animal = copy.deepcopy(self)
            mutation = random.randint(0, 7)
            new_animal.genes[mutation] += random.randint(-1, 1)
            new_animal.genes[mutation] = max(new_animal.genes[mutation], 1)
            return [new_animal]
        else:
            return []

    def __repr__(self):
        return 'Animal(x=%(x)s, y=%(y)s, energy=%(energy)s, dir=%(dir)s, genes=%(genes)s)' % vars(self)


class World(object):
    WIDTH, HEIGHT = 100, 30

    JUNGLE_X, JUNGLE_Y = 45, 10
    JUNGLE_WIDTH, JUNGLE_HEIGHT = 10, 10

    JUNGLE = JUNGLE_X, JUNGLE_Y, JUNGLE_WIDTH, JUNGLE_HEIGHT
    BOARD = 0, 0, WIDTH, HEIGHT

    PLANT_ENERGY = 80
    REPRODUCTION_ENERGY = 200

    def __init__(self):
        self.plants = set()
        self.animals = [
            Animal(
                x=World.WIDTH >> 1,
                y=World.HEIGHT >> 1,
                energy=1000,
                dir=0,
                genes=[random.randint(1, 9) for i in xrange(8)]
            )
        ]

    def add_random_plant(self, left, top, width, height):
        pos_x = random.randint(left, left + width - 1)
        pos_y = random.randint(top, top + height - 1)
        self.plants.add((pos_x, pos_y))

    def add_plants(self):
        self.add_random_plant(*(World.JUNGLE))
        self.add_random_plant(*(World.BOARD))

    def update(self):
        for animal in self.animals[:]:
            if animal.energy < 0:
                self.animals.remove(animal)
            else:
                animal.turn()
                animal.move()
                animal.eat(self.plants)
                new_animals = animal.reproduce()
                self.animals.extend(new_animals)
        self.add_plants()


def draw_world(world, out):
    animal_positions = set((animal.x, animal.y) for animal in world.animals)
    for y in xrange(World.HEIGHT):
        out.write('|')
        for x in xrange(World.WIDTH):
            if (x, y) in animal_positions:
                out.write('M')
            elif (x, y) in world.plants:
                out.write('*')
            else:
                out.write(' ')
        out.write('|\n')


def print_stats(animals):
    for animal in animals:
        print animal
    print [sum(x) / float(len(world.animals)) for x in itertools.izip(
        *[animal.genes for animal in world.animals])]


def evolution(world):
    try:
        while 1:
            draw_world(world, sys.stdout)
            if not world.animals:
                print "EXTINCTION"
                break
            command = raw_input('steps> ')
            if command.lower() == 'quit':
                break
            if command.lower() == 'animals':
                print_stats(world.animals)
                continue
            try:
                steps = int(command)
            except ValueError:
                steps = 1
            for i in xrange(steps):
                world.update()
                if i % 1000 == 0 and i > 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()
            else:
                print
    finally:
        pickle.dump(
            [animal.genes for animal in world.animals],
                                                      file('isle.log', 'wt')
        )


class View(object):
    ITEM_SIZE = 10
    TIME_STEP = 10

    def __init__(self, root, world):
        self.world = world
        self.root = root
        self.frame = tk.Frame(root)

        self.create_canvas()
        self.create_button()

        self.frame.pack()

    def create_canvas(self):
        self.canvas = tk.Canvas(
            self.frame,
            width=World.WIDTH * View.ITEM_SIZE,
            height=World.HEIGHT * View.ITEM_SIZE)
        self.canvas.pack()

    def create_button(self):
        self.var = tk.IntVar()
        self.button = tk.Checkbutton(
            self.frame,
            text="Go",
            variable=self.var,
            command=self.start
        )
        self.button.pack()

    def should_continue(self):
        return self.var.get() == 1

    def start(self):
        self.update()

    def update(self):
        self.world.update()
        self.update_ui()
        if self.should_continue():
            self.root.after(View.TIME_STEP, self.update)

    def update_ui(self):
        self.clear_ui()
        for (plant_x, plant_y) in self.world.plants:
            plant_x *= View.ITEM_SIZE
            plant_y *= View.ITEM_SIZE
            self.canvas.create_oval(
                plant_x, plant_y, plant_x + View.ITEM_SIZE, plant_y + View.ITEM_SIZE,
                fill='green'
            )
        for animal in self.world.animals:
            animal_x = animal.x * View.ITEM_SIZE
            animal_y = animal.y * View.ITEM_SIZE
            self.canvas.create_oval(
                animal_x, animal_y, animal_x + View.ITEM_SIZE, animal_y + View.ITEM_SIZE,
                fill=self.animal_color(animal)
            )

    def animal_color(self, _animal):
        # may depend on energy or genes
        return 'black'

    def clear_ui(self):
        self.canvas.delete(tk.ALL)

if __name__ == '__main__':
    world = World()
    if '-gui' in sys.argv:
        root = tk.Tk()
        window = View(root, world)
        root.protocol('WM_DELETE_WINDOW', root.quit)
        root.mainloop()
    else:
        evolution(world)


