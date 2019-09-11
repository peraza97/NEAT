from abc import ABC, abstractmethod
import pygame

pygame.init()

class Game(ABC):
    def __init__(self,width, height,caption,display):
        self.clock = None
        self.gameName = caption
        self.width = width
        self.height = height
        self.display = display
        self.score = 0
        self.font = None
        self.window = None

    def Init(self):
        self.running = True
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsans", 50)
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.gameName)

    @abstractmethod
    def Run(self):
        pass
    
    @abstractmethod
    def Train(self, config_file):
        pass

