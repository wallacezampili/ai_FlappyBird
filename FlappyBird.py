import neat
import pygame as pg
import os
import random

WINDOW_WIDTH = 500
WINDW_HEIGHT = 760

generation = 0
ai_playing = True

IMG_BIRD = [
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird1.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird2.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird3.png')))
]

IMG_PIPE = pg.transform.scale2x(
    pg.image.load(os.path.join('imgs', 'pipe.png')))
IMG_BACKGROUND = pg.transform.scale2x(
    pg.image.load(os.path.join('imgs', 'bg.png')))
IMG_FLOOR = pg.transform.scale2x(
    pg.image.load(os.path.join('imgs', 'base.png')))

pg.font.init()

SCORE_FONT = pg.font.SysFont('Fipps', 30)


class Bird:
    IMG = IMG_BIRD

    # animations, bird angle

    MAX_ANGLE = 25
    ROTATION_SPD = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.spd = 0
        self.height = self.y
        self.time = 0
        self.sprite_index = 0
        self.sprite = self.IMG[0]

    def jump(self):
        self.spd = -10.5
        self.time = 0
        self.height = self.y

    def move(self):

        # movement
        self.time += 1
        movement = 1.5 * (self.time**2) + self.spd * self.time

        if movement > 16:
            movement = 16
        elif movement < 0:
            movement -= 2

        self.y += movement

        # angle
        if (movement < 0 or self.y < (self.height + 50)):
            if (self.angle < self.MAX_ANGLE):
                self.angle = self.MAX_ANGLE
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPD

    def draw(self, scr):
        # animation
        self.sprite_index += 1

        if self.sprite_index < self.ANIMATION_TIME:
            self.sprite = self.IMG[0]
        elif self.sprite_index < self.ANIMATION_TIME*2:
            self.sprite = self.IMG[1]
        elif self.sprite_index < self.ANIMATION_TIME*3:
            self.sprite = self.IMG[2]
        elif self.sprite_index < self.ANIMATION_TIME*4:
            self.sprite = self.IMG[1]
        elif self.sprite_index >= self.ANIMATION_TIME*4 + 1:
            self.sprite = self.IMG[2]
            self.sprite_index = 0

        if self.angle <= -80:
            self.sprite = self.IMG[1]
            self.sprite_index = self.ANIMATION_TIME*2

        # draw sprite
        image_rotated = pg.transform.rotate(self.sprite, self.angle)
        rect_center = self.sprite.get_rect(topleft=(self.x, self.y)).center
        rect = image_rotated.get_rect(center=rect_center)
        scr.blit(image_rotated, rect.topleft)

    def get_mask(self):
        return pg.mask.from_surface(self.sprite)


class Pipe:
    DISTANCE = 200
    SPEED = 12

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.base = 0
        self.TOP_SPRITE = pg.transform.flip(IMG_PIPE, False, True)
        self.BASE_SPRITE = IMG_PIPE
        self.outOfBounds = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TOP_SPRITE.get_height()
        self.base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, scr):
        scr.blit(self.TOP_SPRITE, (self.x, self.top))
        scr.blit(self.BASE_SPRITE, (self.x, self.base))

    def colision(self, bird):
        bird_mask = bird.get_mask()

        top_mask = pg.mask.from_surface(self.TOP_SPRITE)
        base_mask = pg.mask.from_surface(self.BASE_SPRITE)

        distance_top = (self.x - bird.x, self.top - bird.y)
        distance_base = (self.x - bird.x, self.base - bird.y)

        top_colision = bird_mask.overlap(top_mask, distance_top)
        base_colision = bird_mask.overlap(base_mask, distance_base)

        if (top_colision or base_colision):
            return True
        else:
            return False


class Floor:
    SPEED = 5
    WIDTH = IMG_FLOOR.get_width()
    SPRITE = IMG_FLOOR

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED
        if (self.x1 + self.WIDTH < 0):
            self.x1 = self.WIDTH + self.x2

        if (self.x2 + self.WIDTH < 0):
            self.x2 = self.WIDTH + self.x1

    def draw(self, scr):
        scr.blit(self.SPRITE, (self.x1, self.y))
        scr.blit(self.SPRITE, (self.x2, self.y))


def draw_scr(scr, birds, pipes, floor, score):
    scr.blit(IMG_BACKGROUND, (0, 0))

    for bird in birds:
        bird.draw(scr)

    for pipe in pipes:
        pipe.draw(scr)

    text = SCORE_FONT.render(f'Score: {score}', 1, (0, 0, 0))
    scr.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    
    text = SCORE_FONT.render(f'Generation: {generation}', 1, (0, 0, 0))
    scr.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 30))
    
    floor.draw(scr)

    pg.display.update()


def main(genomes, config):
    global generation
    generation += 1

    if ai_playing:
        network = []
        genome_list = []
        birds = []

        for _, genome in genomes:
            n = neat.nn.FeedForwardNetwork.create(genome, config)
            network.append(n)
            genome.fitness = 0
            genome_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    scr = pg.display.set_mode((WINDOW_WIDTH, WINDW_HEIGHT))
    score = 0
    timer = pg.time.Clock()

    playing = True

    while playing:
        timer.tick(30)

        for event in pg.event.get():
            if (event.type == pg.QUIT):
                pg.quit()
                quit()
            if not ai_playing:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if (len(pipes) > 1) and (birds[0].x > (pipes[0].x + pipes[0].TOP_SPRITE.get_width())):
                pipe_index = 1
        else:
            playing = False
            break


        for i, bird in enumerate(birds):
            bird.move()

            if ai_playing:
                # increase fitness
                genome_list[i].fitness += 0.1
                output = network[i].activate((bird.y, abs(
                    bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].base)))
                # calculate de I.A Params
                if output[0] > 0.5:
                    bird.jump()

        floor.move()

        new_pipe = False
        remove_pipes = []

        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.colision(bird):
                    birds.pop(i)
                    if ai_playing:
                        genome_list[i].fitness -= 1
                        genome_list.pop(i)
                        network.pop(i)
                if not pipe.outOfBounds and bird.x > pipe.x:

                    pipe.outOfBounds = True
                    new_pipe = True
            pipe.move()
            if (pipe.x + pipe.TOP_SPRITE.get_width() < 0):
                remove_pipes.append(pipe)

        if new_pipe == True:
            score += 1
            pipes.append(Pipe(600))
            if ai_playing:
                for genome in genome_list:
                    genome.fitness += 5
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.sprite.get_height() > floor.y) or (bird.y < 0):
                birds.pop(i)
                if ai_playing:
                    genome_list[i].fitness -= 1
                    genome_list.pop(i)
                    network.pop(i)
        draw_scr(scr, birds, pipes, floor, score)


def run(config_path):

    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)


if __name__ == '__main__':
    path = 'config.txt'
    run(path)
