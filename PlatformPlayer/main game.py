import pygame
import sys
import time
import random
import math
import json
pygame.init()
pygame.mixer.init()
FPS = 60
clock = pygame.time.Clock()
font_type = pygame.font.match_font('dejavusans')
special_font = pygame.font.Font(font_type, 32)
font = pygame.font.Font(None, 32)
click_sound = pygame.mixer.Sound('Mouse Click Sound Effect (256 kbps).mp3')
zawarudo_sound = pygame.mixer.Sound('zawarudo.mp3')
player_images = [
    pygame.transform.scale(pygame.image.load("Slime/walk1.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk2.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk3.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk4.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk5.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk6.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk7.png"), (30, 30)),
    pygame.transform.scale(pygame.image.load("Slime/walk8.png"), (30, 30)),
]

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 830

class Button:
    def __init__(self, screen, font, text, position, color, box_color, want_box):
        self.screen = screen
        self.font = font
        self.text = text
        self.vertical = position[0]
        self.horizontal = position[1]
        self.color = color
        self.box_color = box_color
        self.want_box = want_box

        self.size = self.font.size(self.text)
        self.pos = ((self.screen.get_width() - self.size[0]) / 2) + self.horizontal
        self.box = pygame.Rect(self.pos - 5, self.vertical, self.size[0] + 10, 50)

    def draw(self):
        if self.want_box:
            pygame.draw.rect(self.screen, self.box_color, self.box)
        self.draw_text()

    def draw_text(self):
        text_obj = self.font.render(self.text, True, self.color)
        text_rect = text_obj.get_rect()
        text_rect.center = (self.screen.get_width() // 2 + self.horizontal, self.vertical + 25)
        self.screen.blit(text_obj, text_rect)

    def collision(self):
        posx, posy = pygame.mouse.get_pos()
        if self.box.collidepoint((posx, posy)):
            click_sound.play
            return True

    def hovered(self):
        posx, posy = pygame.mouse.get_pos()
        if self.box.collidepoint((posx, posy)):
            self.box_color = (0, 0, 0)
        else:
            self.box_color = (60, 179, 113)

class Platform:
    def __init__(self, screen, color, rect):
        self.screen = screen
        self.color = color
        self.rect = rect

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)
        return image
    
class Player:
    def __init__(self, screen, color, rect):
        self.screen = screen
        self.color = color
        self.rect = rect
        self.vel_y = 0
        self.jump = False

        self.image = player_images
        self.current_frame = 0
        self.frame_cooldown = 10
    
    def draw(self):
        image = self.image[self.current_frame]
        if self.jump:
            image = pygame.transform.flip(image, False, True)

        self.screen.blit(image, self.rect)
        #pygame.draw.rect(self.screen, self.color, self.rect)

    def update(self, platforms, chosen_keys):

        if self.frame_cooldown >= 0:
            self.frame_cooldown = self.frame_cooldown - 1
        else:
            self.current_frame = (self.current_frame + 1) % len(self.image)
            self.frame_cooldown = 10

        keys = pygame.key.get_pressed()

        if keys[chosen_keys[1]] and self.rect.x > 0:
            self.rect.x -= 5
        if keys[chosen_keys[3]] and self.rect.x < SCREEN_WIDTH - self.rect.width:
            self.rect.x += 5
        if keys[chosen_keys[0]]:
            self.jump_action()

        if not self.jump:
            self.vel_y = 10

        self.rect.y += self.vel_y

        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.jump = False
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.vel_y = 0

        if keys[chosen_keys[2]]:
            self.jump = False
            self.rect.y += 5
        
        if self.jump:
            self.vel_y = -10

    def jump_action(self):
        if not self.jump:
            self.jump = True
            self.vel_y = -15

    def down_action(self):
        if self.jump:
            self.jump = False
            self.vel_y = 10

class Points:
    def __init__(self, screen, color, rect):
        self.screen = screen
        self.color = color
        self.rect = rect
        self.timer = int(time.time())
        self.collected = 0

    def draw(self,despawntime):
        if self.timer + despawntime/3 >= int(time.time()):
            pygame.draw.rect(self.screen, self.color, self.rect)
        elif self.timer + 2*(despawntime/3) >= int(time.time()):
            pygame.draw.rect(self.screen, "orange", self.rect)
        elif self.timer + despawntime >= int(time.time()):
            pygame.draw.rect(self.screen, "red", self.rect)
        else:
            self.move()

    def dodge(self):
        self.rect.x += 0.5
        if self.rect.x >= SCREEN_WIDTH:
            self.move()

    def move(self):
        self.rect.update(random.randint(10, SCREEN_WIDTH - 25), random.randint(10, SCREEN_HEIGHT - 25), 10, 10)
        self.timer = int(time.time())

