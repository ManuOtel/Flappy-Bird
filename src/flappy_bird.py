"""Flappy Bird AI.

This module contains both the creation of Flappy Bird game and the NEAT algorithm training. 

@Author: Emanuel-Ionut Otel
@Created: 2020-05-15
@Contact: manuotel@gmail.com
"""

#### ---- IMPORTS AREA ---- ####
import pygame, neat, os, random
#### ---- IMPORTS AREA ---- ####


#### ---- INIT AREA ---- ####
os.chdir('..')
pygame.font.init()
WIN_WIDTH = 550
WIN_HEIGHT = 800
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#### ---- INIT AREA ---- ####


class Bird:
    """Bird class.

    This class contains the bird object and its methods.

    :attr x: The x coordinate of the bird.
    :attr y: The y coordinate of the bird.
    :attr tilt: The tilt of the bird.
    :attr tick_count: The tick count of the bird.
    :attr vel: The velocity of the bird.
    :attr height: The height of the bird.
    :attr img_count: The image count of the bird.
    :attr img: The image of the bird.
    :attr IMGS: The list of images of the bird.
    :attr MAX_ROTATION: The maximum rotation of the bird.
    :attr ROT_VEL: The rotation velocity of the bird.
    :attr ANIMATION_TIME: The animation time of the bird.
    """
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self) -> None:
        """This method makes the bird jump.
        
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self) -> None:
        """This method makes the bird move.

        :return: None
        """
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win) -> None:
        """This method draws the bird.
        
        :param win: The window of the game.
        :return: None"""
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 5:
            self.img = self.IMGS[1]
        elif self.img_count >= self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    """Pipe class.
    
    This class contains the pipe object and its methods.
    
    :attr x: The x coordinate of the pipe.
    :attr height: The height of the pipe.
    :attr gap: The gap between the pipes.
    :attr top: The top of the pipe.
    :attr bottom: The bottom of the pipe.
    :attr PIPE_TOP: The top image of the pipe.
    :attr PIPE_BOTTOM: The bottom image of the pipe.
    :attr passed: The passed attribute of the pipe.
    :attr GAP: The gap between the pipes.
    :attr VEL: The velocity of the pipe.
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self) -> None:
        """Sets the height of the pipe.

        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self) -> None:
        """Moves the pipe.

        :return: None
        """
        self.x -= self.VEL

    def draw(self, win) -> None:
        """Draws the pipe.

        :param win: The window of the game.

        :return: None
        """
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird) -> bool:
        """Checks if the bird collides with the pipe.

        :param bird: The bird object.

        :return: True if the bird collides with the pipe, False otherwise.
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bot_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bot_offset = (self.x - bird.x, self.bottom - round(bird.y))
        b_point = bird_mask.overlap(bot_mask, bot_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if t_point or b_point:
            return True
        return False


class Base:
    """Base class.
    
    This class contains the base object and its methods.
    
    :attr y: The y coordinate of the base.
    :attr x1: The x coordinate of the first base image.
    :attr x2: The x coordinate of the second base image.
    :attr VEL: The velocity of the base.
    :attr WIDTH: The width of the base image.
    :attr IMG: The base image.
    """
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self) -> None:
        """Moves the base.

        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win) -> None:
        """Draws the base.

        :param win: The window of the game.

        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score) -> None:
    """Draws the whole window with all the elements.

    :param win: The window of the game.
    :param birds: The list of birds.
    :param pipes: The list of pipes.
    :param base: The base object.
    :param score: The score of the game.

    :return: None
    """
    win.blit(BG_IMG, (0, 0))
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    win.blit(text, (10, 10))
    pygame.display.update()


def main(genomes, config) -> None:
    """ Runs both the game and the training based on the genomes and the config file.

    :param genomes: The genomes of the birds.
    :param config: The config file.

    :return: None
    """
    nets = []
    ge = []
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    birds = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    pipes = [Pipe(700)]
    base = Base(730)
    run = True
    score = 0
    clock = pygame.time.Clock()
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        pipe_int = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_int = 1
        else:
            run = False
            break
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_int].height), abs(bird.y - pipes[pipe_int].bottom)))
            if output[0] > 0.5:
                bird.jump()
        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        base.move()
        draw_window(win, birds, pipes, base, score)


def run(config_path) -> None:
    """Runs the game.

    :param config_path: The path of the config file.

    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    _ = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
