from FlappyBird import FlappyBird
import os
import argparse

def createGame(name, disable):
    if name == "Flappy Bird":
        return FlappyBird(500,800, disable)
    else:
        print("Unsupported game")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", help="train model", action="store_true")
    parser.add_argument("-d", "--disable",help="Disable drawing the screen", action="store_false")
    parser.add_argument("-g", "--game",help="Game to play", required=True)
    args = parser.parse_args()

    game = createGame(args.game, args.disable)
    game.Init()
    
    if game is None:
        return

    if args.train:
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        game.Train(config_path)
    else:
        game.Run()


def Train(config_file):

    game = FlappyBird(500,800)
    game.Train(config_file)

if __name__ =='__main__':
    main()
