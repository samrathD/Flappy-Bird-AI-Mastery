import pygame
import neat
import time
import os
import random
pygame.font.init()
# Setting height and width of the window of the game
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Loading all the images
# path.join concatenates various path components and creates a single path
# transform.scale2x increases the size of the image by 2x
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Creating bird class
class Bird :
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # The maximum rotation the bird can achieve
    ROT_VEL = 20 # How much to rotate on each frame
    ANIMATION_TIME = 5 # How long we are going to show each bird animation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y
    
    # call move on every single frame to move the bird
    def move(self):
        self.tick_count+=1
        displacement = self.velocity*self.tick_count + 1.5 * self.tick_count**2

        # Fail proof the bird
        # If the bird is moving down too fast the maximum displacement must be 16
        # meaning we want the bird to stop accelerating at some point
        if displacement>16:
            displacement = 16
        
        if displacement<0:
            displacement-=2
        
        # Change the y position based on the displacement
        self.y = self.y + displacement

        # Tilting the bird

        # If the bird is moving up 
        # or if the current position of the bird is less than the position it jumped from 
        # tilt the bird up
        if displacement<0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION :
                self.tilt = self.MAX_ROTATION
        
        # tilting the bird down
        else:
            if self.tilt > -90 :
                self.tilt -= self.ROT_VEL
    
    def draw(self,win):
        self.img_count+=1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
            # print("its here")
        elif self.img_count < 2*self.ANIMATION_TIME:
            self.img = self.IMGS[1]
            # print("its here1")

        elif self.img_count < 3*self.ANIMATION_TIME:
            self.img = self.IMGS[2]
            # print("its here2")
        elif self.img_count < 4*self.ANIMATION_TIME + 1:
            self.img = self.IMGS[1]
            self.img_count = 0
            # print("its here3")
        
        if self.tilt<=-80 :
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        
        rotated_image = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

# Use when we get collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Creating a Pipe class
class Pipe :
    GAP = 200
    velocity = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        
        self.top = 0 # Keep track of where top of the pipe is going to be drawn
        self.bottom = 0 # Keep track of where bottom of the pipe is going to be drawn
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randint(50,450) #Where the face of pipe is located
        self.top = self.height - self.PIPE_TOP.get_height() #Calculate where to place the pipe in order to reach the location for the face
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.velocity
    
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM, (self.x,self.bottom))
    
    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask,top_offset)

        if bottom_point or top_point:
            return True
        
        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0 # Represents the position of the first ground image
        self.x2 = self.WIDTH # Represents the position of the second ground image(Which is after the first image)
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if(self.x1 + self.WIDTH <=0):
            self.x1 = self.x2 + self.WIDTH
        
        if(self.x2 + self.WIDTH <=0):
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

# Create a draw_window function 
def draw_window(win,birds, pipes, base, score):
    win.blit(BG_IMG,(0,0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), True, (255,255,255))

    win.blit(text,(WIN_WIDTH -10 - text.get_width(),10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

# Create a main function
def main(genomes, config): 
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0 
        ge.append(g)

    # bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(600)]

    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes)>1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        # if all the birds die quit the generation
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness+= 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump() 
        # bird.move()
        base.move()    
        add_pipe = False
        rem = [] # A remove list that stores removed pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # check for collision
                if pipe.collide(bird) == True:
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            # If pipe is completly off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        
        if add_pipe:
            score+=1
            # Increase the fitness
            for g in ge:
                g.fitness+=5
            pipes.append(Pipe(600)) # Add a new pipe in the pipes list
        
        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            # Check if the bird hit the ground
            if bird.y + bird.img.get_height() >= 730 or bird.y<0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        # if score>=50:
        #     break


        draw_window(win,birds, pipes, base, score)
    

def run(config_path):
    # Load the configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)

    # Print stats on terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    # Locating the configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    # 
    run(config_path)