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
def draw_window(win,bird, pipes, base, score):
    win.blit(BG_IMG,(0,0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), True, (255,255,255))

    win.blit(text,(WIN_WIDTH -10 - text.get_width(),10))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

# Create a main function
def main():
    bird = Bird(230,350)
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
        
        # bird.move()
        base.move()    
        add_pipe = False
        rem = [] # A remove list that stores removed pipes
        for pipe in pipes:
            # check for collision
            if pipe.collide(bird) == True:
                pass
            # If pipe is completly off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()
        
        if add_pipe:
            score+=1
            pipes.append(Pipe(600)) # Add a new pipe in the pipes list
        
        for r in rem:
            pipes.remove(r)

        # Check if the bird hit the ground
        if bird.y + bird.img.get_height() >= 730:
            pass



        draw_window(win,bird, pipes, base, score)
    pygame.quit()
    quit()

main()
print("hello")