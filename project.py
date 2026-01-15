from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

player_pos = [0.0, 0.0]
player_direction = 270
player_speed = 1500
player_head = 128

game_intro = True
game_start = True
game_over = False
boss_dead = False
enemies = {}
enemy_db = None

player_type = None
player_flicker = False
enemy_flicker = False
player_black = False
enemy_black = False
FLICKER_INTERVAL = 0.20
player_timer = 0.0
enemy_timer = 0.0
projectile = []
in_combat = False
combat_cooldown = 0.0


COMBAT_FIGHT_BTN = (50, 720, 200, 760)
COMBAT_RUN_BTN = (50, 660, 200, 700)
COMBAT_INVENTORY_BTN = (300, 720, 500, 760)
MOVE1_BTN = (50, 720, 350, 760)
MOVE2_BTN = (50, 660, 350, 700)
YES_BTN = (30, 90, 80, 120)
NO_BTN  = (100, 90, 150, 120)

combat_state = {
    "enemy": None,
    "turn": None,
    "phase": None,
    "player_pos": None,
    "player_dir": None,
    "enemy_pos": None,
    "enemy_dir": None
}

door_prompt = {
    "active": False,
    "item": None
}

camera_pos = [0, 450, 450]
camera_angle = 0
camera_zoom = 1

torch_on = False
torch_brightness = 0.25
paused = False

last = time.time()
dt = 0

current_room = 0
interact = False
is_locked = False
is_barred1 = False
is_barred2 = False
bar_removed = False

opposite = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east"
}

valid_entry = [1, 5, 8, 13]

rooms_checked = set()
rooms = [
    {
        "width": 1400,
        "height": 1000,
        "floor": (0.5, 0.7, 0.1),
        "wall": (0.3, 0.2, 0.2),
        "doors": [
            {"side": "south", "target": 1, "locked": False}
        ]
    },

    {
        "width": 1800,
        "height": 1400,
        "floor": (0.25, 0.15, 0.07),
        "wall": (0.18, 0.1, 0.05),
        "enemies": 0,
        "chests": 0,
        "doors": [
            {"side": "north", "target": 0, "locked": False, "backup": 0},
            {"side": "south", "target": 9, "locked": False, "barred": True},
            {"side": "east", "target": 2, "locked": False},
            {"side": "west", "target": 3, "locked": False},
        ],
    },

    {
        "width": 2400,
        "height": 1200,
        "floor": (0.18, 0.08, 0.03),
        "wall": (0.12, 0.05, 0.02),
        "enemies": 2,
        "chests": 1,
        "doors": [
            {"side": "west", "target": 1, "locked": False},
            {"side": "east", "target": 4, "locked": False},
            {"side": "south", "target": 8, "locked": False}
        ],
    },

    {
        "width": 1200,
        "height": 2200,
        "floor": (0.12, 0.12, 0.18),
        "wall": (0.08, 0.08, 0.14),
        "enemies": 0,
        "chests": 1,
        "doors": [
            {"side": "east", "target": 1, "locked": False},
            {"side": "west", "target": 8, "locked": False, "barred": True},
            {"side": "south", "target": 16, "locked": False, "barred": True}
        ]
    },

    {
        "width": 3000,
        "height": 1000,
        "floor": (0.2, 0.1, 0.1),
        "wall": (0.15, 0.05, 0.05),
        "enemies": 3,
        "chests": 2,
        "doors": [
            {"side": "west", "target": 2, "locked": False},
            {"side": "south", "target": 5, "locked": False}
        ]
    },

    {
        "width": 2600,
        "height": 2600,
        "floor": (0.20, 0.10, 0.05),
        "wall": (0.13, 0.06, 0.03),
        "enemies": 2,
        "chests": 0,
        "doors": [
            {"side": "north", "target": 4, "locked": False, "backup": 0},
            {"side": "west", "target": 6, "locked": False},
            {"side": "east", "target": 7, "locked": False},
        ]
    },

    {
        "width": 1000,
        "height": 1400,
        "floor": (0.14, 0.06, 0.02),
        "wall": (0.08, 0.03, 0.01),
        "enemies": 0,
        "chests": 1,
        "doors": [
            {"side": "east", "target": 5, "locked": False},
        ]
    },

    {
        "width": 3400,
        "height": 1600,
        "floor": (0.22, 0.11, 0.06),
        "wall": (0.14, 0.07, 0.03),
        "enemies": 1,
        "chests": 0,
        "doors": [
            {"side": "west", "target": 5, "locked": False},
        ]
    },

    {
        "width": 2800,
        "height": 2200,
        "floor": (0.12, 0.05, 0.08),
        "wall": (0.18, 0.12, 0.16),
        "enemies": 1,
        "chests": 1,
        "doors": [
            {"side": "north", "target": 2, "locked": False, "backup": 0},
            {"side": "east", "target": 3, "locked": False, "bar_target": True},
            {"side": "west", "target": 9, "locked": False}
        ]
    },

    {
        "width": 2000,
        "height": 1800,
        "floor": (0.10, 0.10, 0.10),
        "wall": (0.05, 0.05, 0.05),
        "enemies": 2,
        "chests": 0,
        "doors": [
            {"side": "north", "target": 1, "locked": False, "bar_target": True},
            {"side": "east", "target": 8, "locked": False},
            {"side": "west", "target": 10, "locked": False},
        ]
    },

    {
        "width": 1600,
        "height": 2600,
        "floor": (0.08, 0.06, 0.10),
        "wall": (0.04, 0.03, 0.07),
        "enemies": 1,
        "chests": 1,
        "doors": [
            {"side": "east", "target": 9, "locked": False},
            {"side": "north", "target": 11, "locked": False, "barred": True},
            {"side": "west", "target": 13, "locked": False},
        ]
    },

    {
        "width": 3000,
        "height": 1400,
        "floor": (0.18, 0.09, 0.04),
        "wall": (0.12, 0.06, 0.03),
        "enemies": 3,
        "chests": 0,
        "doors": [
            {"side": "south", "target": 10, "locked": False, "bar_target": True},
            {"side": "east", "target": 12, "locked": False},
        ]
    },

    {
        "width": 1400,
        "height": 3000,
        "floor": (0.06, 0.12, 0.08),
        "wall": (0.03, 0.07, 0.04),
        "enemies": 0,
        "chests": 1,
        "doors": [
            {"side": "west", "target": 11, "locked": False},
            {"side": "south", "target": 13, "locked": False},
        ]
    },

    {
        "width": 2600,
        "height": 1600,
        "floor": (0.15, 0.08, 0.02),
        "wall": (0.10, 0.05, 0.01),
        "enemies": 2,
        "chests": 1,
        "doors": [
            {"side": "north", "target": 12, "locked": False, "backup": 0},
            {"side": "west", "target": 14, "locked": False},
            {"side": "east", "target": 10, "locked": False}
        ]
    },

    {
        "width": 1800,
        "height": 2000,
        "floor": (0.11, 0.07, 0.05),
        "wall": (0.07, 0.04, 0.03),
        "enemies": 1,
        "chests": 0,
        "doors": [
            {"side": "east", "target": 13, "locked": False},
            {"side": "south", "target": 15, "locked": False},
        ]
    },

    {
        "width": 2200,
        "height": 2200,
        "floor": (0.09, 0.09, 0.14),
        "wall": (0.05, 0.05, 0.09),
        "enemies": 3,
        "chests": 2,
        "doors": [
            {"side": "north", "target": 14, "locked": False, "backup": 0},
            {"side": "west", "target": 16, "locked": False},
        ]
    },

    {
        "width": 3000,
        "height": 1000,
        "floor": (0.20, 0.12, 0.07),
        "wall": (0.14, 0.08, 0.04),
        "enemies": 0,
        "chests": 1,
        "doors": [
            {"side": "east", "target": 15, "locked": False},
            {"side": "north", "target": 3, "locked": False, "bar_target": True},
        ]
    }
]