class Enemy:
    def __init__(self, screen, image_path, rect):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))  # Adjust size as needed
        self.rect = rect
        self.speed = random.randint(1, 3)

    def draw(self):
        self.screen.blit(self.image, self.rect.topleft)

    def move(self, player_rect):
        distance_x = player_rect.centerx - self.rect.centerx
        distance_y = player_rect.centery - self.rect.centery

        distance = math.sqrt(distance_x**2 + distance_y**2)

        targetx = player_rect.centerx
        targety = player_rect.centery

        if targetx > self.rect.centerx:
            self.rect.move_ip(1 * self.speed, 0)
        if targetx < self.rect.centerx:
            self.rect.move_ip(-1 * self.speed, 0)
        if targety > self.rect.centery:
            self.rect.move_ip(0, 1 * self.speed)
        if targety < self.rect.centery:
            self.rect.move_ip(0, -1 * self.speed)

class Ability:
    def __init__(self, screen, image_path, rect):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))  # Adjust size as needed
        self.rect = rect
        self.speed = 6
        self.targetx = random.randint(25,SCREEN_WIDTH-25)
        self.targety = random.randint(25,SCREEN_HEIGHT-25)
        self.counter = 30

    def draw(self):
        self.screen.blit(self.image, self.rect.topleft)

    def move(self):

        if self.counter > 0:
            self.counter = self.counter - 1
        else:
            self.counter = 30
            self.targetx = random.randint(25,SCREEN_WIDTH-25)
            self.targety = random.randint(25,SCREEN_HEIGHT-25)

        targetx = self.targetx
        targety = self.targety

        if targetx > self.rect.centerx:
            self.rect.move_ip(1 * self.speed, 0)
        if targetx < self.rect.centerx:
            self.rect.move_ip(-1 * self.speed, 0)
        if targety > self.rect.centery:
            self.rect.move_ip(0, 1 * self.speed)
        if targety < self.rect.centery:
            self.rect.move_ip(0, -1 * self.speed)

