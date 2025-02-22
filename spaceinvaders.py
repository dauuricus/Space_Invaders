#!/usr/bin/env python

# Space Invaders
# Created by Lee Robinson
# MOD BY haywhnk

from pygame import *
import sys
from os.path import abspath, dirname
from random import choice
from operator import itemgetter, attrgetter
# ファイルへのpath
BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + '/fonts/'
IMAGE_PATH = BASE_PATH + '/images/'
SOUND_PATH =  BASE_PATH + '/sounds/'

# RGB値を変数 WHITE,GREEN,YELLOW,BLUE,PURPLE,REDへ用意する
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)
# スクリーンのサイズをpygame.Surfaceオブジェクトとして渡す
SCREEN = display.set_mode((800, 600),SCALED)
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship','shipexplosion1','shipexplosion2','shipexplosion3','mystery',
            'enemy1_1','enemy1_2',
            'enemy2_1','enemy2_2',
            'enemy3_1','enemy3_2',
            'explosionblue','explosiongreen','explosionpurple',
            'laser','laser1','enemylaser','enemylaser1']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
        for name in IMG_NAMES}
# ポジション初期値
BLOCKERS_POSITION = 450 # トーチカ
ENEMY_DEFAULT_POSITION = 65 # ゲームスタートの時のエイリアンの高さ
ENEMY_MOVE_DOWN = 35 # エイリアンの近づいてくる高さの単位

ROUND_NUM = 0 #
SHIP_VX = 10
ROW_counter = 4
LEVEL = 700