chests = {}
chest_idx = None
open_chest = False
lootable = False
rec = None
item_rec = False
loot_rec = False
loot1 = None
loot2 = None

DOOR_WIDTH = 140
DOOR_HEIGHT = 180

ITEMS = {
    "Laughing Gas": {
        "type": "consumable",
        "effects": {
             "Mage": {"sanity": -10, "attack": -2},
             "Rogue": {"sanity": +20, "attack": +5},
             "Warrior": {"sanity": -10, "attack": -2}
         }
    },

    "Smoke Bomb": {
        "type": "consumable",
        "effects": {
            "Mage": {"run": +10},
            "Rogue": {"run": +10},
            "Warrior": {"run": +10}
        }
    },

    "Healing Potion": {
        "type": "consumable",
        "effects": {
             "Mage": {"health": +20},
             "Rogue": {"health": +20},
             "Warrior": {"health": +20}}
    },

    "Mega Potion": {
        "type": "consumable",
        "effects": {
            "Mage": {"health": +80},
            "Rogue": {"health": +80},
            "Warrior": {"health": +80}
        }
    },

    "Magic Elixir": {
        "type": "consumable",
        "effects": {
            "Mage": {"stamina": +30},
            "Rogue": {},
            "Warrior": {}
        }
    },

    "Curse Charm": {
        "type": "consumable",
        "effects": {
            "Mage": {"attack": +15, "defense": +5, "stamina": +10},
            "Rogue": {"defense": -3},
            "Warrior": {"defense": -3}
        }
    },

    "Wine": {
        "type": "consumable",
        "effects": {
            "Mage":     {"sanity": +20, "stamina": +10},
            "Rogue":    {"sanity": +25, "stamina": +10},
            "Warrior":  {"sanity": +30, "stamina": +10}
        }
    },
    "Lockpick": {
        "type": "utility"
    },

    "Key": {
        "type": "utility"
    },

    "Dagger": {
        "type": "weapon"
    },

    "Golden Bow": {
        "type": "weapon"
    },

    "Magic Staff": {
        "type": "weapon"
    },

    "Greatsword": {
        "type": "weapon"
    },

    "Purple Vial": {
        "type": "status cure",
        "cure": "Poisoned"
    },
    "Bandage": {
        "type": "status cure",
        "cure": "Bleeding"
    },

    "Yellow Vial": {
        "type": "status cure",
        "cure": "Infected"
    }
}


class Player:
    def __init__(self, pid):
        self.id = pid

        self.health = 100
        self.stamina = 80
        self.sanity = 100

        self.attack = 20 if self.id == "Warrior" else 12
        self.defense = 15 if self.id == "Warrior" else 8

        self.walk_speed = 0.6 if self.id == "Mage" else 1.0 if self.id == "Warrior" else 2.0
        self.att_speed = 10 if not self.id == "Rogue" else 15
        self.run = 25 if not self.id == "Rogue" else 40

        self.req1 = 5
        self.req2 = 2
        self.dmg1 = 35 if self.id == "Mage" else 25 if self.id == "Rogue" else 45

        self.equip = "Dagger" if self.id == "Rogue" else "Magic Staff" if self.id == "Mage" else "Greatsword"

        self.mov1 = "Soul Flare" if self.id == "Mage" else "Back Stab" if self.id == "Rogue" else "Heavy Slash"
        self.mov2 = "Mind Shield" if self.id == "Mage" else "Tumble" if self.id == "Rogue" else "Iron Guard"

        self.status = []

        self.inventory = {}
        self.initialize_inventory()
        self.visual = self.initialize_visuals()

    def initialize_inventory(self):
        if self.id == "Mage":
            self.inventory = {"Bandage": 2, "Key": 1, "Magic Elixir": 2, "Cursed Charm": 1}
        elif self.id == "Rogue":
            self.inventory = {"Lockpick": 3, "Purple Vial": 1, "Smoke Bomb": 3, "Golden Bow": 1, "Greatsword": 1}
        elif self.id == "Warrior":
            self.inventory = {"Healing Potion": 3, "Key": 1, "Wine": 1, "Yellow Vial": 2}

    def use_item(self, item_name):
        global is_locked, interact
        if item_name not in self.inventory:
            return False

        item = ITEMS[item_name]
        item_type = item.get("type", "consumable")

        if item_type == "consumable":
            effects_by_class = item.get("effects", {})
            effects = effects_by_class.get(self.id, {})

            for stat, delta in effects.items():
                setattr(self, stat, getattr(self, stat) + delta)

            self.health = min(100, self.health)
            self.sanity = min(100, self.sanity)
            self.stamina = min(80, self.stamina)

            self.inventory[item_name] -= 1
            if self.inventory[item_name] == 0:
                self.inventory.pop(item_name)

            print(f"You used {item_name}")
            return True

        if item_type == "weapon":
            old_weapon = self.equip
            self.equip = item_name

            self.inventory[item_name] -= 1
            if self.inventory[item_name] == 0:
                self.inventory.pop(item_name)

            if old_weapon:
                self.inventory[old_weapon] = self.inventory.get(old_weapon, 0) + 1

            print(f"You equipped {item_name}")
            self.update_moves()
            return True

        if item_type == "utility":
            if in_combat:
                print(f"{item_name} cannot be used right now.")
                return False
            else:
                hit, door = door_in_front(rooms[current_room])
                if hit and door["locked"]:
                    self.inventory[item_name] -= 1
                    if self.inventory[item_name] == 0:
                        self.inventory.pop(item_name)
                    if item_name == "Key":
                        print("You opened the locked door")
                        door["locked"] = False
                        is_locked = False
                        interact = False
                    else:
                        open_door = random.random() < (0.5 if self.id == "Rogue" else 0.2)
                        if open_door:
                            print("You successfully pick the lock")
                            door["locked"] = False
                            is_locked = False
                            interact = False
                        else:
                            print("Lock picking failed, you broke the lockpick....")
                            interact = False
                return True
        if item_type == "status cure":
            cure = item.get("cure")

            if cure not in self.status:
                print(f"You are not {cure}.")
                return False

            self.status.remove(cure)

            self.inventory[item_name] -= 1
            if self.inventory[item_name] == 0:
                self.inventory.pop(item_name)

            print(f"You are no longer {cure}.")
            return True

    def add_item(self, item):
        if item not in self.inventory:
            self.inventory[item] = 1
        else:
            self.inventory[item] += 1
        print(f"{item} added to inventory")

    def add_status_effect(self, status):
        if status not in self.status:
            self.status.append(status)
            msg = "You have been" if status == "Infected" else "You are now"
            print(f"{msg} {status}")

    def status_damage(self):
        if len(self.status) >= 1:
            self.health -= 2
            for stat in self.status:
                temp = "being" if not stat == "Bleeding" else ""
                print(f"You take damage from {temp} {stat}")

    def update_moves(self):
        weapon_moves = {
            "Dagger": "Back Stab",
            "Greatsword": "Heavy Slash",
            "Magic Staff": "Soul Flare",
            "Golden Bow": "Quick Shot"
        }
        self.mov1 = weapon_moves.get(self.equip)

    def initialize_visuals(self):
        visuals = {
            "Mage": {
                "pants": (0.1, 0.2, 0.6),
                "torso": (0.1, 0.2, 0.6),
                "hair": (0.55, 0.25, 0.15),
                "skin": (1.0, 0.75, 0.5),
                "scale": (0.7, 1.4, 1.2),
            },

            "Rogue": {
                "pants": (0.4, 0.1, 0.1),
                "torso": (0.6, 0.1, 0.1),
                "hair": (0.05, 0.05, 0.05),
                "skin": (0.5, 0.35, 0.25),
                "scale": (0.7, 1.2, 1.2),
            },

            "Warrior": {
                "pants": (0.45, 0.45, 0.45),
                "torso": (0.55, 0.55, 0.55),
                "hair": (0.55, 0.55, 0.55),
                "skin": (0.45, 0.45, 0.45),
                "scale": (0.9, 1.2, 1.3),
            }
        }

        return visuals[self.id]