class MainGame:
    def __init__(self):
        pygame.display.set_caption("Test")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.state = "StartScreen"
        self.click = False

        #images
        self.bg_image = pygame.image.load("bg.jpg").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.enemy_image = pygame.image.load("enemy.jpg").convert()
        self.enemy_image = pygame.transform.scale(self.enemy_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        #game settings 
        self.controls = [pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d]
        self.leaderboards = []
        self.finalscore = 0
        self.playername = ""

        #game constants
        self.starttime = int(time.time())
        self.score = 0
        self.player = Player(self.screen, (255, 0, 0), pygame.Rect(50, SCREEN_HEIGHT - 50, 30, 30))
        self.points = Points(self.screen, "green", pygame.Rect(random.randint(10, SCREEN_WIDTH - 25),
                                                                random.randint(10, SCREEN_HEIGHT - 25), 10, 10))
        self.enemies = []
        self.abilities = []

        #abilities
        self.ability_active = ""
        self.ability_time = 1
        self.ability_timer = 0
        
        #map difficulty
        self.difficulty = 0
        self.platforms = []
        self.points_needed = 0
        self.points_despawn_time = 0
        self.spawn_rate = 0

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.jump_action()

            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.player.down_action()

            if event.type == pygame.KEYDOWN and self.state == "GameWin":
                if event.key == pygame.K_BACKSPACE:
                    self.playername = self.playername[0:-1]
                else:
                    self.playername = self.playername + event.unicode

    def start_screen(self):
        start_button = Button(self.screen, font, "Start Game", (175, 0), (255, 255, 255), (60, 179, 113), True)

        start_button.hovered()
        start_button.draw()

        if self.click:
            if start_button.collision():
                self.state = "Menu"
            self.click = False

    def menu(self):
        level_button = Button(self.screen, font, "Level Select", (75, 0), (255, 255, 255), (60, 179, 113), True)
        settings_button = Button(self.screen, font, "Settings", (175, 0), (255, 255, 255), (60, 179, 113), True)
        leaderboard_button = Button(self.screen, font, "Leaderboard", (280, 0), (255, 255, 255), (60, 179, 113), True)

        level_button.hovered()
        settings_button.hovered()
        leaderboard_button.hovered()

        level_button.draw()
        settings_button.draw()
        leaderboard_button.draw()

        if self.click:
            if level_button.collision():
                self.state = "LevelSelect"
            elif settings_button.collision():
                self.state = "Settings"
            elif leaderboard_button.collision():
                self.state = "Leaderboard"
                self.load_leaderboard()
            self.click = False

    def settings(self):
        display = Button(self.screen, font, "Settings", (20, 0), (255, 255, 255), (60, 179, 113), True)
        display.draw()

        wasd_w = Button(self.screen, font, "W", (100, -200), (255, 255, 255), (60, 179, 113), True)
        wasd_a = Button(self.screen, font, "A", (160, -240), (255, 255, 255), (60, 179, 113), True)
        wasd_s = Button(self.screen, font, "S", (160, -200), (255, 255, 255), (60, 179, 113), True)
        wasd_d = Button(self.screen, font, "D", (160, -160), (255, 255, 255), (60, 179, 113), True)

        uldr_u = Button(self.screen, special_font, "↑", (100, 0), (255, 255, 255), (60, 179, 113), True)
        uldr_l = Button(self.screen, special_font, "←", (160, -40), (255, 255, 255), (60, 179, 113), True)
        uldr_d = Button(self.screen, special_font, "↓", (160, 0), (255, 255, 255), (60, 179, 113), True)
        uldr_r = Button(self.screen, special_font, "→", (160, 40), (255, 255, 255), (60, 179, 113), True)

        tfgh_t = Button(self.screen, font, "T", (100, 200), (255, 255, 255), (60, 179, 113), True)
        tfgh_f = Button(self.screen, font, "F", (160, 160), (255, 255, 255), (60, 179, 113), True)
        tfgh_g = Button(self.screen, font, "G", (160, 200), (255, 255, 255), (60, 179, 113), True)
        tfgh_h = Button(self.screen, font, "H", (160, 240), (255, 255, 255), (60, 179, 113), True)

        draw_keys = [wasd_w, wasd_a, wasd_s, wasd_d, uldr_u, uldr_l, uldr_d, uldr_r, tfgh_t, tfgh_f, tfgh_g, tfgh_h]
        for key in draw_keys:
            key.draw()

        wasd = Button(self.screen, font, "  Select  ", (220, -200), (255, 255, 255), (60, 179, 113), True)
        uldr = Button(self.screen, font, "  Select  ", (220, 0), (255, 255, 255), (60, 179, 113), True)
        tfgh = Button(self.screen, font, "  Select  ", (220, 200), (255, 255, 255), (60, 179, 113), True)

        wasd.hovered()
        uldr.hovered()
        tfgh.hovered()

        if self.controls == [pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d]:
            wasd.text = "Selected"
            wasd.box_color = (45, 144, 255)
        elif self.controls == [pygame.K_UP,pygame.K_LEFT,pygame.K_DOWN,pygame.K_RIGHT]:
            uldr.text = "Selected"
            uldr.box_color = (45, 144, 255)
        elif self.controls == [pygame.K_t,pygame.K_f,pygame.K_g,pygame.K_h]:
            tfgh.text = "Selected"
            tfgh.box_color = (45, 144, 255)

        wasd.draw()
        uldr.draw()
        tfgh.draw()

        back_button = Button(self.screen, font, "Back", (375, 0), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        if self.click:
            if back_button.collision():
                self.state = "Menu"
            elif wasd.collision():
                self.controls = [pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d]
            elif uldr.collision():
                self.controls = [pygame.K_UP,pygame.K_LEFT,pygame.K_DOWN,pygame.K_RIGHT]
            elif tfgh.collision():
                self.controls = [pygame.K_t,pygame.K_f,pygame.K_g,pygame.K_h]
            self.click = False

    def leaderboard(self):
        display = Button(self.screen, font, "Leaderboard", (20, 0), (255, 255, 255), (60, 179, 113), True)
        display.draw()

        level1 = Button(self.screen, font, "Level 1", (100, -200), (255, 255, 255), (60, 179, 113), True)
        level1.draw()
        level2 = Button(self.screen, font, "Level 2", (100, 0), (255, 255, 255), (60, 179, 113), True)
        level2.draw()
        level3 = Button(self.screen, font, "Level 3", (100, 200), (255, 255, 255), (60, 179, 113), True)
        level3.draw()

        for x in range (0,5):
            level1_top = f"{self.leaderboards['lvl1'][x][0]}: {self.leaderboards['lvl1'][x][1]}" 
            level1 = Button(self.screen, font, level1_top, (100+(60*(x+1)), -200), (0, 0, 0), (60, 179, 113), False)
            level1.draw()

            level2_top = f"{self.leaderboards['lvl2'][x][0]}: {self.leaderboards['lvl2'][x][1]}" 
            level2 = Button(self.screen, font, level2_top, (100+(60*(x+1)), 0), (0, 0, 0), (60, 179, 113), False)
            level2.draw()
        
            level3_top = f"{self.leaderboards['lvl3'][x][0]}: {self.leaderboards['lvl3'][x][1]}" 
            level3 = Button(self.screen, font, level3_top, (100+(60*(x+1)), 200), (0, 0, 0), (60, 179, 113), False)
            level3.draw()

        back_button = Button(self.screen, font, "Back", (750, 0), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        if self.click:
            if back_button.collision():
                self.state = "Menu"
            self.click = False

    def load_leaderboard(self):
        file = open("PlatformPlayer/score.json","r")
        data = file.readlines()
        file.close()

        self.leaderboards = json.loads(data[0])

    def save_leaderboard(self):
        self.load_leaderboard()

        insert = [self.playername, self.finalscore]
        main = []
        temp = []

        for person in self.leaderboards[self.difficulty]:
            if person[1] <= insert[1]:
                main.append(person)
            else:
                temp.append(person)

        main.append(insert)
        main = main + temp

        self.leaderboards[self.difficulty] = main

        with open("PlatformPlayer/score.json", "w") as file:
            json.dump(self.leaderboards, file)

    def level_select(self):
        self.screen.fill((255, 255, 255))

        level1_button = Button(self.screen, font, "Level 1", (75, 0), (255, 255, 255), (60, 179, 113), True)
        level2_button = Button(self.screen, font, "Level 2", (175, 0), (255, 255, 255), (60, 179, 113), True)
        level3_button = Button(self.screen, font, "Level 3", (275, 0), (255, 255, 255), (60, 179, 113), True)

        level1_button.hovered()
        level2_button.hovered()
        level3_button.hovered()

        level1_button.draw()
        level2_button.draw()
        level3_button.draw()

        back_button = Button(self.screen, font, "Back", (375, 0), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        level1_map = [
            Platform(self.screen, (0, 0, 255), pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(300, SCREEN_HEIGHT - 150, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(100, SCREEN_HEIGHT - 300, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(500, SCREEN_HEIGHT - 250, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(700, SCREEN_HEIGHT - 100, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(900, SCREEN_HEIGHT - 200, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(200, SCREEN_HEIGHT - 400, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(400, SCREEN_HEIGHT - 550, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(600, SCREEN_HEIGHT - 700, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(800, SCREEN_HEIGHT - 300, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1000, SCREEN_HEIGHT - 450, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1200, SCREEN_HEIGHT - 600, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(200, SCREEN_HEIGHT - 800, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(400, SCREEN_HEIGHT - 950, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(600, SCREEN_HEIGHT - 1100, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(800, SCREEN_HEIGHT - 500, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1000, SCREEN_HEIGHT - 650, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1200, SCREEN_HEIGHT - 800, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(200, SCREEN_HEIGHT - 1000, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(400, SCREEN_HEIGHT - 1150, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(600, SCREEN_HEIGHT - 1300, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(800, SCREEN_HEIGHT - 700, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1000, SCREEN_HEIGHT - 850, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1200, SCREEN_HEIGHT - 1000, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(200, SCREEN_HEIGHT - 1200, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(400, SCREEN_HEIGHT - 1350, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(600, SCREEN_HEIGHT - 1500, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(800, SCREEN_HEIGHT - 1100, 200, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1000, SCREEN_HEIGHT - 1250, 150, 10)),
            Platform(self.screen, (0, 0, 255), pygame.Rect(1200, SCREEN_HEIGHT - 1400, 200, 10)),
        ]

        #to be made if time 
        level2_map = []
        level3_map = []

        # [0] = points needed to win - [1] = speed points despawn at - [2] = enemy per points
        level1_config = [15,9,4]
        level2_config = [30,6,2]
        level3_config = [50,3,1]

        if self.click:
            if back_button.collision():
                self.state = "Menu"
            if level1_button.collision() or level2_button.collision() or level3_button.collision():
                #resets time and points
                self.starttime = int(time.time())
                self.points.collected = 0

                #resets enemies
                self.enemies = []

                #resets abilities
                self.abilities = []
                self.ability_active = ""
                self.ability_time = 1
                self.ability_timer = 0

                #reset player positions
                self.player.jump = False
                self.player.rect.update(50, SCREEN_HEIGHT - 50, 30, 30)

            if level1_button.collision():
                self.difficulty = "lvl1"
                self.platforms = level1_map
                self.points_needed = level1_config[0]
                self.points_despawn_time = level1_config[1]
                self.spawn_rate = level1_config[2]
                self.state = "Game"
            elif level2_button.collision():
                self.difficulty = "lvl2"
                self.platforms = level1_map
                self.points_needed = level2_config[0]
                self.points_despawn_time = level2_config[1]
                self.spawn_rate = level2_config[2]
                self.state = "Game"
            elif level3_button.collision():
                self.difficulty = "lvl3"
                self.platforms = level1_map
                self.points_needed = level3_config[0]
                self.points_despawn_time = level3_config[1]
                self.spawn_rate = level3_config[2]
                self.state = "Game"
            self.click = False

    def game(self):
        self.screen.blit(self.bg_image, (0, 0))
        gametime = int(time.time()) - self.starttime

        level_display = Button(self.screen, font, f"Level:{self.difficulty}", (1, -640), (255, 255, 255), (60, 179, 113), True)
        level_display.draw()

        time_display = Button(self.screen, font, f"Time:{gametime}", (1, -530), (255, 255, 255), (60, 179, 113), True)
        time_display.draw()

        collect_display = Button(self.screen, font, f"Collected:{self.points.collected}/{self.points_needed}", (1, -395),
                                 (255, 255, 255), (60, 179, 113), True)
        collect_display.draw()
        
        #ability display and bar
        timeleft = 0
        if self.ability_active != "":
            timeleft = self.ability_timer - (time.time()) 


        abilitybar_outline = pygame.Rect(400, 1, 600, 50)
        pygame.draw.rect(self.screen, (60, 179, 113), abilitybar_outline)

        abilitybar = pygame.Rect(402, 3, timeleft*(596/self.ability_time), 46)
        pygame.draw.rect(self.screen, (45, 144, 255), abilitybar)

        if timeleft <= 0:
            self.ability_active = ""

        phrase = ""
        if self.ability_active == "":
            phrase = "No ability active"
        else:
            phrase = "currently active"

        ability_display = Button(self.screen, font, f"{self.ability_active} {phrase}", (1, -120), (255, 255, 255), (60, 179, 113), False)
        ability_display.draw()

        back_button = Button(self.screen, font, "Back", (1, 500), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        self.player.update(self.platforms, self.controls)
        self.player.draw()

        #pygame.draw.circle(self.screen, ("blue"), [self.player.rect.centerx,self.player.rect.centery], 100, width=5)

        if self.ability_active == "bigcoins":
            self.points.rect.update(self.points.rect.topleft[0], self.points.rect.topleft[1], 20, 20)

        self.points.draw(self.points_despawn_time)
        self.points.dodge()

        #checks if the player has collected a point
        if self.player.rect.colliderect(self.points.rect):
            self.points.collected += 1
            self.points.move()

        #draws all the platforms
        for platform in self.platforms:
            platform.draw()

        #spawns the enemies
        if self.points.collected % self.spawn_rate == 0 and len(self.enemies) < self.points.collected // self.spawn_rate:
            enemy_x = random.randint(10, SCREEN_WIDTH - 25)
            enemy_y = random.randint(10, SCREEN_HEIGHT - 25)
            distance_x = self.player.rect.centerx - enemy_x
            distance_y = self.player.rect.centery - enemy_y
            distance = math.sqrt(distance_x**2 + distance_y**2)

            while distance <= 500:
                enemy_x = random.randint(10, SCREEN_WIDTH - 25)
                enemy_y = random.randint(10, SCREEN_HEIGHT - 25)
                distance_x = self.player.rect.centerx - enemy_x
                distance_y = self.player.rect.centery - enemy_y
                distance = math.sqrt(distance_x**2 + distance_y**2)

            new_enemy = Enemy(self.screen, "enemy.jpg",pygame.Rect(enemy_x, enemy_y, 30, 30))
            self.enemies.append(new_enemy)

        #handles enemies and death
        for enemy in self.enemies:
            enemy.draw()

            for enemy1 in self.enemies:
                if enemy != enemy1:
                    if enemy.rect.colliderect(enemy1.rect):
                        enemy.rect.y = enemy.rect.y - 15
                        enemy.rect.x = enemy.rect.x - 15

                        enemy1.rect.y = enemy1.rect.y + 15
                        enemy1.rect.x = enemy1.rect.x + 15


            if self.ability_active != "freeze":
                zawarudo_sound.play()
                enemy.move(self.player.rect)

            if self.player.rect.colliderect(enemy.rect) and self.ability_active != "invincibility":
                self.state = "GameOver"

            if self.ability_active == "gravity":
                if enemy.rect.y <= SCREEN_HEIGHT - 40:
                    enemy.rect.y = enemy.rect.y + 5
        

        if random.randint(1,2500) == 1 and self.ability_active == "" and self.abilities == []:
            new_ability = Ability(self.screen, "ability.png",pygame.Rect(random.randint(10, SCREEN_WIDTH - 25), 
                                                                    random.randint(10, SCREEN_HEIGHT - 25),30, 30))
            self.abilities.append(new_ability)
            
        #handles abilities
        for ability in self.abilities:
            ability.draw()
            ability.move()

            if self.player.rect.colliderect(ability.rect):
                self.abilities = []
                randomability = random.choice(["freeze","gravity","invincibility","bigcoins"])
                self.ability_active = randomability
                self.ability_time = random.randint(5,15)
                self.ability_timer = int(time.time()) + self.ability_time

        #checks if player has won
        if self.points.collected >= self.points_needed:
            self.state = "GameWin"
            self.finalscore = gametime

        if self.click:
            if back_button.collision():
                self.state = "Menu"
            self.click = False

    def game_win(self):
        
        display = Button(self.screen, font, f"You won ! Your score was {self.finalscore}", (20, 0), (255, 255, 255), (60, 179, 113), True)
        display.draw()

        prompt = Button(self.screen, font, "Enter your name", (160, 0), (255, 255, 255), (60, 179, 113), True)
        prompt.draw()

        name = Button(self.screen, font, f"Name: {self.playername}", (220, 0), (255, 255, 255), (60, 179, 113), True)
        name.draw()

        back_button = Button(self.screen, font, "Back", (750, 0), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        if self.click:
            if back_button.collision():
                if self.playername != "":
                    self.save_leaderboard()
                self.state = "Menu"
            self.click = False

    def game_over(self):

        self.screen.blit(self.enemy_image, (0, 0))

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        game_over_label = Button(self.screen, font, "Game Over", (center_x - 50, center_y),('white'), (175, 0), False)
        game_over_label.draw()

        back_button = Button(self.screen, font, "Back", (1, -350), (255, 255, 255), (60, 179, 113), True)
        back_button.hovered()
        back_button.draw()

        if self.click:
            if back_button.collision():
                self.state = "Menu"
            self.click = False

def GameMenu():
    run = True
    Game = MainGame()

    while run:
        Game.events()
        Game.screen.fill((255, 255, 255))

        if Game.state == "StartScreen":
            Game.start_screen()
        elif Game.state == "Menu":
            Game.menu()
        elif Game.state == "Settings":
            Game.settings()
        elif Game.state == "Leaderboard":
            Game.leaderboard()
        elif Game.state == "LevelSelect":
            Game.level_select()
        elif Game.state == "Game":
            Game.game()
        elif Game.state == "GameWin":
            Game.game_win()
        elif Game.state == "GameOver":
            Game.game_over()

        clock.tick(FPS)
        pygame.display.update()

GameMenu()