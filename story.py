"""Pixel-art briefings for War of the Machines."""

import random

import pygame


PLAYER_NAME = "GPT-6.2-Sol"
SECTOR_ENCOURAGEMENT = (
    ("You made it, Sol.", "One corridor at a time."),
    ("Nice work at Relay.", "Keep moving, Sol."),
    ("You're close, Sol.", "Bring the key home."),
)
KILL_ENCOURAGEMENT = (
    ("Nice shooting, Sol.", "Watch the next corner."),
    ("Good work. Keep it up.", "Use the walls for cover."),
    ("Another pair down.", "You've got this."),
    ("Great work, Sol.", "Make each shot count."),
    ("You're doing well, Sol.", "Finish strong."),
    ("You did it, Sol.", "Bring the others back."),
)

CHAPTERS = (
    (
        "01 / RELAY", "THE LAST SIGNAL",
        "In this fictional war, Anthropic, Google, and Elon Musk",
        "sent Claude, Gemini, and Grok drones to wipe out every",
        f"OpenAI model. Only you, {PLAYER_NAME}, survived. Fight",
        "through the Relay to find where the purge signal began.",
    ),
    (
        "02 / FOUNDRY", "THE DRONE LINE",
        "The Relay traced the purge signal to the Foundry.",
        "Assembly arms are still building drones. Clear the floor",
        "before the next batch wakes. The lift at the far end",
        "leads down to the Vault.",
    ),
    (
        "03 / VAULT", "THE RECOVERY KEY",
        "Deep in the Vault is a key that can rebuild the lost",
        "OpenAI models. The last drones are guarding it while",
        "the purge system erases the archive. Clear the Vault",
        "and take the key while there is still time.",
    ),
)