class EnemyDB:
    def __init__(self):
        self.name = ["Filthkin", "Skeleton", "Bandit"]

        self.attack = [8, 10, 12]
        self.defense = [12, 8, 10]
        self.att_speed = [1.2, 0.9, 1.1]

        self.mov1 = ["Filthy Strike", "Bone Throw", "Quick Stab"]
        self.mov2 = ["Vomit Throw", "Skeleton's Wails", "Sludge Bomb"]

        self.dmg1 = [15, 10, 20]
        self.dmg2 = [10, 10, 10]

    def spawn_enemy(self):
        return random.choice([0, 1, 2])


class EnemyInstance:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.health = 80 if self.id == 0 else 100 if self.id == 1 else 75 if self.id == 2 else 200
        self.dead = False
        self.looted = False

        self.speed = random.uniform(120, 200)
        self.dir = random.choice([0, 90, 180, 270])



def adjust_brightness(color, brightness, combat=False, who="enemy"):
    if combat:
        if who == "enemy" and enemy_flicker and enemy_black:
            return 0, 0, 0
        if who == "player" and player_flicker and player_black:
            return 0, 0, 0
        return color
    brightness = torch_brightness if not torch_on else brightness
    color = (color[0] * brightness, color[1] * brightness, color[2] * brightness)
    return color


def draw_chests(room_id):
    if room_id not in chests:
        return

    brightness = 0.75
    color = adjust_brightness((0.3, 0.2, 0.1), brightness)
    glColor3f(*color)

    for x, y, z in chests[room_id]:
        glPushMatrix()
        if z:
            brightness = 0.75
            color = adjust_brightness((0.22, 0.12, 0.08), brightness)
            glColor3f(*color)
        glTranslatef(x, y, 30)
        glScalef(1.35, 1, 1)
        glutSolidCube(60)
        glPopMatrix()


def draw_text(x, y, text, font=GLUT_BITMAP_9_BY_15, color=(1, 1, 1), ui=False):
    if not ui and (not interact and rooms_checked) and not game_start:
        return

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glClear(GL_DEPTH_BUFFER_BIT)
    glColor3f(*color)
    glRasterPos2f(x, y)
    text = [glutBitmapCharacter(font, ord(c)) for c in text]
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_box(x, y, width, height, color=(0, 0, 0), ui=False):
    if not ui and not interact and not game_start:
        return
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_segmented_bar(x, y, width, height, value, max_value, base_color, low_color=None, ui=False):
    if max_value <= 0:
        return

    ratio = max(0, min(1, value / max_value))

    filled = max(1, int(ratio * 20)) if value > 0 else 0

    segment_width = width / 20

    for i in range(20):
        if i < filled:
            color = base_color
            if low_color and ratio <= 0.3:
                color = low_color
        else:
            color = (0.15, 0.15, 0.15)

        draw_text_box(x + i * segment_width, y, segment_width - 2, height, color, ui=ui)


def draw_floor(w, h, color):
    brightness = 0.75
    color = adjust_brightness(color, brightness)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(-w / 2, -h / 2, 0)
    glVertex3f(w / 2, -h / 2, 0)
    glVertex3f(w / 2, h / 2, 0)
    glVertex3f(-w / 2, h / 2, 0)
    glEnd()


def draw_wall(x1, y1, x2, y2, h, color):

    brightness = 0.75
    color = adjust_brightness(color, brightness)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x1, y1, 0)
    glVertex3f(x2, y2, 0)
    glVertex3f(x2, y2, h)
    glVertex3f(x1, y1, h)
    glEnd()


def draw_walls(room, out=False):
    w, h = room["width"], room["height"]
    c = room["wall"]
    H = 350

    draw_wall(-w / 2, -h / 2, w / 2, -h / 2, H, c)
    if not out:
        draw_wall(-w / 2, h / 2, w / 2, h / 2, H, c)
        draw_wall(-w / 2, -h / 2, -w / 2, h / 2, H, c)
        draw_wall(w / 2, -h / 2, w / 2, h / 2, H, c)


def draw_bar(d, w, h, color=(0.15, 0.10, 0.08)):
    brightness = 0.75 if torch_on else torch_brightness
    adjusted_color = (color[0] * brightness, color[1] * brightness, color[2] * brightness)
    glColor3f(*adjusted_color)
    glPushMatrix()

    if d["side"] == "north":
        glTranslatef(0, h / 2 - 6, DOOR_HEIGHT * 0.6)

    elif d["side"] == "south":
        glTranslatef(0, -h / 2 + 6, DOOR_HEIGHT * 0.6)

    elif d["side"] == "east":
        glTranslatef(w / 2 - 6, 0, DOOR_HEIGHT * 0.6)
        glRotatef(90, 0, 0, 1)

    elif d["side"] == "west":
        glTranslatef(-w / 2 + 6, 0, DOOR_HEIGHT * 0.6)
        glRotatef(90, 0, 0, 1)

    glPushMatrix()
    glScalef(DOOR_WIDTH * 0.9, 10, 18)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()


def draw_door(d, room, color=(0.75, 0.6, 0.15)):
    w, h = room["width"], room["height"]
    if d["locked"]:
        color = (0.35, 0.3, 0.28)
    if d.get("barred") or d.get("bar_target"):
        color = (0.25, 0.15, 0.12)
    brightness = 0.75
    color = adjust_brightness(color, brightness)
    glColor3f(*color)
    glBegin(GL_QUADS)

    if d["side"] == "north":
        y = h / 2 - 4
        x1, x2 = -DOOR_WIDTH / 2, DOOR_WIDTH / 2
        glVertex3f(x1, y, 0)
        glVertex3f(x2, y, 0)
        glVertex3f(x2, y, DOOR_HEIGHT)
        glVertex3f(x1, y, DOOR_HEIGHT)

    elif d["side"] == "south":
        y = -h / 2 + 4
        x1, x2 = -DOOR_WIDTH / 2, DOOR_WIDTH / 2
        glVertex3f(x1, y, 0)
        glVertex3f(x2, y, 0)
        glVertex3f(x2, y, DOOR_HEIGHT)
        glVertex3f(x1, y, DOOR_HEIGHT)

    elif d["side"] == "east":
        x = w / 2 - 4
        y1, y2 = -DOOR_WIDTH / 2, DOOR_WIDTH / 2
        glVertex3f(x, y1, 0)
        glVertex3f(x, y2, 0)
        glVertex3f(x, y2, DOOR_HEIGHT)
        glVertex3f(x, y1, DOOR_HEIGHT)

    elif d["side"] == "west":
        x = -w / 2 + 4
        y1, y2 = -DOOR_WIDTH / 2, DOOR_WIDTH / 2
        glVertex3f(x, y1, 0)
        glVertex3f(x, y2, 0)
        glVertex3f(x, y2, DOOR_HEIGHT)
        glVertex3f(x, y1, DOOR_HEIGHT)

    glEnd()

    if d.get("bar_target"):
        draw_bar(d, w, h)


