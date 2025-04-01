import sys
import pygame
from pygame.math import Vector2
import random

class Snake:
    def __init__(self,start_position,player_number):
        # self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self._initialize(start_position,player_number)
        self.new_block = False

        folder_path = f"../graphics/player{player_number}/"

        self.head_up = pygame.image.load(f'{folder_path}head_up.png').convert_alpha()
        self.head_down = pygame.image.load(f'{folder_path}head_down.png').convert_alpha()
        self.head_right = pygame.image.load(f'{folder_path}head_right.png').convert_alpha()
        self.head_left = pygame.image.load(f'{folder_path}head_left.png').convert_alpha()

        self.tail_up = pygame.image.load(f'{folder_path}tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load(f'{folder_path}tail_down.png').convert_alpha()
        self.tail_right = pygame.image.load(f'{folder_path}tail_right.png').convert_alpha()
        self.tail_left = pygame.image.load(f'{folder_path}tail_left.png').convert_alpha()

        self.body_vertical = pygame.image.load(f'{folder_path}body_vertical.png').convert_alpha()
        self.body_horizontal = pygame.image.load(f'{folder_path}body_horizontal.png').convert_alpha()
        
        self.body_tr = pygame.image.load(f'{folder_path}body_tr.png').convert_alpha()
        self.body_tl = pygame.image.load(f'{folder_path}body_tl.png').convert_alpha()
        self.body_br = pygame.image.load(f'{folder_path}body_br.png').convert_alpha()
        self.body_bl = pygame.image.load(f'{folder_path}body_bl.png').convert_alpha()

        self.crunch_sound = pygame.mixer.Sound('Sound/crunch.wav')

    def _initialize(self, start_position, player_number):
        if player_number == 1:
            self.body = [Vector2(start_position[0], start_position[1]),
                         Vector2(start_position[0] - 1, start_position[1]),
                         Vector2(start_position[0] - 2, start_position[1])]
            self.direction = Vector2(1, 0)  
        elif player_number == 2:
            self.body = [Vector2(start_position[0], start_position[1]),
                         Vector2(start_position[0] + 1, start_position[1]),
                         Vector2(start_position[0] + 2, start_position[1])]
            self.direction = Vector2(-1, 0)  

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()
        self.update_body_graphics()

        for index,block in enumerate(self.body):
            x_pos = block.x*cell_size
            y_pos = block.y*cell_size
            block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)

            if index == 0:
                screen.blit(self.head,block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail,block_rect)
            else:
                previous_block = self.body[index+1] - block
                next_block = self.body[index-1] - block
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical,block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal,block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x ==-1:    
                        screen.blit(self.body_tl,block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x ==-1:    
                        screen.blit(self.body_bl,block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x ==1:    
                        screen.blit(self.body_tr,block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x ==1:    
                        screen.blit(self.body_br,block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down
    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
        elif tail_relation == Vector2(0,1): self.tail = self.tail_up
        elif tail_relation == Vector2(0,-1): self.tail = self.tail_down
    def update_body_graphics(self):
        pass

    def move_snake(self):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0]+self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0]+self.direction)
            self.body = body_copy[:]
    def add_block(self):
        self.new_block = True
    def play_crunch_sound(self):
        self.crunch_sound.play()
    def reset(self,start_position,player_number):
        # self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self._initialize(start_position,player_number)

class Fruit:
    def __init__(self):
        self.x = random.randint(0,cell_number-1)
        self.y = random.randint(0,cell_number-1)
        self.pos = Vector2(self.x,self.y)
        # create x and y pos
        # draw squares 
    def draw_fruit(self):
        fruit_rect = pygame.Rect(self.pos.x*cell_size,self.pos.y*cell_size,cell_size,cell_size)
        screen.blit(apple,fruit_rect)
        # pygame.draw.rect(screen,(126,166,140),fruit_rect)
    def randomize(self):
        self.x = random.randint(0,cell_number-1)
        self.y = random.randint(0,cell_number-1)
        self.pos = Vector2(self.x,self.y)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font('Font/PoetsenOne-Regular.ttf', 25)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Main:
    def __init__(self):    
        self.snake = Snake(start_position=(3,10),player_number=1)
        self.snake2 = Snake(start_position=(22,10),player_number=2) 
        self.fruit = Fruit()
        self.game_state = 'start'

        # start button
        button_width, button_height = 200, 50
        button_x = (cell_number * cell_size - button_width) // 2
        button_y = (cell_number * cell_size - button_height) // 2
        self.start_button = Button(button_x, button_y, button_width, button_height, 
                                   'Start Game', (0, 255, 0), (0, 0, 0))
        
        # reset button
        self.reset_button = Button(button_x, button_y, button_width, button_height, 
                                   'Start Again', (255, 0, 0), (255, 255, 255))

        self.countdown = 4
        self.last_countdown_tick = None
    def update(self):
        if self.game_state == 'countdown':
            # Handle countdown timer
            current_time = pygame.time.get_ticks()
            if self.last_countdown_tick is None or current_time - self.last_countdown_tick >= 1000:
                self.countdown -= 1
                self.last_countdown_tick = current_time
                if self.countdown <= 0:
                    self.game_state = 'playing'
        elif self.game_state == 'playing':
            self.snake.move_snake() 
            self.snake2.move_snake()
            self.check_collition()
            self.check_fail()
    def draw_elements(self):
        self.draw_grass()
        if self.game_state == 'start':
            self.start_button.draw(screen)
        elif self.game_state == 'countdown':
            self.draw_countdown()
        elif self.game_state == 'playing':
            self.fruit.draw_fruit()
            self.snake.draw_snake()
            self.snake2.draw_snake()
        elif self.game_state == 'game_over':
            self.reset_button.draw(screen)
        # self.draw_score()
    def draw_countdown(self):
        countdown_text = game_font.render(str(self.countdown), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(cell_number * cell_size // 2, cell_number * cell_size // 2))
        screen.blit(countdown_text, countdown_rect)
    def check_collition(self):
        if self.fruit.pos == self.snake.body[0]:
            # print("snack")
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
        if self.fruit.pos == self.snake2.body[0]:
            # print("snack")
            self.fruit.randomize()
            self.snake2.add_block()
            self.snake2.play_crunch_sound()
        for block in self.snake2.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
    def check_fail(self):
        if not 0 <= self.snake.body[0].x<cell_number or not 0 <= self.snake.body[0].y<cell_number:
            self.game_over()
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()
        if not 0 <= self.snake2.body[0].x<cell_number or not 0 <= self.snake2.body[0].y<cell_number:
            self.game_over()
        for block in self.snake2.body[1:]:
            if block == self.snake2.body[0]:
                self.game_over()
        
        for block in self.snake2.body:
            if block == self.snake.body[0]:
                self.game_over()
        for block in self.snake.body:
            if block == self.snake2.body[0]:
                self.game_over()
        
    def game_over(self):
        self.game_state = 'game_over'
        # pygame.quit()
        # sys.exit()
    def reset_game(self):
        self.snake.reset(start_position=(3,10), player_number=1)
        self.snake2.reset(start_position=(22,10), player_number=2)
        self.fruit.randomize()
        self.start_countdown()

    def start_countdown(self):
        self.game_state = 'countdown'
        self.countdown = 4
        self.last_countdown_tick = None

    def draw_grass(self):
        grass_color = (167,209,61)
        for row in range(cell_number):
            if row % 2 == 0:   
                for col in range(cell_number):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col*cell_size,row*cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_color,grass_rect)
            else:
                for col in range(cell_number):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col*cell_size,row*cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_color,grass_rect)

    # def draw_score(self):
    #     score_text = str(len(self.snake.body) - 3)
    #     score_surface = game_font.render(score_text,True,(56,74,12))
    #     score_x = int(cell_size*cell_number-60)
    #     score_y = int(cell_size*cell_number-60)
    #     score_rect = score_surface.get_rect(center =(score_x,score_y))
    #     apple_rect = apple.get_rect(midright=(score_rect.left,score_rect.centery))
    #     bg_rect = pygame.Rect(apple_rect.left,apple_rect.top,apple_rect.width+score_rect.width +6,apple_rect.height)

    #     pygame.draw.rect(screen,(167,209,61),bg_rect)
    #     screen.blit(score_surface,score_rect)
    #     screen.blit(apple,apple_rect)
    #     pygame.draw.rect(screen,(56,74,12),bg_rect,2)
    

pygame.mixer.pre_init(44100,16,2,512)
pygame.init()
cell_size = 40
cell_number = 25
screen = pygame.display.set_mode((cell_number*cell_size,cell_number*cell_size))
clock = pygame.time.Clock()
apple = pygame.image.load('graphics/apple.png').convert_alpha()
game_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf',25)
# apple = pygame.transform.scale(apple, (cell_size, cell_size))

Screen_Update = pygame.USEREVENT
pygame.time.set_timer(Screen_Update,150)

main_game = Main()

while True:
    #Draw all Elements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if main_game.game_state == 'start':
                if main_game.start_button.is_clicked(event.pos):
                    main_game.start_countdown()
            elif main_game.game_state == 'game_over':
                if main_game.reset_button.is_clicked(event.pos):
                    main_game.reset_game()

        if main_game.game_state == 'playing':
            if event.type == Screen_Update:
                main_game.update()
            
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_UP:
                    if main_game.snake.direction.y != 1:
                        main_game.snake.direction = Vector2(0,-1)
                if event.key == pygame.K_DOWN:
                    if main_game.snake.direction.y != -1:
                        main_game.snake.direction = Vector2(0,1)
                if event.key == pygame.K_RIGHT:
                    if main_game.snake.direction.x != -1:
                        main_game.snake.direction = Vector2(1,0)
                if event.key == pygame.K_LEFT:
                    if main_game.snake.direction.x != 1:
                        main_game.snake.direction = Vector2(-1,0)

                
                if event.key == pygame.K_w:
                    if main_game.snake2.direction.y != 1:
                        main_game.snake2.direction = Vector2(0,-1)
                if event.key == pygame.K_s:
                    if main_game.snake2.direction.y != -1:
                        main_game.snake2.direction = Vector2(0,1)
                if event.key == pygame.K_d:
                    if main_game.snake2.direction.x != -1:
                        main_game.snake2.direction = Vector2(1,0)
                if event.key == pygame.K_a:
                    if main_game.snake2.direction.x != 1:
                        main_game.snake2.direction = Vector2(-1,0)

    if main_game.game_state in ['countdown']:
        main_game.update()

    screen.fill((175,215,70))
    if main_game.game_state == 'countdown':
        main_game.draw_grass()
        main_game.draw_countdown()
    else:
        main_game.draw_elements()
    pygame.display.update()
    clock.tick(60) # while loop wount run more than 60times a second

