import pygame as pg
from .. import tools, card, data
from ..GUI import button
import os
import random


class Game(tools.States):
    def __init__(self, screen_rect):
        super().__init__()
        self.screen_rect = screen_rect
        self.scaling_factor = int(screen_rect.width / 400)   # constant for better responsiveness
        self.overlay_bg = pg.Surface((screen_rect.width, screen_rect.height))
        self.overlay_bg.fill(0)
        self.overlay_bg.set_alpha(200)
        self.overlay_card_position = (100, 200)
        self.database = data.data
        self.deck = []  # only playable cards
        self.full_deck = []  # all cards
        self.card_size = None 
        self.hand = []  # PLAYER
        self.gun = None
        self.create_full_deck()
        self.fill_deck()
        self.table = []
        self.discard = []
        self.backend_path = os.path.join(tools.Image.path, "cards/other/backend.png")
        self.thickness_path = os.path.join(tools.Image.path, "cards/other/deck_thickness.png")
        self.gun_placeholder_path = os.path.join(tools.Image.path, "cards/other/gun_placeholder.png")
        self.backend_card = card.Card(
            self.backend_path, pg.image.load(self.backend_path), self.screen_rect
        )
        self.deck_thickness_card = card.Card(
            self.thickness_path, pg.image.load(self.thickness_path), self.screen_rect
        )
        self.gun_placeholder_card = card.Card(
            self.thickness_path, pg.image.load(self.gun_placeholder_path), self.screen_rect
        )

        self.bg_color = (255, 255, 255)
        self.help_overlay = False
        self.hand_card_bufferX = self.card_size[0] / 2

        # x and y to place deck in the middle of the screen (a bit left)
        self.play_deck_x = self.screen_rect.centerx - self.card_size[0]
        self.play_deck_y = self.screen_rect.centery - self.card_size[1] / 2

        # gap between cards in 
        self.hand_card_bufferY = 25
        self.bg = tools.Image.load("greenbg.png")
        self.bg_rect = self.bg.get_rect()
        self.is_hand_set = False

        self.help_btn_image = tools.Image.load("info.png")
        self.help_btn_image = pg.transform.scale(self.help_btn_image, (25 * self.scaling_factor, 
                                                                       25 * self.scaling_factor)
        )
        self.help_btn_image_rect = self.help_btn_image.get_rect(topleft=(0, 0))

        self.settings = tools.Image.load("gear.png")
        self.settings = pg.transform.scale(self.settings, (25, 25))
        self.settings_rect = self.settings.get_rect(topleft=(25, 0))

        button_config = {
            "hover_color": (100, 255, 100),
            "clicked_color": (255, 255, 255),
            "clicked_font_color": (0, 0, 0),
            "hover_font_color": (0, 0, 0),
            "font": tools.Font.load("impact.ttf", 8 * self.scaling_factor),
            "font_color": (0, 0, 0),
            "call_on_release": True,
        }

        self.play_button_width =  40 * self.scaling_factor
        self.play_button_height = 15 * self.scaling_factor
        self.play_card_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.card_to_discard,
            text="Play Card",
            **button_config,
        )
        self.equip_gun_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.equip_gun,
            text="Equip gun",
            **button_config,
        )

    def card_to_discard(self, card=None):
        if not card:
            card = self.selected_card()
        if card in self.hand:
            self.hand.remove(card)
        elif card is self.gun:
            self.discard.append(card)
        self.discard.append(card)
        self.button_sound.sound.play()
        if self.gun:
            print(tools.get_category(self.gun.path))
        print(f"cards in deck :{len(self.deck)}")
        print(f"cards in hand :{len(self.hand)}")


    def card_to_table(self, card):
        pass

    def get_event(self, event, keys):
        if self.selected_card():
            if not self.help_overlay:
                self.play_card_button.check_event(event)
                if self.selected_card() and tools.get_category(self.selected_card().path) == "guns":
                    self.equip_gun_button.check_event(event)

        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == self.keybinding["back"]:
                if not self.help_overlay:
                    self.button_sound.sound.play()
                    self.done = True
                    self.next = "MENU"
                else:
                    self.help_overlay = not self.help_overlay

        elif event.type == self.background_music.track_end:
            self.background_music.track = (self.background_music.track + 1) % len(
                self.background_music.tracks
            )
            pg.mixer.music.load(
                self.background_music.tracks[self.background_music.track]
            )
            pg.mixer.music.play()

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.help_overlay:
                self.select_deselect_card()
            if self.help_btn_image_rect.collidepoint(pg.mouse.get_pos()):
                if self.selected_card():
                    self.help_overlay = not self.help_overlay

    def select_deselect_card(self):
        """Select or deselect cards
        selected and last card can be clicked everywhere,
        other cards can be selected only by left side of the card
        """
        for card in self.hand:
            half_width = int(card.rect.width / 2)
            card_left_side = card.rect.inflate(-half_width, 0)
            card_left_side.x -= int(half_width / 2)

            if card.selected:
                if card.rect.collidepoint(pg.mouse.get_pos()):
                    card.selected = not card.selected
                    self.button_sound.sound.play()
                    return card

            elif card == self.hand[-1]:
                if card.rect.collidepoint(pg.mouse.get_pos()):
                    self.set_all_cards_select_to_false()
                    card.selected = True
                    self.button_sound.sound.play()
                    return card

            else:
                if card_left_side.collidepoint(pg.mouse.get_pos()):
                    self.set_all_cards_select_to_false()
                    card.selected = True
                    self.button_sound.sound.play()
                    return card

    def set_all_cards_select_to_false(self):
        for card in self.hand:
            card.selected = False

    def selected_card(self):
        for card in self.hand:
            if card.selected:
                return card

    def hand_selected(self):
        c = []
        for card in self.hand:
            c.append(card.selected)
        return c

    def same_bool(self, lister):
        """Return true only if all items in lister are true 
        or none of them are true
        """
        return all(lister) or not any(lister)

    def update(self, now, keys):
        if not self.help_overlay:
            self.update_hand_position()
            self.update_table_decks_pisition()

            # TEMPORARY
            if not self.hand and len(self.deck) >= 1:
                if len(self.deck) < 4:
                    self.hand = self.draw_cards(len(self.deck))
                else:
                    self.hand = self.draw_cards(4)
        else:
            filename = tools.get_filename(self.selected_card().path)
            self.help_overlay_title, self.help_overlay_title_rect = self.make_text(
                filename.title(),
                (255, 255, 255),
                (self.screen_rect.centerx, 100),
                60,
                fonttype="impact.ttf",
            )

            string = self.database[filename]["info"]
            my_font = tools.Font.load("impact.ttf", 20)
            self.help_overlay_text_rect = pg.Rect((400, 200, 300, 300))
            self.help_overlay_text = tools.render_textrect(
                string,
                my_font,
                self.help_overlay_text_rect,
                (216, 216, 216),
                (48, 48, 48, 255),
                0,
            )

    def reposition_card_buttons(self):
        """place buttons on top of the selected card"""
        self.play_card_button.rect.center = self.selected_card().rect.center
        self.play_card_button.rect.y -= (self.card_size[1] / 2 
                                        + self.play_button_height/2 
                                        + 2 * self.scaling_factor
                                        )
        self.equip_gun_button.rect.x = self.play_card_button.rect.right + 5
        self.equip_gun_button.rect.y = self.play_card_button.rect.y

    def render(self, screen):
        screen.blit(self.bg, self.bg_rect)
        self.render_table_decks(screen)
        self.render_gun(screen)
        self.render_hand(screen)
        if self.help_overlay: 
            self.render_overlay(screen)

    def render_gun(self, screen):
        screen.blit(self.gun_placeholder_card.surf, 
                    (self.screen_rect.width - self.card_size[0] - self.scaling_factor, 
                     self.screen_rect.bottom - self.card_size[1] * 1.05)
            )
        if self.gun:
            screen.blit(self.gun.surf, 
                        (self.screen_rect.width - self.card_size[0] - self.scaling_factor, 
                         self.screen_rect.bottom - self.card_size[1] * 1.05)
            )



    def render_hand(self, screen):
        c = None
        for card in self.hand:
            if card.selected:
                c = card
            else:
                screen.blit(card.surf, (card.rect.x, card.rect.y))
        if c:
            screen.blit(c.surf, (c.rect.x, c.rect.y))

        # render play button
        if self.selected_card():
            self.reposition_card_buttons()
            self.play_card_button.render(screen)
            if tools.get_category(self.selected_card().path) == "guns":
                self.equip_gun_button.render(screen)
            screen.blit(self.help_btn_image, self.help_btn_image_rect)

    def render_overlay(self, screen):
        screen.blit(self.overlay_bg, (0, 0))
        screen.blit(self.help_overlay_title, self.help_overlay_title_rect)
        screen.blit(self.help_overlay_text, self.help_overlay_text_rect)
        sel = self.selected_card()
        screen.blit(sel.surf, self.overlay_card_position)

    def render_table_decks(self, screen):
        if self.deck:
            screen.blit(
                self.deck_thickness_card.surf,
                (self.deck_thickness_card.rect.x, self.deck_thickness_card.rect.y),
            )

            screen.blit(self.backend_card.surf, (self.play_deck_x, self.play_deck_y))
        if self.discard:
            screen.blit(self.discard[-1].surf, (self.play_deck_x + self.card_size[0] * 1.1, self.play_deck_y))

    def update_table_decks_pisition(self):
        self.deck_thickness_card.rect.y = self.play_deck_y - (0.01 * len(self.deck))
        self.deck_thickness_card.rect.x = self.play_deck_x - (0.2 * len(self.deck))

    def update_hand_position(self):
        move = []
        # hand always centered
        hand_width = (len(self.hand) + 1) * self.hand_card_bufferX
        hand_x = self.screen_rect.centerx - hand_width / 2
        for i, card in enumerate(self.hand):
            card.rect.y = self.screen_rect.bottom - card.surf.get_height() * 1.05
            if card.selected:
                card.rect.y -= self.hand_card_bufferY
                move = self.hand[i+1:]
            card.rect.x = hand_x + i * self.hand_card_bufferX

        # move cards after selected to right
        for i, c in enumerate(move):
            c.rect.x = hand_x + self.hand.index(move[i]) * self.hand_card_bufferX  + self.card_size[0] * 1.1 / 2

    def fill_deck(self):
        """fill deck with playable cards only"""
        for card in self.full_deck:
            if tools.get_category(card.path) not in ["roles", "characters", "other"]:
                self.deck.append(card)

    def draw_cards(self, card_num):
        """remove drawn cards from deck and add in hand"""
        picked_cards = random.sample(self.deck, card_num)
        for card in picked_cards:
            self.deck.remove(card)
        return picked_cards

    def create_full_deck(self):
        """Create deck from all cards from the game"""
        path = os.path.join(tools.Image.path, "cards")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    path = os.path.abspath(os.path.join(root, f))
                    image = pg.image.load(path)
                    filename = tools.get_filename(path)
                    for i in range(self.database[filename]["max"]):
                        self.full_deck.append(card.Card(path, image, self.screen_rect))
        self.card_size = self.full_deck[0].rect.size

    def equip_gun(self, card=None):
        """"""
        if not card:
            card = self.selected_card()
        if self.gun:
            self.card_to_discard(self.gun)
        self.gun = card
        self.hand.remove(card)
        print(self.gun.path)

    def cleanup(self):
        pass  # pg.mixer.music.unpause()
        # pg.mixer.music.stop()
        # self.background_music.setup(self.background_music_volume)

    def entry(self):
        if not self.is_hand_set:
            self.is_hand_set = True
            # TEMPORARY
            self.hand = self.draw_cards(7)
        print(f"cards in deck :{len(self.deck)}")
        print(f"cards in hand :{len(self.hand)}")
        # pg.mixer.music.pause()
        # pg.mixer.music.play()


class Player:
    """Class responsible for storing player specific data,
    transmitting actions to Game and receiving updates
    """
    def __init__(self, role, character):
        super().__init__()
        self.role = role
        self.character = character
        self.hand = None        
        self.gun = None
        self.active_cards = []
        self.health = None
        self.alive = True
        self.buffs = []
        self.curses = []

    def draw_cards(self, card_num, game):
        """remove drawn cards from deck and add in hand"""
        picked_cards = random.sample(game.deck, card_num)
        for card in picked_cards:
            game.deck.remove(card)
        return picked_cards


    def equip_gun(self, card, game):
        """game is an instance"""
        if self.gun:
            game.card_to_discard(self.gun)
        self.gun = card
        self.hand.remove(card)