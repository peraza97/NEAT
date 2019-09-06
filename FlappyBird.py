import pygame
import os
import random
import neat
from Game import Game

CLOCK = pygame.time.Clock()
WIN = pygame.display.set_mode((500, 800))
gen = 0

class FlappyBird(Game):
    def __init__(self, height, width, draw):
        super().__init__(height,width,"Flappy Bird")
        self.draw = draw
        self.bg_img = pygame.transform.scale(pygame.image.load(os.path.join("FlappyBirdImgs","bg.png")).convert_alpha(), (500, 800))
        self.bird = None
        self.pipes = []
        self.base = None

    def Init(self):
        super().Init()
        self.bird = Bird((230,350))
        self.base = Base(730)
        self.pipes = [Pipe(500)]

    def Draw(self):
        #draw the background image
        self.window.blit(self.bg_img, (0,0))
        #draw the pipes
        for pipe in self.pipes:
            pipe.Draw(self.window)
        #draw the base
        self.base.Draw(self.window)
        #draw the bird
        self.bird.Draw(self.window)

        score_label = self.font.render("Score: " + str(self.score),1,(255,255,255))
        self.window.blit(score_label, (self.width - score_label.get_width() - 15, 10))

        pygame.display.update()
        self.clock.tick(30)

    def Logic(self):

        #move bird and base 
        self.bird.Move()
        self.base.Move()

        #move pipe and check for collision
        for pipe in self.pipes:
            pipe.Move()
            
            #check if the bird has collided with pipe
            if pipe.Collide(self.bird):
                self.running = False

            #check if the bird has just passed the pipe
            if pipe.JustPassed(self.bird):
                self.score += 1 
                self.pipes.append(Pipe(550))
        
        #Need to check if left most pipe goes off screen
        if self.pipes[0].OffScreen():
            del(self.pipes[0])
 
        #if bird is off screen
        if self.bird.y + self.bird.img.get_height() > 730 or self.bird.y < 0:
            self.running = False

    def Run(self):
        while self.running:
            #event handler
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.bird.Jump()
                if event.type == pygame.QUIT:
                    exit()

            self.Logic()
            self.Draw()

    def eval_birds(self, genomes, config):

        global WIN, CLOCK, gen
        win = WIN
        gen += 1
        clock = CLOCK

        #set up
        score = 0
        pipes = [Pipe(600)]
        base = Base(730)

        nets = []
        birds = []
        ge = []
        for genome_id, genome in genomes:
            genome.fitness = 0  # start with fitness level of 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            birds.append(Bird((230,350)))
            ge.append(genome)

        running = True
        while running and len(birds) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exit()
            
            pipe_ind = 0
            for i, pipe in enumerate(pipes):
                if birds[0].x > pipe.x + pipe.pipe_top.get_width():
                    pipe_ind = i + 1
                    break

            for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
                ge[x].fitness += 0.1
                bird.Move()

                # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
                output = nets[birds.index(bird)].activate((bird.y, bird.y - pipes[pipe_ind].height, bird.y - pipes[pipe_ind].bottom, bird.velocity))

                if output[0] > 0.5: 
                    bird.Jump()
        
            base.Move()
            rem_birds = []
            for pipe in pipes:
                pipe.Move()
                for bird in birds:
                    #check if the bird has collided with pipe or goes off screen
                    if pipe.Collide(bird) or bird.y + bird.img.get_height() > 730 or bird.y < 0:
                        ge[birds.index(bird)].fitness -= 1
                        rem_birds.append(bird)
                        nets.pop(birds.index(bird))
                        ge.pop(birds.index(bird))
                        birds.pop(birds.index(bird))
                
                    #check if the bird has passed the pipe
                    if pipe.JustPassed(bird):
                        score += 1 
                        pipes.append(Pipe(600))
            
            #Need to check if left most pipe goes off screen
            if pipes[0].OffScreen():
                del(pipes[0])

            if self.draw:
                self.TrainDraw(clock, win, birds, pipes, base, gen, score)

    def TrainDraw(self, clock, win, birds, pipes, base, gen, score):
            win.blit(self.bg_img, (0,0))
            #draw the pipes
            for pipe in pipes:
                pipe.Draw(win)
            #draw the base
            base.Draw(win)
            #draw the birds
            for bird in birds:
                bird.Draw(win)
            
            score_label = self.font.render("Score: " + str(score),1,(255,255,255))
            win.blit(score_label, (self.width - score_label.get_width() - 15, 10))

            gen_label = self.font.render("Gen: " + str(gen),1,(255,255,255))
            win.blit(gen_label, (5, 10))

            pop_label = self.font.render("Pop: " + str(len(birds)),1,(255,255,255))
            win.blit(pop_label, (5, 50))
            pygame.display.update()
            clock.tick(30)
             
    def Train(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_file)

        p = neat.Population(config)
        # Add a stdout reporter to show progress in the terminal.
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        best = p.run(self.eval_birds, 50)