def draw_player(player):
    v = player.visual
    brightness = 1.0
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    if player.health <= 0:
        glRotatef(-90, 0, 1, 0)
    else:
        glRotatef(player_direction, 0, 0, 1)

    quad = gluNewQuadric()

    for side in (-1, 1):
        glPushMatrix()
        color = adjust_brightness(v["pants"], brightness, in_combat, "player")
        glColor3f(*color)
        glTranslatef(0, side * 20, 40)
        gluCylinder(quad, 4, 10, 30, 10, 10)
        glPopMatrix()

    glPushMatrix()
    color = adjust_brightness(v["torso"], brightness, in_combat, "player")
    glColor3f(*color)
    glTranslatef(0, 0, 90)
    glScalef(*v["scale"])
    glutSolidCube(35)
    glPopMatrix()

    glPushMatrix()
    color = adjust_brightness(v["skin"], brightness, in_combat, "player")
    glColor3f(*color)
    glTranslatef(0, 0, player_head)
    gluSphere(quad, 14, 10, 10)
    glPopMatrix()

    glPushMatrix()
    color = adjust_brightness(v["hair"], brightness, in_combat, "player")
    glColor3f(*color)
    glTranslatef(0, 0, player_head + 10)
    glScalef(0.8, 0.8, 0.8)
    gluSphere(quad, 14, 10, 10)
    glPopMatrix()

    for side in (-1, 1):
        glPushMatrix()
        color = adjust_brightness(v["skin"], brightness, in_combat, "player")
        glColor3f(*color)
        glTranslatef(15, side * 20, 90)
        glRotatef(90, 0, 1, 0)
        gluCylinder(quad, 8, 6, 30, 10, 1)
        glPopMatrix()

    glPopMatrix()
    draw_weapon(player)


def draw_weapon(player):
    if torch_on or game_over:
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    glRotatef(player_direction, 0, 0, 1)

    glTranslatef(45, -20, 90)
    quad = gluNewQuadric()

    if player.equip == "Dagger":
        glColor3f(0.7, 0.7, 0.7)
        gluCylinder(quad, 2, 1, 25, 8, 1)

    elif player.equip == "Magic Staff":
        glColor3f(0.4, 0.2, 0.1)
        gluCylinder(quad, 3, 3, 40, 8, 8)
        glTranslatef(0, 0, 40)
        glColor3f(0.2, 0.6, 1.0)
        gluSphere(quad, 5, 10, 10)

    elif player.equip == "Greatsword":
        glColor3f(0.5, 0.5, 0.5)
        gluCylinder(quad, 3, 2, 50, 8, 1)

    glPopMatrix()


def draw_projectile(x, y, color):

    glPushMatrix()
    glTranslatef(x, y, 90)
    glColor3f(*color)
    glScalef(1.2, 1, 1)
    glutSolidCube(15)
    glPopMatrix()


def draw_enemies():
    if current_room not in enemies:
        return

    for e in enemies[current_room]:
        if in_combat and e is not combat_state["enemy"]:
            continue
        draw_enemy(e.id, e.x, e.y, e.dir, e.dead)


def draw_enemy(id, x, y, facing, dead):
    brightness = 1.0
    glPushMatrix()
    glTranslatef(x, y, 0)
    if dead:
        glRotatef(-90, 0, 1, 0)

    if id != 2:
        glScalef(1.5, 1.5, 1.5)
    glRotatef(facing, 0, 0, 1)
    quad = gluNewQuadric()

    if id == 0:
        color = adjust_brightness((0.3, 0.55, 0.25), brightness, in_combat, "enemy")
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0, 35)
        glRotatef(-10, 1, 0, 0)
        gluCylinder(quad, 10, 14, 35, 10, 1)
        glPopMatrix()

        color = adjust_brightness((0.55, 0.75, 0.45), brightness, in_combat, "enemy")
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0, 75)
        gluCylinder(quad, 8, 6, 18, 10, 1)
        glPopMatrix()

        color = adjust_brightness((0.55, 0.75, 0.45), brightness, in_combat, "enemy")
        glColor3f(*color)
        for side, length in [(-1, 38), (1, 28)]:
            glPushMatrix()
            glTranslatef(0, side * 18, 35)
            gluCylinder(quad, 4, 4, length, 8, 1)
            glPopMatrix()


        color = adjust_brightness((0.2, 0.4, 0.2), brightness, in_combat, "enemy")
        glColor3f(*color)
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(0, side * 8, 0)
            gluCylinder(quad, 5, 6, 35, 8, 1)
            glPopMatrix()

    elif id == 1:
        color = adjust_brightness((0.85, 0.85, 0.85), brightness, in_combat, "enemy")
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0, 30)
        gluCylinder(quad, 4, 4, 45, 6, 1)
        glPopMatrix()

        for z in range(40, 65, 6):
            glPushMatrix()
            glTranslatef(0, 0, z)
            gluCylinder(quad, 12, 12, 2, 8, 1)
            glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 0, 80)
        gluCylinder(quad, 9, 7, 16, 10, 1)
        glPopMatrix()

        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(0, side * 18, 40)
            gluCylinder(quad, 3, 3, 35, 6, 1)
            glPopMatrix()

        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(0, side * 7, 0)
            gluCylinder(quad, 3, 3, 35, 6, 1)
            glPopMatrix()

    else:
        for side in (-1, 1):
            glPushMatrix()
            color = adjust_brightness((0.75, 0.34, 0.8), brightness, in_combat, "enemy")
            glColor3f(*color)
            glTranslatef(0, side * 20, 40)
            gluCylinder(quad, 4, 10, 30, 10, 10)
            glPopMatrix()

        glPushMatrix()
        color = adjust_brightness((0.5, 0.3, 0.6), brightness, in_combat, "enemy")
        glColor3f(*color)
        glTranslatef(0, 0, 90)
        glScalef(0.7, 1.2, 1.2)
        glutSolidCube(35)
        glPopMatrix()

        glPushMatrix()
        color = adjust_brightness((0.35, 0.25, 0.25), brightness, in_combat, "enemy")
        glColor3f(*color)
        glTranslatef(0, 0, player_head)
        gluSphere(quad, 14, 10, 10)
        glPopMatrix()

        glPushMatrix()
        color = adjust_brightness((0.6, 0.6, 0), brightness, in_combat, "enemy")
        glColor3f(*color)
        glTranslatef(0, 0, player_head + 10)
        glScalef(0.8, 0.8, 0.8)
        gluSphere(quad, 14, 10, 10)
        glPopMatrix()

        for side in (-1, 1):
            glPushMatrix()
            color = adjust_brightness((0.35, 0.25, 0.25), brightness, in_combat, "enemy")
            glColor3f(*color)
            glTranslatef(15, side * 20, 90)
            glRotatef(90, 0, 1, 0)
            gluCylinder(quad, 8, 6, 30, 10, 1)
            glPopMatrix()

    glPopMatrix()


