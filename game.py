import math
import random
from array import array
from dataclasses import dataclass
from pathlib import Path

import pygame
from pygame._sdl2 import Window

from story import (
    KILL_ENCOURAGEMENT,
    PLAYER_NAME,
    SECTOR_ENCOURAGEMENT,
    draw_sam_message,
    draw_story,
    make_sam_portrait,
    make_story_art,
)

WIDTH, HEIGHT = 400, 250
VIEW_HEIGHT = 196
FOCAL = 280
RELAY = (
    "###############",
    "#.....#.......#",
    "#.............#",
    "#.....#..##...#",
    "#.##..#.......#",
    "#.....###..#..#",
    "#..........#..#",
    "#..#.......#..#",
    "#..#..##......#",
    "#.............#",
    "###############",
)
FOUNDRY = (
    "###############",
    "#.............#",
    "#.#####.#####.#",
    "#.#.........#.#",
    "#.#.###.###.#.#",
    "#...#.....#...#",
    "###.#.....#.###",
    "#...#.....#...#",
    "#.###.....###.#",
    "#.............#",
    "###############",
)
VAULT = (
    "###############",
    "#.....#.......#",
    "#.###.#.#####.#",
    "#...#.........#",
    "###.#.###.#####",
    "#.....#.......#",
    "#.###.#.###.#.#",
    "#...#.......#.#",
    "#.#.#####.#.#.#",
    "#.............#",
    "###############",
)
SECTORS = (
    ("RELAY", RELAY, (90, 113, 128), (2.5, 2.5), ((8, 2), (12, 4), (7, 7))),
    ("FOUNDRY", FOUNDRY, (147, 92, 68), (1.5, 1.5), ((11, 1), (7, 5), (3, 7), (12, 9))),
    ("VAULT", VAULT, (98, 120, 96), (1.5, 1.5), ((5, 2), (12, 3), (10, 5), (3, 7), (12, 9))),
)
DRONE_TYPES = (
    ("Claude", (242, 151, 104)),
    ("Gemini", (140, 167, 255)),
    ("Grok", (219, 129, 212)),
)
INK = (12, 16, 26)
TEXT = (224, 236, 231)
MINT = (104, 236, 193)
SAMPLE_RATE = 22050
TEXTURE_SIZE = 32
LIGHT_LEVELS = 16
SECTOR_DELAY = 1.5
SHOT_COOLDOWN = 0.27
BLAST_FRAME_DURATION = 0.04
SAM_MESSAGE_DURATION = 3.5


def make_blast_frames():
    frames = []
    for reach, width, sparks in (
        (5, 4, ((8, 11), (16, 10))),
        (1, 8, ((3, 8), (21, 6), (7, 3), (17, 2))),
        (7, 6, ((2, 7), (22, 5), (5, 3), (19, 2), (12, 1))),
    ):
        blast = pygame.Surface((25, 20), pygame.SRCALPHA)
        pygame.draw.polygon(blast, (20, 117, 119), [
            (8, 19), (4, 15), (12 - width, 9), (9, 11), (12, reach),
            (15, 11), (12 + width, 8), (20, 15), (16, 19),
        ])
        pygame.draw.polygon(blast, MINT, [
            (9, 19), (7, 14), (10, 15), (12, reach + 3),
            (15, 14), (18, 13), (15, 19),
        ])
        pygame.draw.polygon(blast, (241, 255, 222), [
            (10, 19), (12, max(12, reach + 5)), (14, 19),
        ])
        for index, point in enumerate(sparks):
            pygame.draw.rect(blast, MINT if index % 2 else TEXT, (*point, 1, 2))
        frames.append(pygame.transform.scale(blast, (50, 40)))
    return frames


