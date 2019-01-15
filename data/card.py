import pygame as pg


class Card:
    def __init__(self, path, image, screen_rect=None):
        if screen_rect:
            image_rect = image.get_rect()
            card_aspect_ratio = image_rect.width / image_rect.height
            scale_factor = 3.5

            self.surf = pg.transform.scale(
                image,
                (
                    int((screen_rect.height / scale_factor) * card_aspect_ratio),
                    int(screen_rect.height / scale_factor),
                ),
            )
        else:
            self.surf = image
        self.path = path
        self.rect = self.surf.get_rect()
        self.selected = False