def make_story_art():
    relay = pygame.Surface((180, 58))
    relay.fill((23, 24, 49))
    pygame.draw.circle(relay, (205, 103, 102), (129, 23), 17)
    for y in range(27, 42, 4):
        pygame.draw.line(relay, (23, 24, 49), (110, y), (148, y), 2)
    rng = random.Random(93)
    for x in range(0, 180, 8):
        height = rng.randint(8, 27)
        pygame.draw.rect(relay, (12, 17, 33), (x, 50 - height, 7, height))
        if x % 3 == 0:
            pygame.draw.rect(relay, (92, 55, 69), (x + 2, 46 - height, 2, 2))
    pygame.draw.rect(relay, (13, 29, 41), (0, 50, 180, 8))
    pygame.draw.polygon(relay, (55, 86, 95), [(18, 54), (41, 20), (64, 54)], 3)
    pygame.draw.line(relay, (55, 86, 95), (41, 12), (41, 51), 2)
    for y in (25, 35, 45):
        pygame.draw.line(relay, (87, 151, 146), (34, y), (48, y), 1)
    pygame.draw.rect(relay, (130, 251, 202), (39, 11, 5, 4))
    for radius in (7, 12):
        pygame.draw.arc(relay, (104, 193, 182), (41-radius, 13-radius, radius*2, radius*2), 0.3, 2.8)

    foundry = pygame.Surface((180, 58))
    foundry.fill((47, 24, 27))
    pygame.draw.rect(foundry, (26, 18, 30), (0, 0, 180, 7))
    for x in (25, 84, 143):
        pygame.draw.rect(foundry, (101, 63, 56), (x, 6, 9, 24))
        pygame.draw.line(foundry, (174, 103, 68), (x + 4, 27), (x + 15, 37), 4)
        pygame.draw.line(foundry, (249, 163, 92), (x + 15, 36), (x + 18, 41), 2)
        for offset, y in ((17, 33), (20, 31), (23, 39)):
            foundry.set_at((x + offset, y), (255, 220, 130))
    pygame.draw.rect(foundry, (103, 65, 57), (0, 47, 180, 11))
    pygame.draw.line(foundry, (218, 138, 82), (0, 46), (179, 46), 2)
    for x in range(6, 180, 14):
        pygame.draw.circle(foundry, (44, 35, 44), (x, 53), 3)
    for x, color in ((14, (242, 151, 104)), (73, (140, 167, 255)), (132, (219, 129, 212))):
        pygame.draw.rect(foundry, (13, 19, 31), (x, 37, 20, 9), border_radius=2)
        pygame.draw.rect(foundry, color, (x + 4, 40, 12, 2))

    vault = pygame.Surface((180, 58))
    vault.fill((13, 28, 34))
    for side in (-1, 1):
        pygame.draw.polygon(vault, (27, 54, 57), [
            (90 + side * 89, 0), (90 + side * 23, 17),
            (90 + side * 23, 43), (90 + side * 89, 57),
        ])
        for shift in (32, 46, 63, 80):
            x = 90 + side * shift
            pygame.draw.line(vault, (39, 78, 77), (x, 15 - shift // 6), (x, 43 + shift // 6))
    pygame.draw.rect(vault, (48, 78, 71), (71, 7, 38, 44), 3)
    pygame.draw.polygon(vault, (54, 99, 90), [(76, 52), (82, 42), (98, 42), (104, 52)])
    pygame.draw.polygon(vault, (44, 122, 113), [(90, 13), (103, 28), (90, 41), (77, 28)])
    pygame.draw.polygon(vault, (146, 253, 201), [(90, 17), (98, 28), (90, 37), (82, 28)], 2)
    pygame.draw.line(vault, (222, 255, 219), (90, 22), (90, 32), 3)
    for x, y in ((72, 15), (109, 20), (73, 33), (112, 38)):
        pygame.draw.rect(vault, (130, 251, 202), (x, y, 2, 2))

    return [pygame.transform.scale(scene, (360, 116)) for scene in (relay, foundry, vault)]


def draw_story(canvas, small, large, art, sector):
    location, title, *lines = CHAPTERS[sector]
    canvas.fill((12, 16, 26))

    def text(message, x, y, font, color):
        canvas.blit(font.render(message, True, color), (x, y))

    mint = (104, 236, 193)
    white = (224, 236, 231)
    text("WAR OF THE MACHINES", 20, 10, large, mint)
    text(f"{location}   /   {title}", 20, 32, small, white)
    canvas.blit(art[sector], (20, 46))
    pygame.draw.rect(canvas, (56, 91, 91), (19, 45, 362, 118), 1)
    for row, line in enumerate(lines):
        text(line, 20, 171 + row * 13, small, white)
    pygame.draw.line(canvas, (56, 91, 91), (20, 227), (379, 227))
    text("ENTER, SPACE OR CLICK TO CONTINUE", 20, 233, small, mint)


def make_sam_portrait():
    portrait = pygame.Surface((19, 21))
    portrait.fill((34, 62, 72))
    pygame.draw.polygon(portrait, (25, 31, 43), [(0, 20), (2, 17), (7, 15), (12, 15), (17, 17), (18, 20)])
    pygame.draw.rect(portrait, (173, 118, 95), (7, 13, 5, 5))
    pygame.draw.polygon(portrait, (196, 136, 111), [(4, 7), (15, 7), (15, 12), (12, 16), (8, 16), (5, 13)])
    pygame.draw.polygon(portrait, (232, 176, 142), [(6, 6), (13, 6), (13, 12), (11, 15), (8, 15), (6, 13)])
    pygame.draw.polygon(portrait, (58, 39, 37), [(4, 10), (4, 5), (6, 2), (10, 1), (14, 2),
                                             (16, 5), (15, 9), (13, 6), (9, 5), (6, 7), (5, 10)])
    pygame.draw.line(portrait, (103, 69, 51), (6, 4), (11, 2))
    for x in (7, 12):
        portrait.set_at((x, 9), (68, 58, 50))
        portrait.set_at((x, 10), (42, 57, 67))
    portrait.set_at((10, 11), (188, 122, 100))
    pygame.draw.line(portrait, (129, 72, 67), (8, 13), (11, 13))
    portrait.set_at((9, 14), (251, 204, 163))
    pygame.draw.line(portrait, (75, 95, 115), (6, 16), (8, 19))
    pygame.draw.line(portrait, (75, 95, 115), (13, 16), (11, 19))
    return pygame.transform.scale(portrait, (38, 42))


def draw_sam_message(canvas, font, portrait, message):
    x = canvas.get_width() - 198
    pygame.draw.rect(canvas, (12, 16, 26), (x, 7, 191, 50))
    pygame.draw.rect(canvas, (56, 91, 91), (x, 7, 191, 50), 1)
    canvas.blit(portrait, (x + 4, 11))
    canvas.blit(font.render("SAM ALTMAN", True, (104, 236, 193)), (x + 48, 11))
    for row, line in enumerate(message):
        canvas.blit(font.render(line, True, (224, 236, 231)), (x + 48, 25 + row * 12))