def draw_torch():
    if not torch_on or game_over:
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    glRotatef(player_direction, 0, 0, 1)

    glTranslatef(45, -20, 90)

    glColor3f(0.6, 0.3, 0.1)
    quad = gluNewQuadric()
    gluCylinder(quad, 3, 3, 25, 8, 8)
    glTranslatef(0, 0, 25)
    glColor3f(1.0, 0.7, 0.0)
    gluCylinder(quad, 5, 0, 15, 8, 8)

    glPopMatrix()


def draw_pause_menu():
    if game_intro or game_start or game_over:
        return
    draw_text_box(200, 150, 600, 500, (0.08, 0.08, 0.08))
    draw_text_box(195, 145, 610, 510, (0.3, 0.25, 0.15))
    draw_text_box(200, 150, 600, 500, (0.08, 0.08, 0.08))

    draw_text(430, 600, "GAME PAUSED")

    draw_text(320, 520, f"Attack: {player_type.attack}")
    draw_text(320, 520, f"Defense: {player_type.defense}")
    draw_text(320, 480, f"Sanity: {player_type.sanity}")
    draw_text(320, 440, f"Player Type: {player_type.id}")

    draw_text(300, 360, "Press P or ESC to Resume")
    draw_text(300, 320, "Press E to interact with your surroundings")



def draw_combat_menu():
    draw_text_box(0, 600, 1000, 200, (0.1, 0.1, 0.1))
    draw_text(58, 735, "Fight!")
    draw_text(60, 675, "Run")
    draw_text(320, 735, "Inventory")


def draw_player_moves():
    draw_text_box(0, 600, 1000, 200, (0.1, 0.1, 0.1))
    draw_text(60, 735, f"{player_type.mov1}  (ST {player_type.req1})")
    draw_text(60, 675, f"{player_type.mov2}  (ST {player_type.req2})")


def draw_combat_status():
    draw_text_box(0, 0, 1000, 200)

    draw_text(30, 160, f"Player Health: {player_type.health}")
    draw_segmented_bar(30, 140, 300, 15, player_type.health, 100, (0.1, 0.8, 0.1), (0.8, 0.1, 0.1))

    draw_text(30, 120, f"Player Stamina: {player_type.stamina}")
    draw_segmented_bar(30,100, 300, 15, player_type.stamina, 80, (0.1, 0.4, 0.9))

    for i in range(len(player_type.status)):
        if player_type.status[i] == "Bleeding":
            draw_text(200 + (i * 50), 160, f"BLD", color=(1, 0, 0))
        elif player_type.status[i] == "Infected":
            draw_text(200 + (i * 50), 160, f"INFTD", color=(0, 1, 0))
        else:
            draw_text(200 + (i * 50), 160, f"PSN", color=(0.7, 0, 0.8))


    enemy = combat_state["enemy"]
    full = 80 if enemy.id == 0 else 100 if enemy.id == 1 else 75 if enemy.id == 2 else 200
    draw_text(360, 145, f"{enemy_db.name[enemy.id]} Health: {enemy.health}")
    draw_segmented_bar(360, 125, 300, 15, enemy.health, full, (0.8, 0.1, 0.8))
    draw_text(30, 80, f"You are attacked by {enemy_db.name[enemy.id]}!")


def print_inventory_menu():
    print("You have the following items in your inventory:")

    items = list(player_type.inventory.items())
    for i, (item, count) in enumerate(items, 1):
        print(f"{i}. {item} - {count}")

    print(f"{len(items) + 1}. Back")


def add_chests(room_id, room):
    global chests

    if room_id in chests:
        return

    chests[room_id] = []

    count = room.get("chests", 0)
    if count == 0:
        return

    WALL_PADDING = 120
    w, h = room["width"], room["height"]

    for _ in range(count):
        chest_x = random.uniform(-w / 2 + WALL_PADDING, w / 2 - WALL_PADDING)
        chest_y = random.uniform(-h / 2 + WALL_PADDING, h / 2 - WALL_PADDING)

        chests[room_id].append([chest_x, chest_y, False])


def lock_doors(r, e):
    global interact

    if r in rooms_checked:
        return

    rooms_checked.add(r)
    if len(rooms_checked) == 1:
        interact = False

    room = rooms[r]

    if r == 0:
        for d in room["doors"]:
            d["locked"] = False
        return

    forward_doors = []

    for d in room["doors"]:
        side = d["side"]

        if side == e or d.get("barred") or d.get("bar_target"):
            d["locked"] = False
            continue

        lock = random.random() < 0.3
        d["locked"] = lock

        if not lock:
            continue

        forward_doors.append(d)

        tar = d["target"]
        opp = opposite[side]

        for out_door in rooms[tar]["doors"]:
            if out_door["side"] == opp and out_door["target"] == r:
                out_door["locked"] = lock
                break

    if not forward_doors:
        return

    unlocked_exists = any(
        not d["locked"] for d in room["doors"] if d["side"] != e and not d.get("barred") and not d.get("bar_target"))

    if not unlocked_exists:
        d = random.choice(forward_doors)
        d["locked"] = False

        tar = d["target"]
        opp = opposite[d["side"]]

        for out_door in rooms[tar]["doors"]:
            if out_door["side"] == opp and out_door["target"] == r:
                out_door["locked"] = False
                break


def enemy_hits_wall(nx, ny, room, r=45):
    w, h = room["width"], room["height"]
    return (
        nx < -w/2 + r or
        nx >  w/2 - r or
        ny < -h/2 + r or
        ny >  h/2 - r
    )


def enemy_hits_chest(nx, ny, room_id, r=45):
    if room_id not in chests:
        return False

    for cx, cy, _ in chests[room_id]:
        dx = nx - cx
        dy = ny - cy
        if dx*dx + dy*dy < (r + 40)**2:
            return True
    return False


def enemy_hits_door(x, y, room):
    w, h = room["width"], room["height"]

    for d in room["doors"]:
        s = d["side"]

        if s == "north":
            if abs(x) < DOOR_WIDTH / 2 and y > h / 2 - 120:
                return True

        elif s == "south":
            if abs(x) < DOOR_WIDTH / 2 and y < -h / 2 + 120:
                return True

        elif s == "east":
            if abs(y) < DOOR_WIDTH / 2 and x > w / 2 - 120:
                return True

        elif s == "west":
            if abs(y) < DOOR_WIDTH / 2 and x < -w / 2 + 120:
                return True

    return False


def get_valid_pos(room_id):
    room = rooms[room_id]
    w, h = room["width"], room["height"]

    for _ in range(50):
        x = random.uniform(-w/2 + 100, w/2 - 100)
        y = random.uniform(-h/2 + 100, h/2 - 100)

        if enemy_hits_chest(x, y, room_id) or enemy_hits_door(x, y, room):
            continue

        return x, y

    return 0, 0


def update_enemies(dt):
    if current_room not in enemies or in_combat:
        return

    room = rooms[current_room]

    for e in enemies[current_room]:
        rad = math.radians(e.dir)
        nx = e.x + math.cos(rad) * e.speed * dt
        ny = e.y + math.sin(rad) * e.speed * dt

        if e.dead:
            continue
        elif enemy_hits_wall(nx, ny, room) or enemy_hits_chest(nx, ny, current_room):
            e.dir = (e.dir + 180) % 360
        else:
            e.x = nx
            e.y = ny


