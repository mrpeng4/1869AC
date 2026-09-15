import pygame
pygame.font.init()

def button(
        screen,
        width:float|int,
        height:float|int,
        posx:int,
        posy:int,
        button_color:str = "#edce5f",
        text:str = "Hi label",
        text_color:str = "#ffffff",
        text_size:int = 25,
        outline:int = 8,
        outline_color:str = "#ffffff",
        rounded_corners:int = 4):

    outline_rect = pygame.draw.rect(
        screen,
        outline_color,
        (posx, posy, width + outline, height + outline),
        border_radius= rounded_corners
    )

    button_rect = pygame.draw.rect(
        screen,
        button_color,
        (posx + 4, posy + 4, width, height), # the 4 is to make the outline rectangle align so all 4 sides show outline
        border_radius= rounded_corners
    )
    # rect: (x, y, width, height)

    render_text(text, screen, posx, posy, text_color, text_size)

def render_text(
        text:str,
        screen,
        posx,
        posy,
        text_color:str = "#ffffff",
        text_size:int = 25,):

    label_font = pygame.font.Font(None, text_size)
    label_text = label_font.render(text, False, text_color)
    label_rect = label_text.get_rect()
    label_rect.center = (posx + 50, posy + 24)

    screen.blit(label_text, label_rect)

