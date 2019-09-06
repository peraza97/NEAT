from abc import ABC, abstractmethod
import pygame

class Game(ABC):
    def __init__(self,width, height,caption):
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = width
        self.height = height
        self.font = None
        self.score = 0
        self.game_name = caption
    
    def Init(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("comicsans", 50)
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.game_name)

    @abstractmethod
    def Run(self):
        pass
    
    @abstractmethod
    def Train(self, config_file):
        pass