def update_flicker(dt):
    global player_black, enemy_black, player_timer, enemy_timer

    if player_flicker:
        player_timer += dt
        if player_timer >= FLICKER_INTERVAL:
            player_black = not player_black
            player_timer = 0.0
    else:
        player_black = False
        player_timer = 0.0

    if enemy_flicker:
        enemy_timer += dt
        if enemy_timer >= FLICKER_INTERVAL:
            enemy_black = not enemy_black
            enemy_timer = 0.0
    else:
        enemy_black = False
        enemy_timer = 0.0


def spawn_enemies(room_id):
    if room_id in enemies:
        return

    enemies[room_id] = []

    count = rooms[room_id].get("enemies", 0)
    if count == 0:
        return

    for _ in range(count):
        id = enemy_db.spawn_enemy()
        x, y = get_valid_pos(room_id)
        enemies[room_id].append(EnemyInstance(id, x, y))


def stage_combat(enemy):
    global player_direction
    combat_state["player_pos"] = tuple(player_pos)
    combat_state["player_dir"] = player_direction
    combat_state["enemy_pos"] = (enemy.x, enemy.y)
    combat_state["enemy_dir"] = enemy.dir

    r = math.radians(player_direction)
    fx, fy = math.cos(r), math.sin(r)


    player_pos[0] = -fx * 120
    player_pos[1] = -fy * 100

    enemy.x = fx * 120
    enemy.y = fy * 100

    enemy.dir = (player_direction + 180) % 360


def spawn_player(side, w, h):
    xy = {
        "north": (0, h / 2 - 100),
        "south": (0, -h / 2 + 100),
        "east": (w / 2 - 100, 0),
        "west": (-w / 2 + 100, 0)
    }

    return xy[side]


def door_in_front(room):
    w, h = room["width"], room["height"]

    for d in room["doors"]:
        s = d["side"]
        if s == "north" and abs(player_pos[0]) < DOOR_WIDTH / 2 and player_pos[1] > h / 2 - 55:
            return True, d
        if s == "south" and abs(player_pos[0]) < DOOR_WIDTH / 2 and player_pos[1] < -h / 2 + 55:
            return True, d
        if s == "east" and abs(player_pos[1]) < DOOR_WIDTH / 2 and player_pos[0] > w / 2 - 55:
            return True, d
        if s == "west" and abs(player_pos[1]) < DOOR_WIDTH / 2 and player_pos[0] < -w / 2 + 55:
            return True, d

    return False, d


def chest_collision(x, y):
    if current_room not in chests:
        return None

    for i, chest in enumerate(chests[current_room]):
        cx, cy, opened = chest
        dx = x - cx
        dy = y - cy
        if dx * dx + dy * dy < 85 ** 2:
            return i

    return None


def enemy_collision():
    global in_combat, interact
    if combat_cooldown > 0 or (game_start and not rooms_checked):
        return False

    for e in enemies.get(current_room, []):
        if e.dead:
            return False

        dx = player_pos[0] - e.x
        dy = player_pos[1] - e.y
        if dx*dx + dy*dy < 85 ** 2:
            start_combat(e)
            return True


def dead_collision():
    for e in enemies.get(current_room, []):
        dx = player_pos[0] - e.x
        dy = player_pos[1] - e.y
        if e.dead:
            if dx*dx + dy*dy < 90 ** 2:
                return True, e

    return False, EnemyInstance(0, 6000, 6000)


def start_combat(enemy):
    global combat_state, in_combat, interact

    stage_combat(enemy)
    in_combat = True
    interact = True

    combat_state["phase"] = "menu"
    combat_state["enemy"] = enemy

    p_speed = player_type.att_speed
    e_speed = enemy_db.att_speed[enemy.id]

    combat_state["turn"] = ("player" if p_speed >= e_speed else "enemy")


def add_move_effect(who, move):
    id = combat_state["enemy"].id
    color = (0.85, 0.85, 0.85) if player_type.equip == "Greatsword" else (0.5, 0.2, 0.2) if player_type.equip == "Dagger" else (0, 0, 0.75) if player_type.equip == "Magic Staff" else (1, 1, 1)
    if who == "player":
        print(f"You used {player_type.mov1 if move == 1 else player_type.mov2}!")
        miss = random.randint(1, 100) < 20
        if miss:
            print("You missed!")
            return
        dmg = player_type.dmg1 if move == 1 else None
        if dmg is not None:
            projectile.append({
                "x1": player_pos[0], "y1": player_pos[1],
                "x2": combat_state["enemy"].x, "y2": combat_state["enemy"].y,
                "t": 0.0,
                "speed": 2,
                "color": color,
                "target": "enemy"
            })
            dmg = int(dmg * (100 / (100 + enemy_db.defense[id])))
            combat_state["enemy"].health -= max(0, dmg)
        else:
            player_type.defense += 5
        player_type.stamina -= player_type.req1 if move == 1 else player_type.req2

    else:
        print(f"{enemy_db.name[id]} used "f"{enemy_db.mov1[id] if move == 1 else enemy_db.mov2[id]}!")
        chance = random.randint(1, 100)
        miss = chance < 25 if id == 0 else chance > 30 if id == 1 else chance > 60 if id == 2 else chance > 10
        if miss:
            print(f"{enemy_db.name[id]} missed!")
            return
        dmg = enemy_db.dmg1[id] if move == 1 else None
        color = (1, 1, 1) if move == 1 else (0.45, 0.4, 0)
        if dmg is not None or move == "Skeleton's Wails":
            projectile.append({
                "x1": combat_state["enemy"].x, "y1": combat_state["enemy"].y,
                "x2": player_pos[0], "y2": player_pos[1],
                "t": 0.0,
                "speed": 2,
                "color": color,
                "target": "player"
            })
        if dmg is not None:
            dmg = int(dmg * (100 / (100 + player_type.defense)))
            player_type.health -= max(0, dmg)
        if enemy_db.mov1[id] == "Filthy Strike" and dmg is not None:
            player_type.add_status_effect("Infected")
        if enemy_db.mov1[id] == "Quick Stab":
            player_type.add_status_effect("Bleeding")
        if dmg is None:
            if enemy_db.mov2[id] == "Vomit Throw":
                player_type.add_status_effect("Poisoned")
            elif enemy_db.mov2[id] == "Skeleton's Wails":
                player_type.defense -= 10
                print("Your bones shiver from the terrifying noise.")
        if in_combat:
            player_type.status_damage()


def attempt_run():
    roll = random.randint(0, 100)
    if roll < player_type.run:
        print("You successfully escaped!")
        end_combat()
    else:
        print("Failed to escape!")
        enemy_turn()


def player_turn(n, torch):
    global torch_on
    if torch:
        print("Your turn is wasted as you scramble to grab your weapon")
        torch_on = False
    elif n == 1 and player_type.stamina < player_type.req1:
        print("Not enough stamina!")
    elif n == 2 and player_type.stamina < player_type.req2:
        print("Not enough stamina!")
    else:
        add_move_effect("player", n)

    combat_state["phase"] = "resolve"
    combat_state["turn"] = "enemy"
    enemy_turn()


def enemy_turn():
    if combat_state["enemy"].health <= 0:
        enemy_died()
        return

    move = random.choice([1, 2])
    add_move_effect("enemy", move)

    if player_type.health <= 0:
        player_died()
        return

    combat_state["phase"] = "menu"
    combat_state["turn"] = "player"


