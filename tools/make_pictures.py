"""Draw the simple step pictures (SVG) used by the task files and skill cards.

Our own drawings, so no license is needed. Calm colors, adult style, no people's
faces, no real cards, card numbers, bank apps or brands.

Run from the repo root:  python tools/make_pictures.py
Writes to frontend/public/img/.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "frontend" / "public" / "img"

INK = "#2b2a28"
LINE = "#5c574e"
SOFT = "#f6f4ef"
SAGE = "#5f7f6a"
SAGE_SOFT = "#e6eee8"
SKY = "#e7eef5"
SKY_INK = "#3d5a73"
WARM = "#fbeee4"
WARM_INK = "#8a4b22"
GREY = "#d9d4c9"
HAND = "#d8b59a"


def svg(body: str, w=320, h=220) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">'
            f'<rect width="{w}" height="{h}" rx="16" fill="{SOFT}"/>{body}</svg>\n')


def text(x, y, s, size=14, fill=INK, weight=400, anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="system-ui,Segoe UI,Arial,sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')


def finger(x, y, angle=0, scale=0.7):
    """A simple pointing finger whose tip is at (x, y). angle turns the hand around the tip."""
    return (f'<g transform="translate({x},{y}) rotate({angle}) scale({scale})">'
            f'<rect x="-9" y="0" width="18" height="46" rx="9" fill="{HAND}" stroke="{LINE}" stroke-width="1.5"/>'
            f'<rect x="-22" y="34" width="44" height="40" rx="14" fill="{HAND}" stroke="{LINE}" stroke-width="1.5"/>'
            f'</g>')


def mitt(x, y, flip=False):
    s = -1 if flip else 1
    return (f'<g transform="translate({x},{y}) scale({s},1)">'
            f'<path d="M-18 40 L-18 0 Q-18 -22 0 -22 Q18 -22 18 0 L18 40 Z" fill="{WARM}" stroke="{WARM_INK}" stroke-width="2"/>'
            f'<path d="M18 4 Q32 2 30 18 L18 22" fill="{WARM}" stroke="{WARM_INK}" stroke-width="2"/>'
            f'<rect x="-20" y="38" width="40" height="10" rx="3" fill="{WARM_INK}"/></g>')


def microwave(open_door=False):
    door = (f'<rect x="40" y="50" width="160" height="120" rx="8" fill="{SKY}" stroke="{LINE}" stroke-width="2"/>'
            if not open_door else
            f'<rect x="40" y="50" width="160" height="120" rx="8" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M40 50 L10 62 L10 182 L40 170 Z" fill="{SKY}" stroke="{LINE}" stroke-width="2"/>')
    return (f'<rect x="30" y="40" width="260" height="140" rx="12" fill="#fff" stroke="{LINE}" stroke-width="2"/>{door}'
            f'<rect x="212" y="52" width="66" height="22" rx="4" fill="{INK}"/>' + text(245, 68, "2:30", 14, "#9fe3b0", 600))


def keypad(highlight="Cook Time"):
    labels = ["Cook Time", "Timer", "Cancel", "Start"]
    out = []
    for i, lab in enumerate(labels):
        y = 84 + i * 22
        on = lab == highlight
        out.append(f'<rect x="214" y="{y}" width="62" height="18" rx="4" fill="{SAGE if on else SOFT}" stroke="{LINE}" stroke-width="1"/>')
        out.append(text(245, y + 13, lab, 9.5, "#fff" if on else INK, 600 if on else 400))
    return "".join(out)


def dish(x, y, w=90, steam=False):
    s = (f'<ellipse cx="{x}" cy="{y}" rx="{w/2}" ry="{w/7}" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
         f'<ellipse cx="{x}" cy="{y-3}" rx="{w/2-10}" ry="{w/9}" fill="{WARM}"/>')
    if steam:
        for dx in (-14, 0, 14):
            s += (f'<path d="M{x+dx} {y-14} q-6 -10 0 -20 q6 -10 0 -20" fill="none" stroke="{GREY}" '
                  f'stroke-width="3" stroke-linecap="round"/>')
    return s


def package(circle=True):
    s = (f'<rect x="70" y="30" width="180" height="160" rx="10" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="70" y="30" width="180" height="34" rx="10" fill="{SAGE_SOFT}"/>' + text(160, 53, "Frozen meal", 15, INK, 600)
         + text(160, 92, "Microwave:", 14, INK, 600) + text(160, 116, "Cook 2 min 30 sec", 14)
         + text(160, 140, "Stir halfway", 13, LINE) + text(160, 162, "Let stand 1 min", 13, LINE))
    if circle:
        s += f'<ellipse cx="160" cy="111" rx="78" ry="16" fill="none" stroke="{WARM_INK}" stroke-width="3"/>'
    return s


def screen(lines, button=None, circle_line=None, w=320, h=220):
    s = f'<rect x="80" y="14" width="160" height="192" rx="18" fill="{INK}"/><rect x="88" y="30" width="144" height="160" rx="6" fill="#fff"/>'
    for i, (label, value) in enumerate(lines):
        y = 54 + i * 22
        s += text(96, y, label, 12, INK, 400, "start") + text(224, y, value, 12, INK, 600, "end")
        if circle_line == i:
            s += f'<rect x="92" y="{y-15}" width="136" height="21" rx="6" fill="none" stroke="{WARM_INK}" stroke-width="2.5"/>'
    if button:
        s += f'<rect x="98" y="150" width="124" height="28" rx="8" fill="{SAGE}"/>' + text(160, 169, button, 13, "#fff", 600)
    return s


def reader(top_text, bottom=None):
    s = (f'<rect x="100" y="20" width="120" height="180" rx="16" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="112" y="34" width="96" height="60" rx="6" fill="{SKY}"/>')
    for i, line in enumerate(top_text):
        s += text(160, 56 + i * 20, line, 13 if i else 12, SKY_INK, 600 if i else 400)
    for r in range(3):
        for c in range(3):
            s += f'<rect x="{118 + c*30}" y="{108 + r*22}" width="24" height="16" rx="3" fill="{SOFT}" stroke="{GREY}"/>'
    if bottom:
        s += bottom
    return s


def card_flat(x, y):
    return (f'<rect x="{x}" y="{y}" width="96" height="60" rx="8" fill="{SAGE}" stroke="{LINE}" stroke-width="1.5" opacity="0.95"/>'
            f'<rect x="{x+12}" y="{y+18}" width="18" height="14" rx="2" fill="#e8d9a8"/>'
            + text(x + 48, y + 50, "BANK CARD", 9, "#fff", 600))


def price_tag(x, y, name, price, unit, circle_unit=False):
    s = (f'<rect x="{x}" y="{y}" width="120" height="78" rx="6" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
         + text(x + 60, y + 22, name, 12, LINE) + text(x + 60, y + 50, price, 22, INK, 700)
         + text(x + 60, y + 68, unit, 10.5, LINE))
    if circle_unit:
        s += f'<rect x="{x+10}" y="{y+57}" width="100" height="16" rx="5" fill="none" stroke="{WARM_INK}" stroke-width="2.5"/>'
    return s


PICTURES = {
    # ----- heat a meal
    "heat_meal/s1.svg": svg(package()),
    "heat_meal/s2.svg": svg(
        f'<rect x="60" y="80" width="200" height="90" rx="10" fill="{WARM}" stroke="{LINE}" stroke-width="2"/>'
        f'<path d="M60 80 L260 80 L260 120 L190 80 Z" fill="{SKY}" opacity="0.8"/>'
        f'<path d="M190 80 L260 80 L240 52 Z" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
        + text(160, 200, "Peel back the film", 14, LINE) + finger(238, 58, 217)),
    "heat_meal/s3.svg": svg(microwave(open_door=True) + dish(120, 140, 80)),
    "heat_meal/s4.svg": svg(microwave() + keypad("Cook Time") + finger(272, 93, -37)),
    "heat_meal/s5.svg": svg(dish(150, 150, 140) + f'<line x1="170" y1="70" x2="150" y2="145" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
                            + mitt(185, 78) + text(160, 205, "Stir with a spoon", 14, LINE)),
    "heat_meal/s6.svg": svg(dish(160, 120, 130) + mitt(82, 108) + mitt(238, 108, flip=True) + text(160, 195, "Hold the sides with mitts", 14, LINE)),
    "heat_meal/s7.svg": svg(dish(160, 150, 160, steam=True) + text(160, 205, "Steam in the middle = hot", 14, LINE)),
    # ----- buying
    "buy/price_tag.svg": svg(f'<rect x="50" y="40" width="220" height="70" rx="8" fill="{SAGE_SOFT}"/>'
                             + f'<rect x="80" y="20" width="60" height="70" rx="6" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
                             + f'<rect x="170" y="30" width="50" height="60" rx="6" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
                             + f'<rect x="40" y="110" width="240" height="8" fill="{LINE}"/>'
                             + price_tag(100, 124, "Rice, 32 oz", "$3.49", "10.9¢ per oz")),
    "buy/compare.svg": svg(price_tag(30, 70, "Rice, 32 oz", "$3.49", "10.9¢ per oz", True)
                           + price_tag(170, 70, "Rice, 16 oz", "$2.29", "14.3¢ per oz", True)
                           + text(160, 190, "Compare the price per oz", 14, LINE)),
    "buy/reader_total.svg": svg(reader(["Total", "$12.48"]) + text(160, 214, "", 1)),
    "buy/card_tap.svg": svg(reader(["Tap, insert", "or swipe"]) + card_flat(112, 48)),
    "buy/phone_tap.svg": svg(reader(["Tap, insert", "or swipe"])
                             + f'<rect x="124" y="30" width="72" height="120" rx="12" fill="{INK}" opacity="0.95"/>'
                             + f'<rect x="130" y="40" width="60" height="96" rx="6" fill="{SKY}"/>' + text(160, 92, "Hold", 12, SKY_INK, 600)
                             + text(160, 108, "near reader", 10, SKY_INK)),
    "buy/add_to_cart.svg": svg(screen([("Rice, 32 oz", ""), ("Price", "$3.49")], "Add to cart") + finger(206, 166, -37)),
    "buy/online_total.svg": svg(screen([("Item", "$3.49"), ("Delivery fee", "$2.99"), ("Service fee", "$1.50"),
                                        ("Tax", "$0.28"), ("Total", "$8.26")], None, 4)),
    "buy/place_order.svg": svg(screen([("Address", "Apt 4B"), ("Payment", "Saved card"), ("Total", "$8.26")], "Place Order")),
    # ----- skill cards with no matching step picture
    "skills/type_address.svg": svg(screen([("Street", "120 Oak St"), ("Apt / Unit", "4B"), ("City", "Phoenix"),
                                           ("ZIP", "85004")], None, 1)),
}


def main():
    for rel, content in PICTURES.items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Wrote {len(PICTURES)} pictures to {OUT}")


if __name__ == "__main__":
    main()