def make_wall_textures():
    rng = random.Random(1993)
    textures = []
    for name, _, color, _, _ in SECTORS:
        pattern = [
            [wall_brightness(name, x, y) * rng.uniform(0.88, 1.12) for x in range(TEXTURE_SIZE)]
            for y in range(TEXTURE_SIZE)
        ]
        palette = []
        for light in range(1, LIGHT_LEVELS + 1):
            texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE)).convert()
            for y, row in enumerate(pattern):
                for x, brightness in enumerate(row):
                    scale = brightness * light / LIGHT_LEVELS
                    texture.set_at((x, y), tuple(min(255, int(channel * scale)) for channel in color))
            palette.append([texture.subsurface((x, 0, 1, TEXTURE_SIZE)) for x in range(TEXTURE_SIZE)])
        textures.append(palette)
    return textures


def wall_brightness(sector, x, y):
    if sector == "RELAY":
        x = (x + (y // 8 % 2) * 8) % 16
        y %= 8
        if x == 0 or y == 0:
            return 0.35
        if x == 1 or y == 1:
            return 1.24
        if x == 15 or y == 7:
            return 0.66
        return 1
    if sector == "FOUNDRY":
        x %= 16
        if x in (0, 15) or y in (0, 31):
            return 0.34
        if x in (2, 13) and y in (3, 28):
            return 1.55
        if 6 <= y < 26:
            return (0.35, 0.50, 1.06, 1.27)[x % 4]
        return 0.85
    if x in (0, 31) or y in (0, 31):
        return 0.28
    if 6 <= y <= 25 and x in (5, 6, 24, 25):
        return 1.47
    if 6 <= x <= 25 and y in (5, 6, 24, 25):
        return 1.47
    if 10 <= x <= 21 and 10 <= y <= 21:
        return 0.40 if y % 3 == 0 else 0.62
    return 0.98


def make_drone_sprite(name, color):
    sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
    if name == "Claude":
        pygame.draw.rect(sprite, INK, (1, 2, 30, 28), border_radius=7)
        pygame.draw.rect(sprite, (155, 75, 50), (3, 4, 26, 24), border_radius=6)
        pygame.draw.rect(sprite, color, (6, 6, 20, 19), border_radius=5)
        for index, length in enumerate((8, 7, 9, 7, 8, 9, 6, 8, 7, 9, 8, 7)):
            angle = index * math.tau / 12 + 0.08
            tip = (round(16 + length * math.cos(angle)), round(15 + length * math.sin(angle)))
            pygame.draw.line(sprite, (255, 241, 221), (16, 15), tip, 2)
    elif name == "Gemini":
        pygame.draw.polygon(sprite, INK, [(16, 1), (31, 15), (23, 27), (16, 31), (9, 27), (1, 15)])
        pygame.draw.polygon(sprite, (55, 69, 125), [(16, 4), (28, 15), (22, 25), (10, 25), (4, 15)])
        points = [(16, 5), (19, 12), (27, 15), (19, 18), (16, 26), (13, 18), (5, 15), (13, 12)]
        for corner, hue in enumerate(((255, 126, 130), color, (121, 229, 175), (255, 211, 123))):
            edge = [points[(corner * 2 + delta) % 8] for delta in (-1, 0, 1)]
            pygame.draw.polygon(sprite, hue, [(16, 15), *edge])
    else:
        pygame.draw.polygon(sprite, color, [(1, 6), (31, 6), (27, 26), (16, 30), (5, 26)])
        pygame.draw.polygon(sprite, INK, [(3, 8), (29, 8), (25, 24), (16, 28), (7, 24)])
        pygame.draw.circle(sprite, TEXT, (16, 16), 8, 2)
        pygame.draw.line(sprite, INK, (10, 22), (24, 8), 5)
        pygame.draw.line(sprite, TEXT, (8, 25), (25, 8), 2)
    return sprite


def make_sound(duration, waveform):
    frames = int(SAMPLE_RATE * duration)
    samples = array("h")
    for index in range(frames):
        time = index / SAMPLE_RATE
        envelope = min(time / 0.005, 1) * (1 - index / frames)
        samples.append(round(20000 * envelope * waveform(time)))
    return pygame.mixer.Sound(buffer=samples)


def pulse_wave(time):
    phase = math.tau * (820 * time - 2200 * time * time)
    return 0.72 * math.sin(phase) + 0.22 * math.sin(phase * 2)


def scream_wave(time):
    phase = math.tau * (660 * time - 530 * time * time) + 1.4 * math.sin(math.tau * 27 * time)
    rasp = 0.7 + 0.3 * math.sin(math.tau * 49 * time)
    return rasp * (0.56 * math.sin(phase) + 0.26 * math.sin(phase * 3) + 0.12 * math.sin(phase * 5))


@dataclass
class Drone:
    name: str
    x: float
    y: float
    color: tuple
    hp: int = 2
    ability_timer: float = 0
    ability_cooldown: float = 0
    dash_timer: float = 0
    aim: tuple = (0, 0)

    @property
    def ability_label(self):
        if self.dash_timer:
            return "DASH"
        if self.ability_timer:
            return {"Claude": "SHIELDED", "Gemini": "AIMING", "Grok": "CHARGING"}[self.name]
        return ""


def cast(level, x, y, dx, dy):
    """Return the distance, wall side, and horizontal texture coordinate."""
    cell_x, cell_y = int(x), int(y)
    step_x, step_y = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
    delta_x = abs(1 / dx) if dx else math.inf
    delta_y = abs(1 / dy) if dy else math.inf
    next_x = (cell_x + (dx > 0) - x) / dx if dx else math.inf
    next_y = (cell_y + (dy > 0) - y) / dy if dy else math.inf
    while True:
        side = next_y < next_x
        if side:
            distance = next_y
            next_y += delta_y
            cell_y += step_y
        else:
            distance = next_x
            next_x += delta_x
            cell_x += step_x
        if level[cell_y][cell_x] == "#":
            hit = x + distance * dx if side else y + distance * dy
            return distance, side, hit % 1


def move(level, x, y, dx, dy, radius):
    def clear(px, py):
        return all(
            level[int(py + oy)][int(px + ox)] == "."
            for ox in (-radius, radius)
            for oy in (-radius, radius)
        )

    if clear(x + dx, y):
        x += dx
    if clear(x, y + dy):
        y += dy
    return x, y


class Game:
    def __init__(self, shot_sound=None, scream_sound=None):
        self.shot_sound = shot_sound
        self.scream_sound = scream_sound
        self.health = 100
        self.energy = 24
        self.kills = 0
        self.load_sector(0)

    def load_sector(self, index):
        self.sector = index
        self.sector_name, self.level, _, spawn, enemy_positions = SECTORS[index]
        self.x, self.y = spawn
        self.angle = 0
        self.cooldown = 0
        self.damage_flash = 0
        self.sector_delay = 0
        self.sam_message = SECTOR_ENCOURAGEMENT[index]
        self.sam_message_time = SAM_MESSAGE_DURATION
        self.drones = []
        for number, (x, y) in enumerate(enemy_positions):
            name, color = DRONE_TYPES[number % len(DRONE_TYPES)]
            self.drones.append(Drone(name, x + 0.5, y + 0.5, color))

    @property
    def status(self):
        if self.health <= 0:
            return "CONNECTION LOST"
        if self.sector == len(SECTORS) - 1 and self.sector_delay:
            return "CAMPAIGN CLEARED"
        return ""

    def fire(self):
        if self.status or self.sector_delay or self.cooldown > 0 or self.energy <= 0:
            return
        self.energy -= 1
        self.cooldown = SHOT_COOLDOWN
        if self.shot_sound is not None:
            self.shot_sound.play()
        wall_distance, _, _ = cast(self.level, self.x, self.y, math.cos(self.angle), math.sin(self.angle))
        for depth, offset, drone in sorted(self.visible_drones(), key=lambda item: item[0]):
            if depth < wall_distance and abs(offset) < 0.28:
                if drone.name == "Claude" and drone.ability_timer:
                    break
                drone.hp -= 1
                if drone.name == "Claude" and drone.hp == 1:
                    drone.ability_timer = 1.1
                if drone.hp == 0:
                    self.energy += 4
                    self.kills += 1
                    if self.kills % 2 == 0:
                        message_index = (self.kills // 2 - 1) % len(KILL_ENCOURAGEMENT)
                        self.sam_message = KILL_ENCOURAGEMENT[message_index]
                        self.sam_message_time = SAM_MESSAGE_DURATION
                    if self.scream_sound is not None:
                        self.scream_sound.play()
                    if all(drone.hp <= 0 for drone in self.drones):
                        self.sector_delay = SECTOR_DELAY
                break

    def visible_drones(self):
        fx, fy = math.cos(self.angle), math.sin(self.angle)
        for drone in self.drones:
            dx, dy = drone.x - self.x, drone.y - self.y
            depth = dx * fx + dy * fy
            if drone.hp > 0 and depth > 0.05:
                yield depth, dy * fx - dx * fy, drone

    def update(self, dt, keys, mouse_dx):
        self.cooldown = max(0, self.cooldown - dt)
        self.sam_message_time = max(0, self.sam_message_time - dt)
        self.damage_flash = max(0, self.damage_flash - dt)
        if self.status:
            return
        if self.sector_delay:
            self.sector_delay -= dt
            if self.sector_delay <= 0:
                self.health = min(100, self.health + 25)
                self.energy += 8
                self.load_sector(self.sector + 1)
            return
        self.angle += mouse_dx * 0.003 + (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 2.2 * dt
        forward = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])
        strafe = keys[pygame.K_d] - keys[pygame.K_a]
        speed = 2.75 * dt / max(1, math.hypot(forward, strafe))
        fx, fy = math.cos(self.angle), math.sin(self.angle)
        self.x, self.y = move(
            self.level, self.x, self.y, (forward * fx - strafe * fy) * speed,
            (forward * fy + strafe * fx) * speed, 0.2,
        )

        for drone in self.drones:
            if drone.hp > 0:
                self.update_drone(drone, dt)

    def take_damage(self, amount):
        if self.damage_flash == 0:
            self.health = max(0, self.health - amount)
            self.damage_flash = 0.55

    def update_drone(self, drone, dt):
        dx, dy = self.x - drone.x, self.y - drone.y
        distance = math.hypot(dx, dy)
        drone.ability_cooldown = max(0, drone.ability_cooldown - dt)

        if drone.dash_timer:
            ax, ay = drone.aim
            travel = 5.5 * min(drone.dash_timer, dt)
            start = drone.x, drone.y
            drone.x, drone.y = move(self.level, *start, ax * travel, ay * travel, 0.24)
            drone.dash_timer = max(0, drone.dash_timer - dt)
            if math.hypot(self.x - drone.x, self.y - drone.y) < 0.62:
                self.take_damage(22)
                drone.dash_timer = 0
            return

        if drone.ability_timer:
            drone.ability_timer = max(0, drone.ability_timer - dt)
            if drone.name != "Claude":
                if drone.ability_timer == 0:
                    ax, ay = drone.aim
                    if drone.name == "Grok":
                        drone.dash_timer = 0.65
                        drone.ability_cooldown = 2.1
                    else:
                        drone.ability_cooldown = 1.8
                        along = dx * ax + dy * ay
                        if 0 < along < 8 and abs(dy * ax - dx * ay) < 0.35:
                            wall, _, _ = cast(self.level, drone.x, drone.y, dx / distance, dy / distance)
                            if wall > distance:
                                self.take_damage(15)
                return

        if distance < 0.62:
            self.take_damage(12)
        elif distance < 8:
            ux, uy = dx / distance, dy / distance
            wall, _, _ = cast(self.level, drone.x, drone.y, ux, uy)
            if wall <= distance:
                return
            if drone.ability_cooldown == 0 and drone.name == "Gemini":
                drone.aim = ux, uy
                drone.ability_timer = 0.7
            elif drone.ability_cooldown == 0 and drone.name == "Grok" and distance < 4:
                drone.aim = ux, uy
                drone.ability_timer = 0.55
            elif drone.name != "Gemini" or distance > 4:
                drone.x, drone.y = move(self.level, drone.x, drone.y, ux * dt, uy * dt, 0.24)

    def draw(self, canvas, small, large, paused, wall_textures, drone_sprites, blast_frames, player_icon):
        def label(message, x, y, font=small, color=TEXT):
            glyph = font.render(message, True, color)
            canvas.blit(glyph, (x - glyph.get_width() // 2, y))

        horizon = VIEW_HEIGHT // 2
        for y in range(VIEW_HEIGHT):
            shade = abs(y - horizon) // 7
            color = (18 + shade, 24 + shade, 36 + shade) if y < horizon else (
                33 + shade, 33 + shade, 44 + shade
            )
            pygame.draw.line(canvas, color, (0, y), (WIDTH - 1, y))

        fx, fy = math.cos(self.angle), math.sin(self.angle)
        depths = []
        canvas.set_clip((0, 0, WIDTH, VIEW_HEIGHT))
        palette = wall_textures[self.sector]
        for column in range(WIDTH):
            offset = (column + 0.5 - WIDTH / 2) / FOCAL
            depth, side, wall_x = cast(self.level, self.x, self.y, fx - fy * offset, fy + fx * offset)
            depths.append(depth)
            height = max(1, int(FOCAL / max(depth, 0.01)))
            shade = max(0.2, 1 / (1 + depth * 0.17)) * (0.75 if side else 1)
            light = max(1, round(shade * LIGHT_LEVELS))
            strip = palette[light - 1][int(wall_x * TEXTURE_SIZE)]
            canvas.blit(pygame.transform.scale(strip, (1, height)), (column, horizon - height // 2))

        for depth, offset, drone in sorted(self.visible_drones(), key=lambda item: item[0], reverse=True):
            size = min(1200, max(1, int(FOCAL * 0.58 / depth)))
            center = int(WIDTH / 2 + FOCAL * offset / depth)
            left, top = center - size // 2, horizon - size // 3
            sprite = drone_sprites[drone.name]
            if drone.ability_label:
                sprite = sprite.copy()
                pygame.draw.circle(sprite, (255, 230, 142), (16, 16), 15, 1)
            scaled = pygame.transform.scale(sprite, (size, size))
            for column in range(max(0, left), min(WIDTH, left + size)):
                if depth < depths[column]:
                    canvas.blit(scaled, (column, top), (column - left, 0, 1, size))
            if 0 <= center < WIDTH and depth < depths[center]:
                label(drone.name, center, top - 12, color=drone.color)
                if drone.ability_label:
                    label(drone.ability_label, center, top - 23, color=(255, 230, 142))

        center = WIDTH // 2
        pygame.draw.polygon(canvas, INK, [(center-50, VIEW_HEIGHT), (center-25, 171),
                            (center-17, 147), (center+17, 147), (center+25, 171),
                            (center+50, VIEW_HEIGHT)])
        pygame.draw.rect(canvas, (78, 105, 116), (center-15, 150, 30, 32), border_radius=4)
        pygame.draw.rect(canvas, MINT, (center-9, 158, 18, 4))
        blast_frame = int((SHOT_COOLDOWN - self.cooldown) / BLAST_FRAME_DURATION)
        if blast_frame < len(blast_frames):
            blast = blast_frames[blast_frame]
            canvas.blit(blast, (center - blast.get_width() // 2, 151 - blast.get_height()))
        pygame.draw.circle(canvas, TEXT, (center, horizon), 4, 1)
        if self.damage_flash > 0.36:
            pygame.draw.rect(canvas, (193, 77, 94), (0, 0, WIDTH, VIEW_HEIGHT), 4)
        canvas.set_clip(None)

        pygame.draw.rect(canvas, INK, (0, VIEW_HEIGHT, WIDTH, HEIGHT - VIEW_HEIGHT))
        pygame.draw.line(canvas, MINT, (0, VIEW_HEIGHT), (WIDTH, VIEW_HEIGHT))
        for x in (90, 166, 234, 310):
            pygame.draw.line(canvas, (51, 71, 83), (x, 204), (x, 242))
        for x, value, caption in (
            (45, self.energy, "ENERGY"), (128, f"{self.health}%", "HEALTH"),
            (272, sum(drone.hp > 0 for drone in self.drones), "DRONES"),
            (355, f"{self.sector + 1:02}", "SECTOR"),
        ):
            label(str(value), x, 203, large, MINT)
            label(caption, x, 232)
        canvas.blit(player_icon, player_icon.get_rect(center=(200, 215)))
        label(PLAYER_NAME, 200, 232)

        message = self.status or ("PAUSED" if paused else "")
        hint = "R  RESTART   |   ESC  QUIT" if self.status else "CLICK OR ESC TO RESUME"
        if not message and self.sector_delay:
            message = f"{self.sector_name} CLEARED"
            hint = f"NEXT SECTOR  /  {SECTORS[self.sector + 1][0]}"
        if message:
            pygame.draw.rect(canvas, INK, (58, 66, 284, 62), border_radius=5)
            label(message, center, 72, large, MINT)
            if message == "CAMPAIGN CLEARED":
                label("RECOVERY KEY SECURED", center, 96)
            label(hint, center, 107)
        elif self.energy == 0:
            label("OUT OF ENERGY  |  R RESTART", center, 8, color=MINT)


def main():
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512, allowedchanges=0)
    pygame.init()
    try:
        screen = pygame.display.set_mode((1000, 625), pygame.RESIZABLE)
        window = Window.from_display_module()
        wall_textures = make_wall_textures()
        drone_sprites = {name: make_drone_sprite(name, color) for name, color in DRONE_TYPES}
        blast_frames = make_blast_frames()
        story_art = make_story_art()
        sam_portrait = make_sam_portrait()
        icon_path = Path(__file__).with_name("assets") / "openai-blossom.png"
        player_icon = pygame.transform.smoothscale(pygame.image.load(icon_path).convert_alpha(), (34, 34))
        pygame.display.set_caption("Context Breach: War of the Machines")
        canvas = pygame.Surface((WIDTH, HEIGHT))
        small = pygame.font.SysFont("dejavusans,liberationsans,arial", 11)
        large = pygame.font.SysFont("dejavusans,liberationsans,arial", 22)
        clock = pygame.time.Clock()
        shot_sound = scream_sound = None
        if pygame.mixer.get_init() is not None:
            shot_sound = make_sound(0.14, pulse_wave)
            scream_sound = make_sound(0.44, scream_wave)
            music_path = Path(__file__).with_name("DOOM_OST.mp3")
            if music_path.is_file():
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.30)
                pygame.mixer.music.play(-1)
        game = Game(shot_sound, scream_sound)
        briefed_sector = -1
        paused = False
        captured = False

        while True:
            dt = min(clock.tick(60) / 1000, 0.05)
            mouse_dx, shooting = 0, False
            briefing = briefed_sector != game.sector
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if briefing:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return
                    if (
                        event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
                        or event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    ):
                        briefed_sector = game.sector
                        paused = False
                    continue
                if event.type == pygame.WINDOWFOCUSLOST:
                    paused = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game.status:
                            return
                        paused = not paused
                    elif event.key == pygame.K_r:
                        game = Game(shot_sound, scream_sound)
                        briefed_sector = -1
                        briefing = True
                        paused = False
                    elif event.key == pygame.K_SPACE and not paused:
                        shooting = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    shooting = not paused
                    paused = False
                if event.type == pygame.MOUSEMOTION and not paused:
                    mouse_dx += event.rel[0]

            if not briefing and not paused:
                game.update(dt, pygame.key.get_pressed(), mouse_dx if captured else 0)
                if shooting and briefed_sector == game.sector:
                    game.fire()

            showing_story = briefed_sector != game.sector
            capture = not briefing and not showing_story and not paused and not game.status
            if capture != captured:
                window.relative_mouse = capture
                captured = capture

            if showing_story:
                draw_story(canvas, small, large, story_art, game.sector)
            else:
                game.draw(canvas, small, large, paused, wall_textures, drone_sprites, blast_frames, player_icon)
                if game.sam_message_time:
                    draw_sam_message(canvas, small, sam_portrait, game.sam_message)
            width, height = screen.get_size()
            scale = min(width / WIDTH, height / HEIGHT)
            size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
            screen.fill(INK)
            screen.blit(pygame.transform.scale(canvas, size),
                        ((width - size[0]) // 2, (height - size[1]) // 2))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