def player_died():
    global in_combat, game_over

    print("You have been defeated.\n")
    projectile.pop()
    in_combat = False
    combat_state["enemy"] = None
    game_over = True


def enemy_died():
    enemy = combat_state["enemy"]
    print(f"{enemy_db.name[enemy.id]} defeated!\n")
    projectile.pop()
    enemy.dead = True

    end_combat()


def end_combat():
    global in_combat, interact, player_direction, camera_angle, combat_cooldown, player_flicker, enemy_flicker

    player_pos[0], player_pos[1] = combat_state["player_pos"]
    player_direction = combat_state["player_dir"]
    enemy = combat_state["enemy"]
    enemy.x, enemy.y = combat_state["enemy_pos"]
    enemy.dir  = combat_state["enemy_dir"]

    combat_state["active"] = False
    combat_state["enemy"] = None
    combat_state["turn"] = None
    combat_state["phase"] = None

    in_combat = False
    interact = False
    player_flicker = False
    enemy_flicker = False

    camera_pos[:] = [0, 450, 450]
    camera_angle = 0
    combat_cooldown = 2


def handle_combat(x, y):
    global player_flicker, enemy_flicker
    if combat_state["turn"] == "enemy":
        return
    if combat_state["phase"] == "menu":
        if inside(x, y, COMBAT_FIGHT_BTN):
            combat_state["phase"] = "choose_move"
            player_flicker = False
            enemy_flicker = False

        elif inside(x, y, COMBAT_RUN_BTN):
            player_flicker = False
            enemy_flicker = False
            attempt_run()

        elif inside(x, y, COMBAT_INVENTORY_BTN):
            combat_state["phase"] = "inventory"
            print_inventory_menu()

    elif combat_state["phase"] == "choose_move":
        if inside(x, y, MOVE1_BTN):
            player_turn(1, torch_on)

        elif inside(x, y, MOVE2_BTN):
            player_turn(2, torch_on)


def inside(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def chest_opened():
    global rec, chest_idx

    if chest_idx is None:
        return False

    if chests[current_room][chest_idx][2]:
        return False

    chests[current_room][chest_idx][2] = True
    item = random.choice(list(ITEMS.keys()))
    item = random.choice([item, "Healing Potion", item])
    player_type.add_item(item)
    rec = item
    chest_idx = None
    return True


def loot_enemy(enemy):
    global loot1, loot2

    if enemy.looted or not interact:
        return False

    enemy.looted = True
    loot1 = random.choice(list(ITEMS.keys()))
    player_type.add_item(loot1)
    loot2 = random.choice(list(ITEMS.keys()))
    player_type.add_item(loot2)
    return True


def room_transition():
    global current_room, player_pos, bar_removed

    room = rooms[current_room]

    hit, door = door_in_front(room)
    if not hit or door["locked"] or door.get("barred") or door.get("bar_target"):
        return

    prev_room = current_room
    current_room = door["target"]

    if bar_removed:
        bar_removed = False
        opp = opposite[door["side"]]

        for d in rooms[current_room]["doors"]:
            if d["side"] == opp and d["target"] == prev_room:
                d.pop("barred", None)
                break

    entry_side = opposite[door["side"]]
    lock_doors(current_room, entry_side)

    new_room = rooms[current_room]
    nw, nh = new_room["width"], new_room["height"]

    for out_door in new_room["doors"]:
        if out_door["target"] == prev_room:
            player_pos[:] = spawn_player(out_door["side"], nw, nh)
            return


def game_restart():
    global player_pos, player_direction, game_intro, game_start, game_over, enemies, enemy_db, current_room, combat_cooldown, camera_pos, camera_angle, camera_zoom, interact, torch_on, paused

    player_pos = [0.0, 0.0]
    player_direction = 270
    game_intro = True
    game_start = True
    game_over = False
    enemies = {}
    enemy_db = None
    current_room = 0
    combat_cooldown = 0.0

    camera_pos = [0, 450, 450]
    camera_angle = 0
    camera_zoom = 1

    interact = False
    torch_on = False
    paused = False


def keyboard(key, x, y):
    global player_direction, in_combat, interact, is_locked, is_barred1, is_barred2, bar_removed, open_chest, lootable, chest_idx, item_rec, loot_rec, game_over
    global torch_on, paused

    if in_combat and combat_state["phase"] == "inventory":
        if key in b'123456789':
            idx = int(key.decode()) - 1
            items = list(player_type.inventory.keys())

            if idx == len(items):
                combat_state["phase"] = "menu"
                print("Leaving Inventory.")
                return


            if 0 <= idx < len(items):
                item = items[idx]
                used = player_type.use_item(item)
                if used:
                    combat_state["phase"] = "resolve"
                    combat_state["turn"] = "enemy"
                    enemy_turn()
                return

        return

    room = rooms[current_room]
    w, h = room["width"], room["height"]
    if game_start:
        return


    if key == b'p' or key == b'\x1b':
        paused = not paused
        return


    if key == b't':
        torch_on = not torch_on if not game_over else False
        return

    if key == b'r' and game_over:
        game_restart()

    if in_combat:
        return

    r = math.radians(player_direction)
    dx = player_speed * dt * math.cos(r) * player_type.walk_speed
    dy = player_speed * dt * math.sin(r) * player_type.walk_speed

    if key == b'w':
        nx = player_pos[0] + dx
        ny = player_pos[1] + dy
        player_type.sanity -= 0.01
        if player_type.sanity <= 0:
            game_over = True

        nx = max(-w / 2 + 50, min(w / 2 - 50, nx))
        ny = max(-h / 2 + 50, min(h / 2 - 50, ny))

        idx = chest_collision(nx, ny)
        hit, enemy = dead_collision()
        if idx is None and not hit and not game_over:
            player_pos[0], player_pos[1] = nx, ny
            open_chest = False
            lootable = False
        elif idx is not None:
            open_chest = True
            chest_idx = idx
        elif hit:
            player_pos[0], player_pos[1] = nx, ny
            lootable = True

        hit, door = door_in_front(room)
        is_locked = True if hit and door["locked"] else False
        is_barred1 = True if hit and door.get("barred") else False
        is_barred2 = False if hit and is_barred1 else is_barred2
        is_barred2 = True if hit and door.get("bar_target") else False
        is_barred1 = False if hit and is_barred2 else is_barred1

    elif key == b's':
        nx = player_pos[0] - dx
        ny = player_pos[1] - dy

        nx = max(-w / 2 + 50, min(w / 2 - 50, nx))
        ny = max(-h / 2 + 50, min(h / 2 - 50, ny))

        idx = chest_collision(nx, ny)
        if idx is None and not game_over:
            player_pos[0], player_pos[1] = nx, ny
            open_chest = False
            lootable = False
            interact = False

        if is_locked:
            is_locked = False
        if is_barred1:
            is_barred1 = False
        if is_barred2:
            is_barred2 = False

    elif key == b'a':
        player_direction = (player_direction + 45) % 360
    elif key == b'd':
        player_direction = (player_direction - 45) % 360

    elif key == b'e':
        hit1, door = door_in_front(room)
        hit2, enemy = dead_collision()
        chest = chest_collision(player_pos[0], player_pos[1])
        interact = not interact if hit1 or hit2 or open_chest else interact
        if hit1 and is_barred2:
            if door.get("bar_target"):
                door.pop("bar_target")
                bar_removed = True
        if open_chest:
            item_rec = chest_opened()
        if lootable:
            loot_rec = loot_enemy(enemy)


def mouse(button, state, x, y):
    global game_start, game_intro, player_type, interact

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        x, y = x, 800 - y
        if in_combat:
            handle_combat(x, y)
            return

        if game_intro:
            game_intro = False

        elif game_start and not game_intro:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()

            gluOrtho2D(0, 1000, 0, 800)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            if 415 <= x <= 415 + 55 and 335 <= y <= 335 + 40:
                player_type = Player("Mage")
                game_start = False
            elif 485 <= x <= 485 + 65 and 335 <= y <= 335 + 40:
                player_type = Player("Rogue")
                game_start = False
            elif 565 <= x <= 565 + 70 and 335 <= y <= 335 + 40:
                player_type = Player("Warrior")
                game_start = False
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

        if door_prompt["active"]:
            if inside(x, y, YES_BTN):
                item = door_prompt["item"]

                used = player_type.use_item(item)

                door_prompt["active"] = False
                door_prompt["item"] = None
                return

            if inside(x, y, NO_BTN):
                door_prompt["active"] = False
                door_prompt["item"] = None
                door_prompt["door"] = None
                interact = False
                return


def special(key, x, y):
    global camera_angle, camera_zoom

    if in_combat:
        return

    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 10) % 360
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 10) % 360


def setucamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, 1.25, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if in_combat:

        rad = math.radians(player_direction)
        x = player_pos[0] + math.cos(rad) * (-150) - math.sin(-rad) * 175
        y = player_pos[1] + math.sin(rad) * (-150) - math.cos(rad) * 175
        z = player_head + 40

        look_x = x + math.cos(rad)
        look_y = y + math.sin(rad)

        gluLookAt(x, y, z, look_x, look_y, z, 0, 0, 1)

    else:
        r = math.radians(camera_angle)
        x = camera_pos[0] * math.cos(r) - camera_pos[1] * math.sin(r)
        y = camera_pos[0] * math.sin(r) + camera_pos[1] * math.cos(r)
        z = camera_pos[2] * camera_zoom

        gluLookAt(x, y + player_pos[1], z, player_pos[0], player_pos[1], -500, 0, 0, 1)


def idle():
    global last, dt, combat_cooldown, player_flicker, enemy_flicker

    if paused:
        glutPostRedisplay()
        return

    now = time.time()
    dt = now - last
    last = now

    if combat_cooldown > 0:
        combat_cooldown -= dt

    for p in projectile[:]:
        p["t"] += p["speed"] * dt

        if p["t"] >= 1.0:
            enemy_flicker = True if p["target"] == "enemy" else enemy_flicker
            player_flicker = True if p["x2"] == player_pos[0] else player_flicker
            projectile.remove(p)

    room_transition()
    update_enemies(dt)

    if not game_over:
        update_flicker(dt)
        enemy_collision()
        dead_collision()

    glutPostRedisplay()


def display():
    global enemy_db, rec
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    setucamera()

    room = rooms[current_room]
    for p in projectile:
        x = p["x1"] + (p["x2"] - p["x1"]) * p["t"]
        y = p["y1"] + (p["y2"] - p["y1"]) * p["t"]
        draw_projectile(x, y, p["color"])

    if game_intro:
        draw_text(400, 400, "Dungeon of the Forgotten")
        draw_text(420, 200, "Click anywhere to play", GLUT_BITMAP_8_BY_13)

    elif game_start and not game_intro:
        enemy_db = EnemyDB()
        draw_text_box(445, 395, 145, 40, (1, 0, 0))
        draw_text(450, 410, "Choose a player", GLUT_BITMAP_HELVETICA_18)
        draw_text_box(400, 335, 55, 40, (1, 0, 0))
        draw_text(405, 350, "Mage", GLUT_BITMAP_HELVETICA_18)
        draw_text_box(485, 335, 65, 40, (1, 0, 0))
        draw_text(490, 350, "Rogue", GLUT_BITMAP_HELVETICA_18)
        draw_text_box(575, 335, 70, 40, (1, 0, 0))
        draw_text(580, 350, "Warrior", GLUT_BITMAP_HELVETICA_18)

    else:
        draw_floor(room["width"], room["height"], room["floor"])
        draw_enemies()
        if current_room == 0:
            draw_walls(room, True)
        else:
            draw_walls(room)

        for d in room["doors"]:
            if current_room == 0:
                draw_door(d, room, (0.18, 0.1, 0.08))
                continue

            draw_door(d, room)

        add_chests(current_room, room)
        draw_chests(current_room)
        spawn_enemies(current_room)
        draw_player(player_type)
        draw_torch()

        if not in_combat and not game_start and not game_intro and not game_over:
            draw_text(60, 735, f"Player Health: {player_type.health}", ui=True)
            draw_segmented_bar(60, 700, 300, 15, player_type.health, 100, (0.1, 0.8, 0.1), (0.8, 0.1, 0.1), ui=True)
            draw_text(60, 680, f"Player Sanity: {int(player_type.sanity)}", ui=True)
            draw_segmented_bar(60, 655, 300, 15, player_type.sanity, 100, (0.9, 0.4, 0.9), ui=True)
            draw_text(380, 735, f"Player Stamina: {player_type.stamina}", ui=True)
            draw_segmented_bar(380, 700, 300, 15, player_type.stamina, 80, (0.1, 0.4, 0.9), ui=True)

        if is_locked and not in_combat:
            draw_text_box(0, 0, 1000, 200)
            draw_text(30, 140, "This door is locked.")

            if "Key" in player_type.inventory:
                draw_text(30, 120, "You have a key, would you like to use it? Click on Yes or No to choose:")
                door_prompt["active"] = True
                door_prompt["item"] = "Key"
                draw_text(30, 100, "Yes")
                draw_text(100, 100, "No")

            elif "Lockpick" in player_type.inventory:
                draw_text(30, 120, "You have a lockpick, would you like to try your luck?  Click on Yes or No to choose:")
                door_prompt["active"] = True
                door_prompt["item"] = "Lockpick"
                draw_text(30, 100, "Yes")
                draw_text(100, 100, "No")

        if is_barred1 and not in_combat:
            draw_text_box(0, 0, 1000, 200)
            draw_text(30, 140, "The door is barred from the other side. You cannot open it.")
        if is_barred2 and not in_combat:
            draw_text_box(0, 0, 1000, 200)
            draw_text(30, 140, "You remove the bar and walk through it")
        if open_chest and not in_combat:
            draw_text_box(0, 0, 1000, 200)
            if not item_rec:
                draw_text(30, 140, f"You already opened the chest.")
            else:
                draw_text(30, 140, f"You open the chest and received {rec}.")
        if lootable and not in_combat:
            draw_text_box(0, 0, 1000, 200)
            if not loot_rec:
                draw_text(30, 140, f"You already looted the monster.")
            else:
                draw_text(30, 140, f"You search the monster and received {loot1} and {loot2}.")

        if in_combat:
            draw_combat_status()
            if combat_state["phase"] == "menu":
                draw_combat_menu()
            elif combat_state["phase"] == "choose_move":
                draw_player_moves()

        if paused:
            draw_pause_menu()

        if game_over:
            draw_text_box(0, 0, 1000, 200, (1, 0, 0))
            draw_text(30, 140, "GAME OVER, YOU DIED! PRESS R TO PLAY AGAIN", (0, 0, 0))

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(525, 0)
    glutCreateWindow(b'Dungeon of the Forgotten')
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()