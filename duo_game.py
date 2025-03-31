#!/usr/bin/env python
""" pygame.examples.aliens

Shows a mini game where you have to defend against aliens.

What does it show you about pygame?

* pg.sprite, the difference between Sprite and Group.
* dirty rectangle optimization for processing for speed.
* music with pg.mixer.music, including fadeout
* sound effects with pg.Sound
* event processing, keyboard handling, QUIT handling.
* a main loop frame limited with a game clock from pg.time.Clock
* fullscreen switching.


Controls
--------

* Left and right arrows to move.
* Space bar to shoot
* f key to toggle between fullscreen.

"""

import os
import math
import random
from typing import List

# import basic pygame modules
import pygame as pg

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# game constants
schermox = 1400
schermoy = 770
SCREENRECT = pg.Rect(0, 0, schermox, schermoy)
main_dir = os.path.split(os.path.abspath(__file__))[0]
ASTEROID_WAIT = 10
SCORE = 0

def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert_alpha()


def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print(f"Warning, unable to load, {file}")
    return None


# Each type of game object gets an init and an update function.
# The update function is called once per frame, and it is when each object should
# change its current position and state.
#
# The Player object actually gets a "move" function instead of update,
# since it is passed extra information about the keyboard.


class Player(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.velx = 0
        self.vely = -70
        self.attrito = 1.15
        self.rotvel = 1
        self.acceleration = 3
        self.score = 0
        self.mask = pg.mask.from_surface(self.image)
        self.rect.move_ip(0, 200)
        self.start = True
        self.respawn = False
        self.tempo = -1
        self.invincible = False
        self.invincibiletime = 0
        self.intalpha = 255


    def move(self, directionx, directiony):
        if self.respawn == True and self.tempo == 0:
            self.vely = -100
            self.respawn = False
            self.tempo = -1
            self.invincible = True
            self.invincibiletime = 0
        else:
            self.tempo = self.tempo - 1
            if self.start == True:
                if self.rect[1] < (schermoy - 60):
                    self.start = False
            else:
                if self.rect[0] > (schermox - 110) or self.rect[0] < 0:
                # errore da risolvere
                    self.alive = False
                
                if self.rect[1] > (schermoy - 60) or self.rect[1] < 0:
                # errore da risolvere
                    self.alive = False

            

            
            
            self.velx = (self.velx + directionx * self.acceleration) / self.attrito
            # self.image = pg.transform.rotate(self.image, self.vel)
            self.rect.move_ip(self.velx, 0)
            self.vely = (self.vely + directiony * 2) / self.attrito
            self.image = pg.transform.rotate(self.images[0], -self.velx)
            c = self.rect.center
            self.rect = self.image.get_rect(center = c)
            self.mask = pg.mask.from_surface(self.image)
            self.rect.move_ip(0, self.vely)
            self.invincibiletime = self.invincibiletime + 1
            if self.invincible == True and (self.invincibiletime % 10) == 0:
                self.intalpha = 60
                if (self.invincibiletime % 20) == 0:
                    self.intalpha = 255
                    if (self.invincibiletime % 100) == 0:
                        self.invincible = False

            self.image.set_alpha(self.intalpha)

class Meteor(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(x = random.randint(0, schermox), y = 0)
        self.image = pg.transform.scale(self.images[0], (10, 10))
        self.velx = random.randint(0, 5)
        if self.rect[0] > (schermox / 2):
            self.velx = self.velx * -1
        self.vely = random.randint(3, 10)
        self.tilt = random.randint(0, 359)
        self.rotatevel = random.randint(-6, 6)
        self.grandezza = random.randint(8, 12) / 10
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.tilt = self.tilt + self.rotatevel
        self.rect.move_ip(self.velx, self.vely)
        self.image = pg.transform.rotate(self.images[0], self.tilt)
        self.image = pg.transform.scale_by(self.image, self.grandezza)
        self.mask = pg.mask.from_surface(self.image)
        c = self.rect.center
        self.rect = self.image.get_rect(center = c)
        if self.rect[1] > (schermoy + 100):
            self.kill()
        

class Stella(pg.sprite.Sprite):

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(x = random.randint(0, schermox), y = random.randint(0, schermoy))

class Coin(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    def __init__(self, player, where, how, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        if where == 0:
            self.rect = self.image.get_rect(x = random.randint(0, schermox), y = 0)
        else:
            self.rect = self.image.get_rect(x = player.rect[0], y = player.rect[1])
        if how == 1:
            self.velx = random.randint(-10, 10)
            self.vely = random.randint(-10, 10)
        else:
            self.velx = random.randint(0, 5)
            if self.rect[0] > (schermox / 2):
                self.velx = self.velx * -1
            self.vely = random.randint(3, 10)

        self.image = pg.transform.scale(self.images[0], (10, 10))
        self.tilt = random.randint(0, 359)
        self.rotatevel = random.randint(-6, 6)
        self.mask = pg.mask.from_surface(self.image)


    def update(self):
        self.tilt = self.tilt + self.rotatevel
        self.rect.move_ip(self.velx, self.vely)
        self.image = pg.transform.rotate(self.images[0], self.tilt)
        self.mask = pg.mask.from_surface(self.image)
        c = self.rect.center
        self.rect = self.image.get_rect(center = c)
        if self.rect[1] > (schermoy + 100):
            self.kill()

class Score(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = pg.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = "blue"
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(0, 0)

    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = f"{SCORE}"
            self.image = self.font.render(msg, 0, self.color)
            


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image("Nave-Sheet.png")
    Player.images = [pg.transform.scale_by(img, 0.3)]
    img = load_image("asteroid.png")
    Meteor.images = [pg.transform.scale_by(img, 0.1)]
    img = load_image("stella.png")
    Stella.images = [pg.transform.scale_by(img, 0.005)]
    img = load_image("coin.png")
    Coin.images = [pg.transform.scale_by(img, 0.05)]

    # decorate the game window
    pg.mouse.set_visible(0)

    # Initialize Game Groups
    all = pg.sprite.RenderUpdates()
    meteoriti = pg.sprite.Group()
    coins = pg.sprite.Group()
    stella = pg.sprite.Group()
    numbers = range(0, 80)
    for x in numbers:
        stelle = Stella(all, stella)

    # Create Some Starting Values
    clock = pg.time.Clock()
    count = 0

    # initialize our starting sprites
    player = Player(all)

    # Run our main loop whilst the player is alive.
    screen_backup = screen.copy()
    screen = pg.display.set_mode(SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth)
    screen.blit(screen_backup, (0, 0))
    pg.display.flip()
    global SCORE
    if pg.font:
        all.add(Score(all))
    
    while player.alive:
        
        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                for x in meteoriti:
                    dx = x.rect[0] - player.rect[0]
                    dy = x.rect[1] - player.rect[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    mag = 5000 / (dist * dist)
                    x.velx = x.velx + mag * (x.rect[0] - player.rect[0])
                    x.vely = x.vely + mag * (x.rect[1] - player.rect[1])
                    x.rotatevel = x.rotatevel / mag / 5
                for x in coins:
                    dx = x.rect[0] - player.rect[0]
                    dy = x.rect[1] - player.rect[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    mag = 5000 / (dist * dist)
                    x.velx = x.velx + mag * (x.rect[0] - player.rect[0])
                    x.vely = x.vely + mag * (x.rect[1] - player.rect[1])
                    x.rotatevel = x.rotatevel / mag / 5
            
        keystate = pg.key.get_pressed()

        #create meteor
        if count == ASTEROID_WAIT:
            meteor = Meteor(all, meteoriti)
            count = 0
        else:
            count = count + 1

        if count == ASTEROID_WAIT * 2:
            coin = Coin(player, 0, 0, coins, all)
            count = 0
        else:
            count = count + 1    

        # clear/erase the last drawn sprites
        background = pg.Surface(SCREENRECT.size)
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        if player.start == False:
            directionx = (keystate[pg.K_RIGHT] - keystate[pg.K_LEFT])
            directiony = (keystate[pg.K_DOWN] - keystate[pg.K_UP])
            player.move(directionx, directiony)
        else:
            player.move(0, 0)
        
        if player.invincible == False:
            for x in pg.sprite.spritecollide(player, meteoriti, 1, pg.sprite.collide_mask):
                SCORE = SCORE - 20
                num = range(0, 20)
                for x in num:
                    coin = Coin(player, 1, 1, coins, all)
                player.rect[0] = 600
                player.rect[1] = 1000
                player.respawn = True
                player.tempo = 200
                player.start = True

            for x in pg.sprite.spritecollide(player, coins, 1, pg.sprite.collide_mask):
                SCORE = SCORE + 1

        # draw the scene
        dirty = all.draw(screen)
        #pg.draw.rect(screen, (255, 0, 0), player.rect, width = 1)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(40)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
