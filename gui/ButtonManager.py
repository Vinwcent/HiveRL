import pygame as pg
import pygame.image as image
import pygame.sprite as sprite

from gui.PieceSprite import PieceSprite

class ButtonSprite(PieceSprite):
    def __init__(self, bug_name):
        super(ButtonSprite, self).__init__(background_int=1,
                                           bug_name=bug_name)
        self.bug_name = bug_name

    def get_size(self):
        width = self.surf.get_rect()[2]
        height = self.surf.get_rect()[3]
        return (width, height)

class ButtonManager(pg.sprite.Sprite):

    def __init__(self, screen_size):
        super(ButtonManager, self).__init__()
        self.surf = pg.Surface((int(screen_size[0]),
                                int(0.2*screen_size[1])))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        # Put the manager below
        self.rect[1] = int(0.8*screen_size[1])

        self.buttons = sprite.Group()


    def init_buttons(self):
        self.bee_button = ButtonSprite(bug_name="bee")
        self.spider_button = ButtonSprite(bug_name="spider")
        self.ant_button = ButtonSprite(bug_name="ant")
        self.beetle_button = ButtonSprite(bug_name="beetle")
        self.grasshopper_button = ButtonSprite(bug_name="grasshopper")

        self.buttons.add(self.bee_button)
        self.buttons.add(self.spider_button)
        self.buttons.add(self.ant_button)
        self.buttons.add(self.beetle_button)
        self.buttons.add(self.grasshopper_button)

        self.button_width, self.button_height = self.bee_button.get_size()

        for count, button in enumerate(self.buttons):
            location = ((count+1)*self.rect[2]/6 - self.button_width/2,
                        self.rect[3]/2 - self.button_height/2)
            button.rect[0:2] = location



    def _draw_buttons(self):
        for count, button in enumerate(self.buttons):
            self.surf.blit(button.surf, button.rect)


    def update(self):
        self._draw_buttons()
