"""Game mode art for Carryover: the reward items and the small decorations for the backgrounds.

Plain shapes only (no brands, no known characters, no people). Every item is written once as a
list of shapes and turned into two files:
  frontend/public/game/<id>.svg          still picture (used when Animations is Off)
  frontend/public/animations/<id>.json   Lottie animation (a gentle sway, bob, spin or drift)
The bird, balloon and kite animations were made earlier by hand and are kept as they are.

Run from the repo root:  python3 tools/make_game_art.py
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "public")
GAME = os.path.join(ROOT, "game")
ANIM = os.path.join(ROOT, "animations")
os.makedirs(GAME, exist_ok=True)
os.makedirs(ANIM, exist_ok=True)


def ell(cx, cy, w, h, color):
    return ("ell", cx, cy, w, h, color)


def poly(points, color):
    return ("poly", points, color)


def rect(x, y, w, h, color):
    return ("poly", [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color)


def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1]


# ---- the items: each is (shapes, motion). Motion is sway, bob, spin or drift. ----
RED, GREEN, GOLD, BLUE, ORANGE, CREAM, BROWN, PINK, INK = (
    "#c8534a", "#6fae7c", "#e5c66b", "#7a9cc6", "#d9825b", "#f3ead8", "#8a5a34", "#e9a6b4", "#3d4a57")

ITEMS = {
    # space
    "rocket": ([ell(50, 50, 26, 54, "#e8edf2"), poly([(37, 32), (50, 6), (63, 32)], ORANGE),
                poly([(32, 62), (16, 82), (38, 74)], ORANGE), poly([(68, 62), (84, 82), (62, 74)], ORANGE),
                ell(50, 46, 12, 12, BLUE), poly([(42, 78), (50, 96), (58, 78)], "#e5a23a")], "bob"),
    "satellite": ([rect(40, 40, 20, 20, "#cfd3d7"), rect(6, 45, 30, 10, BLUE), rect(64, 45, 30, 10, BLUE),
                   ell(50, 32, 18, 10, "#e9edf0"), rect(49, 22, 2, 10, "#9aa1a7")], "sway"),
    "comet": ([poly([(62, 36), (8, 70), (70, 48)], "#e9d9a8"), ell(68, 38, 24, 24, "#f6d88a")], "drift"),
    "planet": ([ell(50, 50, 56, 56, ORANGE), rect(20, 44, 60, 6, "#e9a07a"), rect(24, 58, 52, 5, "#b8663d"),
                ell(50, 50, 96, 12, GOLD)], "spin"),
    # animals: cat
    "yarn": ([ell(48, 50, 56, 56, ORANGE), ell(40, 42, 22, 14, "#e9a07a"), ell(58, 60, 24, 10, "#b8663d"),
              poly([(70, 72), (94, 84), (92, 90), (66, 78)], ORANGE)], "spin"),
    "fish": ([poly([(64, 50), (94, 32), (94, 68)], BLUE), ell(42, 50, 56, 32, BLUE), ell(30, 46, 7, 7, INK),
              ell(46, 50, 18, 10, "#9fb9d8")], "sway"),
    "bell": ([ell(50, 50, 46, 46, GOLD), ell(50, 80, 12, 12, "#b8993f"), rect(30, 52, 40, 3, "#b8993f"),
              ell(50, 22, 14, 10, "#b8993f")], "sway"),
    # animals: dog
    "bone": ([rect(24, 40, 52, 20, "#d9bf8e"), ell(22, 38, 20, 20, "#d9bf8e"), ell(22, 62, 20, 20, "#d9bf8e"),
              ell(78, 38, 20, 20, "#d9bf8e"), ell(78, 62, 20, 20, "#d9bf8e")], "sway"),
    "ball": ([ell(50, 50, 56, 56, ORANGE), ell(50, 50, 56, 8, "#ffffff"), ell(36, 36, 14, 10, "#e9a07a")], "bob"),
    "bowl": ([poly([(12, 46), (88, 46), (76, 82), (24, 82)], BLUE), ell(50, 46, 76, 14, "#9fb9d8"),
              ell(40, 42, 12, 8, BROWN), ell(54, 40, 12, 8, BROWN), ell(62, 44, 10, 6, BROWN)], "bob"),
    # animals: fox
    "acorn": ([ell(50, 62, 38, 44, "#b8793f"), ell(50, 42, 46, 24, "#7a4f2a"), rect(48, 20, 4, 12, "#7a4f2a")], "sway"),
    "leaf": ([poly([(50, 6), (80, 40), (64, 90), (36, 90), (20, 40)], ORANGE),
              rect(49, 30, 3, 58, "#b8663d")], "sway"),
    "mushroom": ([rect(40, 50, 20, 38, CREAM), ell(50, 44, 70, 44, ORANGE), ell(36, 40, 12, 10, "#ffffff"),
                  ell(58, 34, 14, 10, "#ffffff"), ell(64, 48, 9, 7, "#ffffff")], "bob"),
    # fruits: apple
    "apple": ([ell(38, 58, 42, 46, RED), ell(62, 58, 42, 46, RED), rect(48, 16, 4, 16, "#7a4f2a"),
               poly([(52, 26), (76, 10), (70, 32)], GREEN)], "sway"),
    "apple-leaf": ([poly([(50, 6), (82, 42), (62, 92), (38, 92), (18, 42)], GREEN), rect(49, 30, 3, 58, "#4e8a5b")], "sway"),
    "blossom": ([ell(50, 26, 26, 30, "#f6d8e0"), ell(74, 44, 30, 26, "#f6d8e0"), ell(66, 72, 26, 30, "#f6d8e0"),
                 ell(34, 72, 26, 30, "#f6d8e0"), ell(26, 44, 30, 26, "#f6d8e0"), ell(50, 52, 18, 18, GOLD)], "spin"),
    # fruits: strawberry
    "strawberry": ([poly([(20, 36), (80, 36), (50, 92)], "#d6455b"), ell(50, 38, 62, 28, "#d6455b"),
                    ell(36, 52, 5, 7, "#f6d88a"), ell(52, 60, 5, 7, "#f6d88a"), ell(62, 46, 5, 7, "#f6d88a"),
                    ell(46, 74, 5, 7, "#f6d88a"), poly([(30, 30), (50, 12), (70, 30), (50, 36)], GREEN)], "sway"),
    "daisy": ([ell(50, 24, 22, 28, "#f6e3b8"), ell(76, 42, 28, 22, "#f6e3b8"), ell(66, 74, 22, 28, "#f6e3b8"),
               ell(34, 74, 22, 28, "#f6e3b8"), ell(24, 42, 28, 22, "#f6e3b8"), ell(50, 52, 20, 20, GOLD)], "spin"),
    "jar": ([rect(26, 34, 48, 52, "#e9a6b4"), rect(22, 22, 56, 14, GOLD), rect(32, 50, 36, 22, "#ffffff"),
             ell(50, 61, 16, 10, "#d6455b")], "bob"),
    # fruits: mango
    "mango": ([ell(50, 56, 46, 58, "#e5a23a"), ell(40, 50, 20, 32, "#f0c15e"), poly([(52, 16), (82, 8), (70, 30)], GREEN)], "sway"),
    "mango-slice": ([ell(50, 56, 70, 46, "#f0c15e"), ell(50, 56, 56, 32, "#e5a23a"), ell(50, 56, 30, 16, "#f0c15e")], "bob"),
    "apple-basket": ([poly([(12, 50), (88, 50), (78, 90), (22, 90)], "#b8793f"), rect(18, 62, 64, 4, "#8a5a34"),
                      rect(20, 74, 60, 4, "#8a5a34"), ell(32, 44, 28, 28, RED), ell(52, 38, 30, 30, RED),
                      ell(70, 46, 26, 26, RED), poly([(50, 22), (62, 12), (58, 26)], GREEN)], "bob"),
    "apple-pie": ([ell(50, 66, 88, 34, "#e0a96a"), ell(50, 60, 72, 24, RED), rect(20, 54, 60, 5, "#e0a96a"),
                   rect(20, 63, 60, 5, "#e0a96a"), rect(32, 46, 5, 36, "#e0a96a"), rect(48, 46, 5, 36, "#e0a96a"),
                   rect(64, 46, 5, 36, "#e0a96a")], "bob"),
    "berry-basket": ([poly([(14, 48), (86, 48), (76, 90), (24, 90)], "#d9a07a"), rect(20, 62, 60, 4, "#b8794f"),
                      rect(24, 76, 52, 4, "#b8794f"), ell(32, 42, 26, 24, "#d6455b"), ell(52, 38, 26, 24, "#d6455b"),
                      ell(70, 44, 24, 22, "#d6455b"), ell(44, 30, 8, 8, GREEN)], "bob"),
    "shortcake": ([rect(16, 54, 68, 30, "#f3e2b8"), rect(16, 48, 68, 10, "#ffffff"), rect(16, 74, 68, 6, "#ffffff"),
                   ell(50, 38, 24, 26, "#d6455b"), poly([(40, 28), (50, 16), (60, 28)], GREEN)], "bob"),
    "mango-glass": ([poly([(26, 26), (74, 26), (64, 90), (36, 90)], "#f0c15e"), ell(50, 26, 48, 9, "#f6d88a"),
                     rect(60, 6, 5, 42, "#d6455b"), ell(50, 60, 22, 12, "#e5a23a")], "sway"),
    "mango-bowl": ([poly([(10, 52), (90, 52), (78, 88), (22, 88)], "#7a9cc6"), rect(26, 38, 16, 16, "#e5a23a"),
                    rect(44, 32, 16, 16, "#f0c15e"), rect(62, 38, 16, 16, "#e5a23a"), rect(36, 44, 14, 12, "#f0c15e")], "bob"),
    "mango-leaf": ([poly([(8, 56), (50, 16), (92, 56), (50, 84)], GREEN), rect(10, 54, 80, 3, "#4e8a5b")], "sway"),
}

# Faint decorations for the backgrounds (a single colour; dark mode inverts them).
DECOR = {
    "paw": [ell(50, 66, 34, 28, "#000000"), ell(24, 40, 14, 18, "#000000"), ell(40, 24, 14, 18, "#000000"),
            ell(60, 24, 14, 18, "#000000"), ell(76, 40, 14, 18, "#000000")],
    "cat-face": [ell(50, 56, 70, 56, "#000000"), poly([(20, 40), (24, 8), (46, 28)], "#000000"),
                 poly([(80, 40), (76, 8), (54, 28)], "#000000")],
    "dog-face": [ell(50, 54, 56, 60, "#000000"), ell(20, 56, 22, 44, "#000000"), ell(80, 56, 22, 44, "#000000")],
    "fox-face": [poly([(8, 12), (30, 30), (50, 26), (70, 30), (92, 12), (84, 62), (50, 94), (16, 62)], "#000000")],
}


def svg_of(shapes, size=100):
    parts = []
    for s in shapes:
        if s[0] == "ell":
            _, cx, cy, w, h, c = s
            parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}" fill="{c}"/>')
        else:
            _, pts, c = s
            parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{c}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">{"".join(parts)}</svg>'


def lottie_of(name, shapes, motion):
    def tr():
        return {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]},
                "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}

    def group(s):
        if s[0] == "ell":
            _, cx, cy, w, h, c = s
            geo = {"ty": "el", "p": {"a": 0, "k": [cx, cy]}, "s": {"a": 0, "k": [w, h]}}
        else:
            _, pts, c = s
            n = len(pts)
            geo = {"ty": "sh", "ks": {"a": 0, "k": {"i": [[0, 0]] * n, "o": [[0, 0]] * n, "v": [list(p) for p in pts], "c": True}}}
        return {"ty": "gr", "it": [geo, {"ty": "fl", "c": {"a": 0, "k": rgb(c)}, "o": {"a": 0, "k": 100}, "r": 1}, tr()]}

    ease = {"i": {"x": [0.45], "y": [1]}, "o": {"x": [0.55], "y": [0]}}
    linear = {"i": {"x": [1], "y": [1]}, "o": {"x": [0], "y": [0]}}
    rot = {"a": 0, "k": 0}
    pos = {"a": 0, "k": [50, 50, 0]}
    if motion == "sway":
        rot = {"a": 1, "k": [dict(ease, t=0, s=[-8]), dict(ease, t=30, s=[8]), {"t": 60, "s": [-8]}]}
    elif motion == "spin":
        rot = {"a": 1, "k": [dict(linear, t=0, s=[0]), {"t": 120, "s": [360]}]}
    elif motion == "bob":
        pos = {"a": 1, "k": [dict(ease, t=0, s=[50, 54, 0], to=[0, 0, 0], ti=[0, 0, 0]),
                             dict(ease, t=30, s=[50, 46, 0], to=[0, 0, 0], ti=[0, 0, 0]),
                             {"t": 60, "s": [50, 54, 0]}]}
    elif motion == "drift":
        pos = {"a": 1, "k": [dict(ease, t=0, s=[44, 52, 0], to=[0, 0, 0], ti=[0, 0, 0]),
                             dict(ease, t=30, s=[58, 46, 0], to=[0, 0, 0], ti=[0, 0, 0]),
                             {"t": 60, "s": [44, 52, 0]}]}
    layer = {"ddd": 0, "ind": 1, "ty": 4, "nm": name, "sr": 1,
             "ks": {"o": {"a": 0, "k": 100}, "r": rot, "p": pos, "a": {"a": 0, "k": [50, 50, 0]},
                    "s": {"a": 0, "k": [100, 100, 100]}},
             "ao": 0, "shapes": [group(s) for s in reversed(shapes)], "ip": 0, "op": 120 if motion == "spin" else 60, "st": 0, "bm": 0}
    return {"v": "5.7.4", "fr": 30, "ip": 0, "op": layer["op"], "w": 100, "h": 100, "nm": name, "ddd": 0, "assets": [], "layers": [layer]}


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


for name, (shapes, motion) in ITEMS.items():
    write(os.path.join(GAME, f"{name}.svg"), svg_of(shapes))
    with open(os.path.join(ANIM, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(lottie_of(name, shapes, motion), f)
for name, shapes in DECOR.items():
    write(os.path.join(GAME, f"{name}.svg"), svg_of(shapes))

# Still pictures for the sky items (their Lottie files were made earlier by hand).
write(os.path.join(GAME, "bird.svg"), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 24"><path d="M2 14 Q10 4 20 12 Q30 4 38 14 Q30 10 20 18 Q10 10 2 14 Z" fill="#3d4a57"/></svg>')
write(os.path.join(GAME, "balloon.svg"), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 44"><path d="M15 2 C25 2 28 10 28 16 C28 24 20 29 15 30 C10 29 2 24 2 16 C2 10 5 2 15 2 Z" fill="#d9825b" stroke="#a85f3d"/><path d="M15 2 C11 8 11 24 15 30 C19 24 19 8 15 2 Z" fill="#e9b27a"/><path d="M9 29 L12 36 M21 29 L18 36" stroke="#6b4f3a"/><rect x="11" y="36" width="8" height="6" rx="1" fill="#8a6a4f"/></svg>')
write(os.path.join(GAME, "kite.svg"), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 44"><path d="M15 2 L27 16 L15 30 L3 16 Z" fill="#6fae7c" stroke="#4e8a5b"/><path d="M15 2 L15 30 M3 16 L27 16" stroke="#e9f3eb"/><path d="M15 30 q-4 4 0 7 q4 3 0 6" fill="none" stroke="#4e8a5b" stroke-width="1.5"/></svg>')
write(os.path.join(GAME, "rainbow.svg"), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 24"><path d="M3 22 A17 17 0 0 1 37 22" fill="none" stroke="#d9825b" stroke-width="3"/><path d="M7 22 A13 13 0 0 1 33 22" fill="none" stroke="#e5c66b" stroke-width="3"/><path d="M11 22 A9 9 0 0 1 29 22" fill="none" stroke="#6fae7c" stroke-width="3"/><path d="M15 22 A5 5 0 0 1 25 22" fill="none" stroke="#7a9cc6" stroke-width="3"/></svg>')
print(f"wrote {len(ITEMS)} items and {len(DECOR)} decorations")
