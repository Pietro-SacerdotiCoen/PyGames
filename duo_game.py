#!/usr/bin/env python
""" pygame.examples.aliens

Shows a mini game where you have to defend against aliens.

What does it show you about pygame?

* pg.sprite, the difference between Sprite and Group.
* dirty rectangle optimization for processing for speed.
* music with pg.mixer.music, including fadeout
* sound effects with pg.Sound
* event processing, keyboard handling, self.esci handling.
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
SECONDS = 90

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
    """Representing the player1 as a moon buggy type car."""

    def __init__(self, who, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[who]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.velx = random.randint(0, 5)
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
        self.score = 0
        self.who = who
        self.specialtime = 15


    def move(self, directionx, directiony, coins, meteoriti, all): 
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
    
            self.velx = (self.velx + directionx * self.acceleration) / self.attrito
            # self.image = pg.transform.rotate(self.image, self.vel)
            self.rect.move_ip(self.velx, 0)
            self.vely = (self.vely + directiony * 2) / self.attrito
            self.image = pg.transform.rotate(self.images[self.who], -self.velx)
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


    def special(self, rot, special_sound): 
        if self.start != True and self.specialtime == 15:         
            special_sound.play()
            self.specialtime = 0
            for x in rot:
                dx = x.rect[0] - self.rect[0]
                dy = x.rect[1] - self.rect[1]
                dist = math.sqrt(dx*dx + dy*dy)
                mag = 5000 / (dist * dist)
                x.velx = x.velx + mag * (x.rect[0] - self.rect[0])
                x.vely = x.vely + mag * (x.rect[1] - self.rect[1])
                x.rotatevel = max(min(x.rotatevel / mag / 5, 360), -360)
        
    def input(self, coins, meteoriti, keystate, who, all):
        if who == 0:
            if self.start == False:
                directionx = (keystate[pg.K_KP_6] - keystate[pg.K_KP_4])
                directiony = (keystate[pg.K_KP_5] - keystate[pg.K_KP_8])
                self.move(directionx, directiony, coins, meteoriti, all)
            else:
                self.move(0, 0, coins, meteoriti, all)
        else:
            if self.start == False:
                directionx = (keystate[pg.K_d] - keystate[pg.K_a])
                directiony = (keystate[pg.K_s] - keystate[pg.K_w])
                self.move(directionx, directiony, coins, meteoriti, all)
            else:
                self.move(0, 0, coins, meteoriti, all)
    
    def coll(self, coins, meteoriti, all, boom_sound, coin_sound):
        if self.invincible == False:
            for x in pg.sprite.spritecollide(self, meteoriti, 1, pg.sprite.collide_mask):
                num = range(0, min(10, self.score))
                for x in num:
                    coin = Coin(self, 1, 1, coins, all)
                self.score = self.score - min(10, self.score)
                self.rect[0] = 600
                self.rect[1] = 1000
                self.respawn = True
                self.tempo = 200
                self.start = True
                boom_sound.play()

            for x in pg.sprite.spritecollide(self, coins, 1, pg.sprite.collide_mask):
                self.score = self.score + 1
                coin_sound.play()
            
            if self.start == False:
                if self.rect[0] > (schermox - 110) or self.rect[0] < 0:
                    num = range(0, min(10, self.score))
                    for x in num:
                        coin = Coin(self, 1, 1, coins, all)
                    self.score = self.score - min(10, self.score)
                    self.rect[0] = 600
                    self.rect[1] = 1000
                    self.respawn = True
                    self.tempo = 200
                    self.start = True
                    boom_sound.play()
                
                if self.rect[1] > (schermoy - 60) or self.rect[1] < 0:
                    num = range(0, min(10, self.score))
                    for x in num:
                        coin = Coin(self, 1, 1, coins, all)
                    self.score = self.score - min(10, self.score)
                    self.rect[0] = 600
                    self.rect[1] = 1000
                    self.respawn = True
                    self.tempo = 200
                    self.start = True
                    boom_sound.play()
 

class Meteor(pg.sprite.Sprite):
    """Representing the player1 as a moon buggy type car."""

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
        self.tilt = (self.tilt + self.rotatevel) % 360
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
    """Representing the player1 as a moon buggy type car."""

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
        self.tilt = (self.tilt + self.rotatevel) % 360
        self.rect.move_ip(self.velx, self.vely)
        self.image = pg.transform.rotate(self.images[0], self.tilt)
        self.mask = pg.mask.from_surface(self.image)
        c = self.rect.center
        self.rect = self.image.get_rect(center = c)
        if self.rect[1] > (schermoy + 100):
            self.kill()
class Score(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, player, x, y, color, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = pg.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = color
        self.lastscore = -1
        self.player = player
        self.rect = pg.Rect(x, y, x, y)
        
    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        if self.player.score != self.lastscore:
            self.lastscore = self.player.score
            msg = f"{self.player.score}"
            self.image = self.font.render(msg, 0, self.color)
            self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)

class Timer(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, TEMPOs, click_sound, player1, player2, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = pg.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = "white"
        self.rect = pg.Rect(650, 0, 0, 0)
        self.time = SECONDS * 1000
        self.comma = ":"
        self.esci = False
        self.click_sound = click_sound
        self.lasttime = -1
        self.player1 = player1
        self.player2 = player2
        
    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        msg = f"{math.floor(self.time / 60)}{self.comma}{self.time % 60}"
        self.image = self.font.render(msg, 0, self.color)
        self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)
        
    def aggiorna(self, TEMPOs):
        self.time = math.floor(TEMPOs / 1000)
        if self.time != self.lasttime:
            self.lasttime = self.time
            if self.player1.specialtime < 15:
                self.player1.specialtime += 1
            if self.player2.specialtime < 15:
                self.player2.specialtime += 1
            if self.time <= 10:
                self.click_sound.play()
                self.color = "red"
                if self.time <= 0:
                    self.esci = True

class Bar(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, numero, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        if numero < 15:
            self.distx = numero * 7 + 20
        else:
            self.distx = numero * 7 + 1200
        self.rect = self.image.get_rect(x = self.distx, y = 20)

        
    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
            
        
            
            


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

    TEMPOs = SECONDS * 1000

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img1 = load_image("Nave-Sheet.png")
    img2 = load_image("Nave-Sheet-Red.png")
    Player.images = [pg.transform.scale_by(img1, 0.3), pg.transform.scale_by(img2, 0.3)]
    img = load_image("asteroid.png")
    Meteor.images = [pg.transform.scale_by(img, 0.1)]
    img = load_image("stella.png")
    Stella.images = [pg.transform.scale_by(img, 0.005)]
    img = load_image("coin.png")
    Coin.images = [pg.transform.scale_by(img, 0.05)]
    img = load_image("red_square.png")
    Bar.images = [pg.transform.scale_by(img, 0.05)]

    boom_sound = load_sound("booms.wav")
    coin_sound = load_sound("coin.mp3")
    special_sound = load_sound("special.wav")
    click_sound = load_sound("click.mp3")

    # decorate the game window
    pg.mouse.set_visible(0)

    # Initialize Game Groups
    all = pg.sprite.RenderUpdates()
    meteoriti = pg.sprite.Group()
    bars = pg.sprite.Group()
    coins = pg.sprite.Group()
    rot = pg.sprite.Group()
    stella = pg.sprite.Group()
    numbers = range(0, 80)
    for x in numbers:
        stelle = Stella(all, stella)
    for x in range(0, 15 * 2):
        block = Bar(x, all, bars)

    # Create Some Starting Values
    clock = pg.time.Clock()
    ast_count = 0
    coin_count = 0

    # initialize our starting sprites
    player1 = Player(0, all)
    player2 = Player(1, all)
    time = Timer(TEMPOs, click_sound, player1, player2)
    all.add(time)

    # Run our main loop whilst the player1 is alive.
    screen_backup = screen.copy()
    screen = pg.display.set_mode(SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth)
    screen.blit(screen_backup, (0, 0))
    pg.display.flip()
    if pg.font:
        all.add(Score(player1, 1320, 0, "blue", all))
        all.add(Score(player2, 10, 0, "red", all))

    start_time = pg.time.get_ticks()
    
    while player1.alive:
        
        TEMPOs =  SECONDS * 1000 - pg.time.get_ticks() + start_time
        time.aggiorna(TEMPOs)
    
        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_RALT:
                player1.special(rot, special_sound)
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                player2.special(rot, special_sound)
            
            
        #create meteor
        if ast_count >= ASTEROID_WAIT:
            meteor = Meteor(all, meteoriti, rot)
            ast_count = 0
        else:
            ast_count += 1

        if coin_count >= ASTEROID_WAIT * 2: 
            coin = Coin(player1, 0, 0, coins, all, rot)
            coin_count = 0
        else:
            coin_count += 1    

        # clear/erase the last drawn sprites
        background = pg.Surface(SCREENRECT.size)
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player1 input
        keystate = pg.key.get_pressed()
        player1.input(coins, meteoriti, keystate, 0, all)
        player2.input(coins, meteoriti, keystate, 1, all)
        
        player1.coll(coins, meteoriti, all, boom_sound, coin_sound)
        player2.coll(coins, meteoriti, all, boom_sound, coin_sound)

        # draw the scene
        dirty = all.draw(screen)
        #pg.draw.rect(screen, (255, 0, 0), player1.rect, width = 1)
        pg.display.update(dirty)

        if time.esci == True:
            pg.time.delay(3000)
            return



        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(40)



# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