# クラス定義
class Ship(sprite.Sprite): # playerのアイコン
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image,(50,50))
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.dist_x = self.rect.x
        self.speed = 1
        self.vx = SHIP_VX

    def update(self, keys, *args): # 画面左右playerが動ける範囲
        if keys[K_a] and self.rect.x > 10:
            # self.rect.x -= self.speed # 左移動
            self.vx += self.speed
            self.dist_x = (self.rect.x - self.vx)
            self.rect.x += (-(-(self.dist_x - self.rect.x))//3)
            if self.rect.x < 10: # 画面左端まできたら止まる
                self.rect.x = 10
            # キーアップで速度vxをSHIP_VXに戻す check_input()
        if keys[K_d] and self.rect.x < 740:
            # self.rect.x += self.speed # 右移動
            self.vx += self.speed
            self.dist_x = (self.rect.x + self.vx)
            self.rect.x += (-(-(self.dist_x - self.rect.x))//3)
            if self.rect.x > 740: # 画面右端まできたら止まる
                self.rect.x = 740
            # キーアップで速度vxをSHIP_VXに戻す　check_input()
        game.screen.blit(self.image, self.rect) # Surfaceオブジェクトにblit

class Bullet(sprite.Sprite): # 弾
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.image2 = IMAGES[filename + '1']
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename
        self.timer = time.get_ticks()

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        current_time = time.get_ticks()

        
        if self.rect.y < 35:            
            self.rect.y = 35
            game.screen.blit(self.image2, self.rect)
            if current_time > self.timer + 700:
                self.kill() # 画面の上部で弾の表示を消す
                
        if self.rect.y > 585:            
            self.rect.y = 580
            game.screen.blit(self.image2, self.rect)
            if current_time > self.timer + 160:
                self.kill() # 画面の下部で弾の表示を消す

                
# 弾の変化
class bulletExplosion(sprite.Sprite):
    def __init__(self, enemylaser, *groups):
        super(bulletExplosion, self).__init__(*groups)
        self.image = IMAGES['enemylaser1']
        self.rect = self.image.get_rect(topleft=(enemylaser.rect.x, enemylaser.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 300:
           game.screen.blit(self.image, self.rect)
        elif 300 < passed:
           self.kill()


class Enemy(sprite.Sprite): # 敵キャラクター
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.moveTime = 200
        self.timeOffset = row * (-50) + column * 120
        self.timer = time.get_ticks() + self.timeOffset
        global LEVEL
        LEVEL = 700
    #アニメーション
    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        current_time = time.get_ticks()
        if current_time - self.timer > self.moveTime:
            game.screen.blit(self.image, self.rect)
        #self.timer += self.moveTime
        
    def load_images(self):
        images = {0:['1_2', '1_1'],1:['2_2', '2_1'],2:['2_2', '2_1'],3:['3_1', '3_2'],4:['3_1', '3_2']}
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in images[self.row])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))


class EnemiesGroup(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 200
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        # ラウンドが上がると敵が下へ降りてくる
        self.timeOffset = 22000 * ROUND_NUM
        self.timer = time.get_ticks() - self.timeOffset
        self.speedup = 0
        #self.timer = time.get_ticks()
        self.bottom = game.enemyPosition + ((rows - 1) * 45) +35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1
        self.minRow = 0
        self.maxRow = 4

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove

            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                global ROW_counter
                
                s = sorted(self, key=attrgetter('row'),reverse=True)
                for enemy in s:
                #for enemy in self:
                    
                    if len(self) <= 4: # skip check when 4 enemies
                        enemy.rect.x += velocity
                        enemy.toggle_image()
                        continue # goto loop start
                    
                    row_i = enemy.row
                    
                    if row_i == ROW_counter:
                        enemy.rect.x += velocity
                        enemy.toggle_image()
                        
                    else:
                        continue
                
                if len(self) <= 4:
                    self.moveNumber += 1    
                else:
                    ROW_counter -= 1
                    if ROW_counter == self.minRow -1:
                        ROW_counter = self.maxRow
                        self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                        for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                        for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        # 敵の数が減れば段階的にスピードアップする
        global LEVEL
        minimum = 5
        maxmum = 0
        for l in self:
            compRow = l.row    
            if compRow < minimum:
                minimum = compRow            
            if compRow > maxmum:
                maxmum = compRow
            self.minRow = minimum
            self.maxRow = maxmum

        if len(self) == 1: # 敵の数が１になれば、敵の動きがすごく速くなる
            self.moveTime = 2
            LEVEL = 350
#=============================================================================
        elif len(self) ==  2:
            self.moveTime = 40
        elif len(self) ==  3:
            self.moveTime = 60
        elif len(self) ==  4:
             self.moveTime = 60
        elif len(self) <=  10:
             self.moveTime = 40
        elif len(self) <=  15:
             self.moveTime = 80
        elif len(self) <= 20:
             self.moveTime = 90
        elif len(self) <= 30: # 敵の数が30になれば、敵の動きが速くなる↑
             self.moveTime = 100
        elif len(self) <= 40: # 敵の数が40になれば、敵の動きが速くなる↑
             self.moveTime = 110
             LEVEL = 400
#=============================================================================

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)

        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)


class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, (80, 40))
        self.rect = self.image.get_rect(topleft=(-80, 25))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.1)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        if self.rect.x > 830:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime


class EnemyExplosion(sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), (40, 35))
        self.image2 = transform.scale(self.get_image(enemy.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
           game.screen.blit(self.image, self.rect)
        elif passed <= 200:
           game.screen.blit(self.image2, (self.rect.x -6, self.rect.y -6))
        elif 400 < passed:
           self.kill()


class MysteryExplosion(sprite.Sprite):
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE, mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['shipexplosion1']
        self.image2 = IMAGES['shipexplosion2']
        self.image3 = IMAGES['shipexplosion3']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif 100 < passed <= 200:
            game.screen.blit(self.image2, self.rect)
        elif 200< passed <= 300:
            game.screen.blit(self.image3, self.rect)
        elif 300 < passed <= 400:
            game.screen.blit(self.image2, self.rect)
        elif 400 < passed <= 500:
            game.screen.blit(self.image, self.rect)
        elif 500 < passed <= 600:
            game.screen.blit(self.image3, self.rect)
        elif 600 < passed <= 700:
            game.screen.blit(self.image2, self.rect)
        elif 700 < passed <= 800:
            game.screen.blit(self.image3, self.rect)
        elif 800 < passed:
            self.kill()


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
    def __init__(self):

        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False

        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'Space Invaders', WHITE, 164, 155)
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE, 201, 225)
        self.gameOverText = Text(FONT, 50, 'Game Over', RED, 250, 270)
        self.gameOverText0 = Text(FONT, 50, 'G', RED, 250, 270)
        self.gameOverText1 = Text(FONT, 50, 'Ga', RED, 250, 270)
        self.gameOverText2 = Text(FONT, 50, 'Gam', RED, 250, 270)
        self.gameOverText3 = Text(FONT, 50, 'Game', RED, 250, 270)
        self.gameOverText4 = Text(FONT, 50, 'Game O', RED, 250, 270)
        self.gameOverText5 = Text(FONT, 50, 'Game Ov', RED, 250, 270)
        self.gameOverText6 = Text(FONT, 50, 'Game Ove', RED, 250, 270)
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 240, 270)
        self.enemy1Text = Text(FONT, 25, '   =   10 pts', GREEN, 368, 270)
        self.enemy2Text = Text(FONT, 25, '   =   20 pts', BLUE, 368, 320)
        self.enemy3Text = Text(FONT, 25, '   =   30 pts', PURPLE, 368, 370)
        self.enemy4Text = Text(FONT, 25, '   =   ?????', RED, 368, 420)
        self.scoreText = Text(FONT, 20,'Score', WHITE, 5, 5)
        self.livesText = Text(FONT, 20,'Lives', WHITE, 640, 5)


        self.life1 = Life(715, 3)
        self.life2 = Life(742, 3)
        self.life3 = Life(769, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.player, self.enemies, self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers1(self, number):
        barrierDesign = [[],
                         [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                         [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                         [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                         [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1],
                         [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
                         [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
                         [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
                         ]
        blockerGroup = sprite.Group()
        row = 0
        for b in barrierDesign:
            column = 0
            for b in b:
                if b != 0:
                    blocker = Blocker(3, RED, row, column)
                    blocker.rect.x = 60 + (200 * number) + (column * blocker.width)
                    blocker.rect.y = BLOCKERS_POSITION +25+ (row * (blocker.height))
                    blockerGroup.add(blocker)
                column += 1
            row += 1
        # ground
        for x in range(200):
            blocker = Blocker(4, RED, row, column)
            blocker.rect.x = x * blocker.width 
            blocker.rect.y = 595
            blockerGroup.add(blocker)
            column += 1
            row += 1
        return blockerGroup

    #def make_blockers(self, number):
    #    blockerGroup = sprite.Group()
    #    for row in range(4):
    #        for column in range(9):
    #            blocker = Blocker(10, RED, row, column)
    #            blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
    #            blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
    #            blockerGroup.add(blocker)
    #    return blockerGroup
    
    def set4Blocker(self):
        # トーチカ(blockers)を4つ作る
        self.allBlockers = sprite.Group(self.make_blockers1(0),# left end 
                                        self.make_blockers1(1),# second from left
                                        self.make_blockers1(2),# third from left
                                        self.make_blockers1(3) # right end
                                        )


    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot','shoot2','invaderkilled', 'mysterykilled','shipexplosion']:
            self.sounds[sound_name] = mixer.Sound(SOUND_PATH + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.1)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.1)
        

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime *3:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime * 3

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:                	
                if e.key == K_s:
                    if len(self.bullets) == 0 and self.shipAlive:
                        if self.score <= 1990: # 点数が1500点まで
                            bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot'].play()
                            
                        elif 1990 <= self.score < 3500 : # 点数が1500点以に達すると弾が2つづつ発射できる
                            leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot2'].play()
                                
                        elif 3500 <= self.score : 
                            bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, 'laser', 'center')
                            self.bullets.add(bullet)
                            leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot2'].play()
                    
                    if ROUND_NUM >= 6 and self.shipAlive:
                        bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, 'laser', 'center')
                        self.bullets.add(bullet)
                        leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, 'laser', 'left')
                        rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, 'laser', 'right')
                        self.bullets.add(leftbullet)
                        self.bullets.add(rightbullet)
                        self.allSprites.add(self.bullets)
                        self.sounds['shoot2'].play()
                        
            if e.type == KEYUP:
                if e.key == K_d or K_a:# キーアップでplayerの横移動の加速速度vxを初期値に戻す
                    self.player.vx = SHIP_VX


    def make_enemies(self):
        enemies = EnemiesGroup(10, 5)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = 157 + (column * 50)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self):
        if (time.get_ticks() - self.timer) > LEVEL and self.enemies:
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5, 'enemylaser', 'center'))
            self.allSprites.add(self.enemyBullets)
            self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30, 1: 20,2: 20, 3: 10, 4: 10, 5: choice([50, 100, 150, 300])}
        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGES['enemy3_1']
        self.enemy1 = transform.scale(self.enemy1, (40, 40))
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.screen.blit(self.enemy1, (318, 270))
        self.screen.blit(self.enemy2, (318, 320))
        self.screen.blit(self.enemy3, (318, 370))
        self.screen.blit(self.enemy4, (299, 420))

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets, True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets, True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets, True, True).keys():
            self.sounds['shipexplosion'].play()
            ShipExplosion(player, self.explosionsGroup)
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
            	self.gameOver = True
            	self.startGame = False
            
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False
            
        if self.enemies.bottom >= 540:
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)

            if not self.player.alive() or self.enemies.bottom >= 600:
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        
        bullet = sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        for enemylaser in bullet.keys():
            bulletExplosion(enemylaser, self.explosionsGroup)
            
        if self.enemies.bottom >= BLOCKERS_POSITION:
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 1600):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime):
        
        # ゲームオーバーの文字を点滅
        passed = currentTime - self.timer        	
        if 900 < passed < 1000:
        	self.gameOverText0.draw(self.screen)
        elif 1000 < passed < 1100:
            self.gameOverText1.draw(self.screen)
        elif 1100 < passed < 1200:
            self.gameOverText2.draw(self.screen)
        elif 1200 < passed < 1300:
            self.gameOverText3.draw(self.screen)
        elif 1300 < passed < 1400:
            self.gameOverText4.draw(self.screen)
        elif 1500 < passed < 1600:
            self.gameOverText5.draw(self.screen)
            #self.screen.blit(self.background, (0, 0))
        elif 1600 < passed < 1700:
            self.gameOverText6.draw(self.screen)
        elif 1700 < passed < 1800:
            self.gameOverText.draw(self.screen)
        elif passed > 4000:
            self.mainScreen = True # メイン画面へ

        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)

                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        # 最初のゲームスタート
                        # トーチカ(blockers)を作る
                       # self.allBlockers = sprite.Group(self.make_blockers1(0),# left end 
                       #                                 self.make_blockers1(1),# second from left
                       #                                 self.make_blockers1(2),# third from left
                       #                                 self.make_blockers1(3) # right end
                       #                                 )
                        self.set4Blocker() # トーチカ(blockers)を作る

                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            elif self.startGame:
                if not self.enemies and not self.explosionsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        global ROUND_NUM
                        self.roundText = Text(FONT, 50, str(ROUND_NUM + 2), WHITE, 390, 350)
                        self.roundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # nextRound
                        ROUND_NUM += 1
                        # トーチカ(blockers)を作る
                        self.set4Blocker()                        

                        # move eneies closer to bottom
                        self.enemyPosition = ENEMY_DEFAULT_POSITION #+= ENEMY_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.roundText = Text(FONT, 20, 'Round ' + str(ROUND_NUM + 1), WHITE, 325, 5)
                    self.roundText.draw(self.screen)
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.enemies.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.check_collisions()
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.make_enemies_shoot()

            elif self.gameOver:
                currentTime = time.get_ticks()
                # Reset enemy starting position
                self.enemyPosition = ENEMY_DEFAULT_POSITION
                self.create_game_over(currentTime)
                ROUND_NUM = 0
            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()