class Bird:

    max_rotation = 25
    rotation_velocity = 20
    animation_time = 5
    imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBirdImgs","bird" + str(x) + ".png"))) for x in range(1,4)]
    def __init__(self, start_pos):
        self.imgs = Bird.imgs
        self.img = self.imgs[0]
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
    
    def Jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def Move(self):
        self.tick_count +=1
        # for downward acceleration
        displacement = self.velocity*(self.tick_count) + 1.5 *(self.tick_count)**2

        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement
        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < Bird.max_rotation:
                self.tilt = Bird.max_rotation
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= Bird.rotation_velocity
        
    def Draw(self, window):
        self.img_count += 1

        if self.img_count < Bird.animation_time:
            self.img = self.imgs[0]
        elif self.img_count < Bird.animation_time * 2:
            self.img = self.imgs[1]
        elif self.img_count < Bird.animation_time * 3:
            self.img = self.imgs[2]
        elif self.img_count < Bird.animation_time * 4:
            self.img = self.imgs[1]
        elif self.img_count == Bird.animation_time * 4 + 1:
            self.img = self.imgs[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = Bird.animation_time*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
        window.blit(rotated_img,new_rect.topleft)
    
    def GetPos(self):
        return (self.x, self.y)

    def GetMask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    gap = 150
    velocity = 5
    pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBirdImgs","pipe.png")).convert_alpha())
    
    def __init__(self,x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.pipe_top = pygame.transform.flip(Pipe.pipe_img,False,True)
        self.pipe_bottom = Pipe.pipe_img

        self.passed = False
        self.SetHeight()
    
    def SetHeight(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + Pipe.gap

    def Move(self):
        self.x -= Pipe.velocity
    
    def Draw(self, window):
        window.blit(self.pipe_top, (self.x,self.top))
        window.blit(self.pipe_bottom, (self.x,self.bottom))
    
    def Collide(self, bird):
        
        if self.passed == True:
            return False

        bird_mask = bird.GetMask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bot_mask = pygame.mask.from_surface(self.pipe_bottom)

        top_offset = (self.x - bird.x , self.top - round(bird.y))
        bot_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bot_mask,bot_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if(b_point or t_point):
            return True

        return False

    def JustPassed(self, bird):
        if self.passed == False and self.x < bird.GetPos()[0]:
            self.passed = True
            return True
        return False

    def OffScreen(self):
        if self.x + self.pipe_top.get_width() < 0:
            return True

class Base:
    velocity = 5
    base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("FlappyBirdImgs","base.png")).convert_alpha())
    
    def __init__(self, y):
        self.img = Base.base_img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.y = y
        self.firstX = 0
        self.secondX = self.width

    def Move(self):
        self.firstX -= Base.velocity
        self.secondX -= Base.velocity

        if self.firstX + self.width < 0:
            self.firstX = self.secondX + self.width
        if self.secondX + self.width < 0:
            self.secondX = self.firstX + self.width
    
    def Draw(self, win):
        win.blit(self.img,(self.firstX, self.y))
        win.blit(self.img,(self.secondX, self.y))



