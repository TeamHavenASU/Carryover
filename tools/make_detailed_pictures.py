"""Detailed step pictures for Carryover. Plain shapes and gradients only, no brands, no people
(hands only), no real card numbers. Writes SVGs into the folder given as the first argument."""
import os
import sys

OUT = sys.argv[1]
FONT = 'font-family="Arial,Helvetica,sans-serif"'

DEFS = """
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f5f6"/><stop offset="1" stop-color="#d6dade"/></linearGradient>
<linearGradient id="cavity" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ece6d8"/><stop offset="1" stop-color="#cfc6b3"/></linearGradient>
<linearGradient id="door" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cfd3d7"/><stop offset="1" stop-color="#eef0f2"/></linearGradient>
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6b896"/><stop offset="1" stop-color="#c98f6b"/></linearGradient>
<linearGradient id="mitt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7a9cc6"/><stop offset="1" stop-color="#4f73a1"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#eef2f5"/></linearGradient>
<linearGradient id="dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4148"/><stop offset="1" stop-color="#22282d"/></linearGradient>
<linearGradient id="box" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3f7fa6"/><stop offset="1" stop-color="#2d5f80"/></linearGradient>
<radialGradient id="food" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#e9a45a"/><stop offset="1" stop-color="#b8692c"/></radialGradient>
<pattern id="mesh" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1" fill="#3b3f44"/></pattern>
"""


def svg(name, label, body, counter=True):
    floor = '<rect x="0" y="182" width="320" height="38" fill="#c9b79c"/><rect x="0" y="182" width="320" height="4" fill="#b29f83"/>' if counter else ""
    text = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 220" role="img" aria-label="{label}">'
            f'<defs>{DEFS}</defs><rect width="320" height="220" rx="16" fill="#efe9df"/>{floor}{body}</svg>')
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def steam(x, y, n=3, gap=12, h=30):
    return "".join(
        f'<path d="M{x+i*gap} {y} q-6 -{h/3} 0 -{h*2/3} q6 -{h/3} 0 -{h}" fill="none" stroke="#9aa5ad" stroke-width="3" stroke-linecap="round" opacity="0.7"/>'
        for i in range(n))


def dish(cx, cy, w=40):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{w}" ry="{w*0.22}" fill="#fff" stroke="#9aa3a8" stroke-width="1.5"/>'
            f'<path d="M{cx-w+2} {cy} Q{cx-w+4} {cy-16} {cx} {cy-18} Q{cx+w-4} {cy-16} {cx+w-2} {cy} Z" fill="#fff" stroke="#9aa3a8" stroke-width="1.5"/>'
            f'<ellipse cx="{cx}" cy="{cy-14}" rx="{w*0.8}" ry="{w*0.15}" fill="url(#food)"/>'
            f'<circle cx="{cx-12}" cy="{cy-15}" r="2.5" fill="#6f9e4a"/><circle cx="{cx+8}" cy="{cy-13}" r="2.5" fill="#6f9e4a"/>'
            f'<circle cx="{cx-2}" cy="{cy-17}" r="2" fill="#d9c25a"/>')


def microwave_open(inside=""):
    keys = "".join(f'<rect x="{248+12*c}" y="{78+11*r}" width="10" height="8" rx="1.5"/>' for r in range(3) for c in range(3))
    return (
        '<rect x="62" y="38" width="236" height="146" rx="10" fill="url(#metal)" stroke="#8d939a" stroke-width="2"/>'
        '<rect x="72" y="48" width="160" height="126" rx="6" fill="url(#cavity)" stroke="#a59c8a" stroke-width="1.5"/>'
        '<rect x="72" y="48" width="160" height="10" fill="#fff8e6" opacity="0.7"/>'
        '<ellipse cx="152" cy="158" rx="62" ry="10" fill="#dfe7ea" stroke="#9fb0b6" stroke-width="1.5" opacity="0.9"/>'
        + inside +
        '<rect x="242" y="50" width="46" height="124" rx="4" fill="#e3e6e9" stroke="#a7adb3"/>'
        '<rect x="247" y="56" width="36" height="16" rx="2" fill="#20262b"/>'
        f'<text x="265" y="68" text-anchor="middle" {FONT} font-size="11" fill="#7fe3c0">0:00</text>'
        f'<g fill="#f8f9fa" stroke="#9aa1a7" stroke-width="0.8">{keys}<rect x="260" y="111" width="10" height="8" rx="1.5"/></g>'
        '<rect x="248" y="124" width="34" height="11" rx="2" fill="#f8f9fa" stroke="#9aa1a7" stroke-width="0.8"/>'
        '<rect x="248" y="139" width="34" height="11" rx="2" fill="#6fae7c" stroke="#4e8a5b" stroke-width="0.8"/>'
        '<rect x="248" y="155" width="34" height="13" rx="2" fill="#b9bfc5" stroke="#8d939a" stroke-width="0.8"/>'
        '<path d="M62 40 L20 58 L20 196 L62 182 Z" fill="url(#door)" stroke="#8d939a" stroke-width="2"/>'
        '<path d="M56 56 L28 68 L28 176 L56 166 Z" fill="#2c3136" opacity="0.85"/>'
        '<path d="M56 56 L28 68 L28 176 L56 166 Z" fill="url(#mesh)" opacity="0.55"/>'
        '<rect x="22" y="100" width="4" height="40" rx="2" fill="#7b8289"/>')


def mitt(x, y, flip=False):
    t = f'translate({x} {y})' + (' scale(-1 1)' if flip else '')
    return (f'<g transform="{t}"><path d="M0 0 C-4 -18 10 -30 22 -26 L30 -40 C34 -48 44 -44 42 -36 L36 -18 C44 -10 44 8 34 16 L8 22 C2 16 2 8 0 0 Z" '
            'fill="url(#mitt)" stroke="#3d5d86" stroke-width="1.5"/>'
            '<path d="M6 20 L36 14 L38 24 L8 30 Z" fill="#e9eef5" stroke="#3d5d86" stroke-width="1.2"/>'
            '<path d="M8 4 C14 8 22 8 28 4" fill="none" stroke="#c9d6e6" stroke-width="1.5" opacity="0.7"/></g>')


def phone(x, y, w, h, content):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#dark)" stroke="#1a1f23" stroke-width="2"/>'
            f'<rect x="{x+6}" y="{y+14}" width="{w-12}" height="{h-28}" rx="6" fill="url(#screen)"/>'
            f'<rect x="{x+w/2-12}" y="{y+5}" width="24" height="4" rx="2" fill="#555c63"/>' + content)


def finger(tip_x, tip_y, from_right=True):
    # A finger coming from the lower right (or lower left) with the tip at (tip_x, tip_y).
    s = 1 if from_right else -1
    pts = (f'M{tip_x} {tip_y} C{tip_x-2*s} {tip_y+8} {tip_x+4*s} {tip_y+14} {tip_x+12*s} {tip_y+14} '
           f'C{tip_x+22*s} {tip_y+14} {tip_x+34*s} {tip_y+24} {tip_x+60*s} {tip_y+60} L{tip_x+80*s} {tip_y+90} '
           f'L{tip_x+40*s} {tip_y+110} L{tip_x+14*s} {tip_y+64} C{tip_x+2*s} {tip_y+44} {tip_x-8*s} {tip_y+20} {tip_x} {tip_y} Z')
    return (f'<path d="{pts}" fill="url(#skin)" stroke="#a8724f" stroke-width="1.5"/>'
            f'<path d="M{tip_x+1*s} {tip_y+3} C{tip_x} {tip_y+8} {tip_x+4*s} {tip_y+10} {tip_x+10*s} {tip_y+9}" fill="none" stroke="#f3d6c2" stroke-width="3" stroke-linecap="round"/>')


def circle_mark(cx, cy, rx, ry):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#c0392b" stroke-width="3"/>'


def reader(x, y, screen_lines):
    lines = "".join(
        f'<text x="{x+50}" y="{y+30+i*16}" text-anchor="middle" {FONT} font-size="{13 if i else 11}" '
        f'font-weight="{700 if i else 400}" fill="#1f2a30">{t}</text>' for i, t in enumerate(screen_lines))
    keys = "".join(f'<rect x="{x+16+c*24}" y="{y+82+r*16}" width="20" height="12" rx="3" fill="#4a525a"/>' for r in range(3) for c in range(3))
    return (f'<rect x="{x}" y="{y}" width="100" height="140" rx="14" fill="url(#dark)" stroke="#1a1f23" stroke-width="2"/>'
            f'<rect x="{x+10}" y="{y+12}" width="80" height="58" rx="5" fill="#dfeee8"/>' + lines + keys)


def card(x, y, angle=0):
    return (f'<g transform="rotate({angle} {x+45} {y+28})"><rect x="{x}" y="{y}" width="90" height="56" rx="7" fill="#5b7fa3" stroke="#3e5d7d" stroke-width="1.5"/>'
            f'<rect x="{x+10}" y="{y+16}" width="16" height="12" rx="2" fill="#e5c66b" stroke="#b8993f"/>'
            f'<path d="M{x+70} {y+16} q6 6 0 12 M{x+75} {y+12} q9 10 0 20 M{x+80} {y+8} q12 14 0 28" fill="none" stroke="#e9eef5" stroke-width="2" stroke-linecap="round"/>'
            f'<rect x="{x+10}" y="{y+38}" width="40" height="5" rx="2" fill="#c3d2e2" opacity="0.7"/></g>')


def waves(x, y):
    return "".join(f'<path d="M{x+i*9} {y-6-i*3} q8 {6+i*3} 0 {12+i*6}" fill="none" stroke="#6fae7c" stroke-width="3" stroke-linecap="round"/>' for i in range(3))


# ---- Heat a meal ----
svg("heat_meal/s1.svg", "A meal package with the cooking time circled",
    '<path d="M70 30 L230 30 L250 44 L250 180 L90 180 L70 166 Z" fill="#244a63"/>'
    '<rect x="70" y="30" width="160" height="150" rx="4" fill="url(#box)" stroke="#1e3d52" stroke-width="2"/>'
    f'<text x="150" y="52" text-anchor="middle" {FONT} font-size="15" font-weight="700" fill="#fff">Frozen meal</text>'
    '<rect x="84" y="62" width="132" height="108" rx="6" fill="#fdfaf3"/>'
    f'<text x="150" y="82" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#22303c">Microwave</text>'
    f'<text x="150" y="104" text-anchor="middle" {FONT} font-size="13" fill="#22303c">Cook 2 min 30 sec</text>'
    + circle_mark(150, 100, 62, 12) +
    f'<text x="150" y="128" text-anchor="middle" {FONT} font-size="12" fill="#4a5a68">Stir halfway</text>'
    f'<text x="150" y="148" text-anchor="middle" {FONT} font-size="12" fill="#4a5a68">Let stand 1 min</text>')

svg("heat_meal/s2.svg", "Peeling back the film on a meal tray",
    '<path d="M60 150 L260 150 L245 180 L75 180 Z" fill="#2b2f33" stroke="#1a1d20" stroke-width="2"/>'
    '<ellipse cx="160" cy="150" rx="100" ry="22" fill="#3a4045" stroke="#1a1d20" stroke-width="2"/>'
    '<ellipse cx="125" cy="150" rx="45" ry="13" fill="url(#food)"/><ellipse cx="205" cy="150" rx="32" ry="11" fill="#e8d9a0"/>'
    '<circle cx="112" cy="148" r="3" fill="#6f9e4a"/><circle cx="135" cy="152" r="3" fill="#6f9e4a"/>'
    '<path d="M70 146 C110 132 200 130 250 146 C240 120 220 96 200 86 C180 100 120 130 70 146 Z" fill="#e6f0f5" opacity="0.85" stroke="#9fb7c4" stroke-width="1.5"/>'
    + finger(198, 84, from_right=True))

svg("heat_meal/s3.svg", "A dish in the middle of an open microwave", microwave_open(dish(152, 150)))

keys4 = "".join(
    f'<rect x="{86+52*c}" y="{108+28*r}" width="44" height="22" rx="4" fill="#fff" stroke="#9aa1a7"/>'
    f'<text x="{108+52*c}" y="{123+28*r}" text-anchor="middle" {FONT} font-size="12" fill="#2b3036">{1+c+3*r}</text>'
    for r in range(2) for c in range(3))
svg("heat_meal/s4.svg", "A finger pressing the Cook Time button",
    '<rect x="70" y="14" width="180" height="196" rx="10" fill="url(#metal)" stroke="#8d939a" stroke-width="2"/>'
    '<rect x="86" y="26" width="148" height="38" rx="4" fill="#1e2429"/>'
    f'<text x="160" y="54" text-anchor="middle" {FONT} font-size="24" font-weight="700" fill="#7fe3c0">2:30</text>'
    f'<rect x="86" y="74" width="70" height="26" rx="5" fill="#fff" stroke="#9aa1a7"/><text x="121" y="91" text-anchor="middle" {FONT} font-size="12" fill="#2b3036">Power</text>'
    f'<rect x="164" y="74" width="70" height="26" rx="5" fill="#fff4cc" stroke="#c9a227" stroke-width="2"/><text x="199" y="91" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#2b3036">Cook Time</text>'
    + keys4 +
    f'<rect x="86" y="164" width="70" height="30" rx="5" fill="#e9ecef" stroke="#9aa1a7"/><text x="121" y="183" text-anchor="middle" {FONT} font-size="12" fill="#2b3036">Stop</text>'
    f'<rect x="164" y="164" width="70" height="30" rx="5" fill="#6fae7c" stroke="#4e8a5b"/><text x="199" y="183" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#fff">Start</text>'
    # finger from the right, tip on the right end of Cook Time so its words stay readable
    '<g transform="translate(8 0)">'
    '<path d="M228 92 C222 92 219 86 222 81 C225 76 233 75 242 76 L320 70 L320 98 L246 98 C238 99 232 96 228 92 Z" fill="url(#skin)" stroke="#a8724f" stroke-width="1.5"/>'
    '<path d="M224 85 C225 80 230 79 235 80" fill="none" stroke="#f3d6c2" stroke-width="3" stroke-linecap="round"/>' '</g>', counter=False)

svg("heat_meal/s5.svg", "Stirring the food with oven mitts on",
    microwave_open(dish(152, 150) +
                   '<path d="M168 134 L214 70" stroke="#b9bfc5" stroke-width="5" stroke-linecap="round"/>'
                   '<ellipse cx="166" cy="137" rx="7" ry="4" fill="#b9bfc5"/>' + mitt(200, 76)))

svg("heat_meal/s6.svg", "Taking the dish out with oven mitts",
    microwave_open() + dish(150, 196, 46).replace('cy="196"', 'cy="196"') + mitt(96, 186) + mitt(204, 186, flip=True)
    + steam(138, 170))

svg("heat_meal/s7.svg", "Steam coming from the middle of the food",
    '<ellipse cx="160" cy="168" rx="110" ry="24" fill="#fff" stroke="#9aa3a8" stroke-width="2"/>'
    '<ellipse cx="160" cy="164" rx="84" ry="16" fill="url(#food)"/>'
    '<circle cx="128" cy="162" r="4" fill="#6f9e4a"/><circle cx="182" cy="166" r="4" fill="#6f9e4a"/><circle cx="160" cy="158" r="3" fill="#d9c25a"/>'
    + steam(146, 150, 3, 14, 60) +
    '<path d="M250 120 L222 158" stroke="#9aa1a7" stroke-width="4" stroke-linecap="round"/>'
    '<path d="M246 112 l8 12 M250 110 l8 12 M254 108 l8 12" stroke="#9aa1a7" stroke-width="2" stroke-linecap="round"/>')

# ---- Buying ----
svg("buy/price_tag.svg", "A price tag on a shelf under an item",
    '<rect x="20" y="40" width="280" height="10" fill="#b6bcc2"/>'
    '<rect x="122" y="60" width="76" height="76" rx="8" fill="#f1e2c2" stroke="#b49a6a" stroke-width="2"/>'
    f'<text x="160" y="102" text-anchor="middle" {FONT} font-size="14" font-weight="700" fill="#6b4f22">Rice</text>'
    '<rect x="20" y="136" width="280" height="14" fill="#9aa1a7"/>'
    '<rect x="116" y="150" width="88" height="44" rx="4" fill="#fffbe6" stroke="#c9a227" stroke-width="2"/>'
    f'<text x="160" y="166" text-anchor="middle" {FONT} font-size="10" fill="#4a5a68">Rice, 2 lb</text>'
    f'<text x="160" y="186" text-anchor="middle" {FONT} font-size="18" font-weight="700" fill="#22303c">$3.49</text>', counter=False)

def tag(x, size, price, unit, mark):
    return (f'<rect x="{x}" y="70" width="120" height="84" rx="6" fill="#fffbe6" stroke="#c9a227" stroke-width="2"/>'
            f'<text x="{x+60}" y="92" text-anchor="middle" {FONT} font-size="11" fill="#4a5a68">{size}</text>'
            f'<text x="{x+60}" y="118" text-anchor="middle" {FONT} font-size="20" font-weight="700" fill="#22303c">{price}</text>'
            f'<text x="{x+60}" y="142" text-anchor="middle" {FONT} font-size="11" fill="#22303c">{unit}</text>'
            + (circle_mark(x + 60, 138, 50, 11) if mark else ""))
svg("buy/compare.svg", "Two price tags side by side with the unit price circled",
    '<rect x="10" y="150" width="300" height="12" fill="#9aa1a7"/>'
    + tag(26, "Rice, 16 oz", "$2.99", "18.7¢ per oz", True) + tag(174, "Rice, 32 oz", "$4.49", "14.0¢ per oz", True), counter=False)

svg("buy/reader_total.svg", "A card reader screen showing the total",
    reader(110, 34, ["Total", "$12.48"]), counter=True)

svg("buy/card_tap.svg", "A card held flat on a card reader",
    reader(110, 66, ["Tap or insert", "$12.48"]) + card(115, 4, -4) + waves(212, 24))

svg("buy/phone_tap.svg", "The top of a phone held near a card reader",
    reader(70, 50, ["Tap to pay", "$12.48"]) +
    '<g transform="rotate(-12 220 70)"><rect x="180" y="20" width="80" height="150" rx="14" fill="url(#dark)" stroke="#1a1f23" stroke-width="2"/>'
    '<rect x="186" y="34" width="68" height="122" rx="6" fill="url(#screen)"/>'
    '<circle cx="220" cy="90" r="16" fill="#dff1e4" stroke="#6fae7c" stroke-width="2"/>'
    '<path d="M213 90 l5 5 l9 -10" fill="none" stroke="#4e8a5b" stroke-width="3" stroke-linecap="round"/></g>'
    + waves(176, 78))

svg("buy/add_to_cart.svg", "A finger tapping an Add to cart button",
    phone(110, 10, 110, 200,
          '<rect x="128" y="34" width="74" height="60" rx="6" fill="#f1e2c2" stroke="#b49a6a"/>'
          f'<text x="165" y="68" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#6b4f22">Rice</text>'
          f'<text x="165" y="112" text-anchor="middle" {FONT} font-size="11" fill="#22303c">Rice, 2 lb</text>'
          f'<text x="165" y="130" text-anchor="middle" {FONT} font-size="15" font-weight="700" fill="#22303c">$3.49</text>'
          '<rect x="124" y="146" width="82" height="26" rx="13" fill="#e5a23a" stroke="#b97d22"/>'
          f'<text x="165" y="163" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#22303c">Add to cart</text>')
    + finger(176, 162), counter=False)

svg("buy/online_total.svg", "A checkout screen with the total circled",
    phone(105, 10, 110, 200,
          f'<text x="160" y="44" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#22303c">Checkout</text>'
          f'<text x="118" y="70" {FONT} font-size="10" fill="#4a5a68">Items</text><text x="202" y="70" text-anchor="end" {FONT} font-size="10" fill="#4a5a68">$21.47</text>'
          f'<text x="118" y="88" {FONT} font-size="10" fill="#4a5a68">Shipping</text><text x="202" y="88" text-anchor="end" {FONT} font-size="10" fill="#4a5a68">$3.50</text>'
          '<line x1="118" y1="98" x2="202" y2="98" stroke="#b8c2cc"/>'
          f'<text x="118" y="118" {FONT} font-size="12" font-weight="700" fill="#22303c">Total</text><text x="202" y="118" text-anchor="end" {FONT} font-size="12" font-weight="700" fill="#22303c">$24.97</text>'
          + circle_mark(160, 114, 48, 12)), counter=False)

svg("buy/place_order.svg", "A Place Order button on a checkout screen",
    phone(105, 10, 110, 200,
          f'<text x="160" y="44" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#22303c">Checkout</text>'
          f'<text x="118" y="80" {FONT} font-size="12" font-weight="700" fill="#22303c">Total</text><text x="202" y="80" text-anchor="end" {FONT} font-size="12" font-weight="700" fill="#22303c">$24.97</text>'
          '<rect x="118" y="140" width="84" height="30" rx="15" fill="#e5a23a" stroke="#b97d22"/>'
          f'<text x="160" y="159" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#22303c">Place Order</text>'), counter=False)

kb = "".join(f'<rect x="{116+c*10}" y="{150+r*12}" width="8" height="9" rx="1.5" fill="#fff" stroke="#c3ccd4" stroke-width="0.6"/>' for r in range(3) for c in range(9))
svg("skills/type_address.svg", "Type an address",
    phone(105, 10, 110, 200,
          f'<text x="160" y="42" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#22303c">Address</text>'
          '<rect x="116" y="52" width="88" height="18" rx="3" fill="#fff" stroke="#2f5d7c" stroke-width="1.5"/>'
          f'<text x="120" y="65" {FONT} font-size="9" fill="#22303c">12 Main St|</text>'
          '<rect x="116" y="76" width="88" height="18" rx="3" fill="#fff" stroke="#b8c2cc"/>'
          f'<text x="120" y="89" {FONT} font-size="9" fill="#9aa5ad">City</text>'
          '<rect x="116" y="100" width="40" height="18" rx="3" fill="#fff" stroke="#b8c2cc"/>'
          f'<text x="120" y="113" {FONT} font-size="9" fill="#9aa5ad">State</text>'
          '<rect x="162" y="100" width="42" height="18" rx="3" fill="#fff" stroke="#b8c2cc"/>'
          f'<text x="166" y="113" {FONT} font-size="9" fill="#9aa5ad">ZIP</text>'
          '<rect x="112" y="144" width="96" height="42" rx="4" fill="#e9edf0"/>' + kb), counter=False)


# ---- Buying: steps that had no picture ----
svg("buy/enough_money.svg", "A wallet with a card and some money, next to an item",
    '<rect x="40" y="96" width="140" height="86" rx="12" fill="#6b4f3a" stroke="#4d3828" stroke-width="2"/>'
    '<rect x="52" y="82" width="90" height="40" rx="5" fill="#9fc49a" stroke="#6f9a6a"/>'
    '<circle cx="66" cy="102" r="8" fill="none" stroke="#6f9a6a" stroke-width="2"/>'
    + card(96, 70, 8) +
    '<path d="M40 120 L180 120" stroke="#4d3828" stroke-width="2"/>'
    '<rect x="212" y="96" width="70" height="86" rx="8" fill="#f1e2c2" stroke="#b49a6a" stroke-width="2"/>'
    f'<text x="247" y="140" text-anchor="middle" {FONT} font-size="13" font-weight="700" fill="#6b4f22">Rice</text>'
    '<rect x="218" y="60" width="58" height="26" rx="4" fill="#fffbe6" stroke="#c9a227" stroke-width="2"/>'
    f'<text x="247" y="78" text-anchor="middle" {FONT} font-size="13" font-weight="700" fill="#22303c">$3.49</text>')

svg("buy/need_it.svg", "An item with a thought bubble: do I need this now?",
    '<rect x="120" y="110" width="80" height="72" rx="8" fill="#f1e2c2" stroke="#b49a6a" stroke-width="2"/>'
    f'<text x="160" y="152" text-anchor="middle" {FONT} font-size="14" font-weight="700" fill="#6b4f22">Rice</text>'
    '<ellipse cx="200" cy="56" rx="78" ry="34" fill="#fff" stroke="#9aa5ad" stroke-width="2"/>'
    '<circle cx="150" cy="98" r="7" fill="#fff" stroke="#9aa5ad" stroke-width="2"/><circle cx="138" cy="110" r="4" fill="#fff" stroke="#9aa5ad" stroke-width="2"/>'
    f'<text x="200" y="52" text-anchor="middle" {FONT} font-size="13" font-weight="700" fill="#22303c">Do I need this</text>'
    f'<text x="200" y="70" text-anchor="middle" {FONT} font-size="13" font-weight="700" fill="#22303c">right now?</text>')

svg("buy/decide.svg", "Two choices: put it in the basket, or back on the shelf",
    '<rect x="20" y="70" width="110" height="10" fill="#b6bcc2"/><rect x="20" y="150" width="110" height="10" fill="#9aa1a7"/>'
    '<rect x="50" y="96" width="50" height="54" rx="6" fill="#f1e2c2" stroke="#b49a6a" stroke-width="2"/>'
    f'<text x="75" y="128" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#6b4f22">Rice</text>'
    f'<text x="75" y="58" text-anchor="middle" {FONT} font-size="12" fill="#22303c">Leave it</text>'
    '<path d="M196 104 L276 104 L266 164 L206 164 Z" fill="#dfe7ea" stroke="#5d6b78" stroke-width="2"/>'
    '<path d="M206 104 Q236 70 266 104" fill="none" stroke="#5d6b78" stroke-width="4"/>'
    '<path d="M206 124 L266 124 M211 144 L261 144" stroke="#9fb0b6" stroke-width="2"/>'
    f'<text x="236" y="58" text-anchor="middle" {FONT} font-size="12" fill="#22303c">Buy it</text>'
    f'<text x="160" y="124" text-anchor="middle" {FONT} font-size="16" font-weight="700" fill="#4a5a68">or</text>')

svg("buy/register_line.svg", "A store checkout counter with a wait-here sign on the floor",
    '<rect x="150" y="96" width="150" height="86" rx="6" fill="#8d939a" stroke="#5d6b78" stroke-width="2"/>'
    '<rect x="150" y="90" width="150" height="12" rx="3" fill="#3a4148"/>'
    '<rect x="160" y="92" width="80" height="6" fill="#5a636b"/>'
    '<rect x="262" y="40" width="34" height="50" rx="6" fill="url(#dark)" stroke="#1a1f23" stroke-width="2"/>'
    '<rect x="267" y="46" width="24" height="16" rx="2" fill="#dfeee8"/>'
    '<rect x="268" y="68" width="22" height="16" rx="2" fill="#4a525a"/>' +
    '<ellipse cx="80" cy="196" rx="52" ry="12" fill="#e5a23a" stroke="#b97d22" stroke-width="2"/>'
    f'<text x="80" y="201" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="#22303c">Wait here</text>'
    '<path d="M80 150 L80 176 M70 166 L80 176 L90 166" stroke="#4a5a68" stroke-width="3" fill="none" stroke-linecap="round"/>')

svg("buy/receipt.svg", "A receipt going into a wallet",
    '<rect x="70" y="112" width="150" height="74" rx="12" fill="#6b4f3a" stroke="#4d3828" stroke-width="2"/>'
    '<path d="M70 134 L220 134" stroke="#4d3828" stroke-width="2"/>'
    '<path d="M120 40 L190 40 L190 120 L183 114 L176 120 L169 114 L162 120 L155 114 L148 120 L141 114 L134 120 L127 114 L120 120 Z" fill="#fff" stroke="#9aa5ad" stroke-width="2"/>'
    f'<text x="155" y="58" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#22303c">RECEIPT</text>'
    '<path d="M130 72 L180 72 M130 84 L172 84 M130 96 L178 96" stroke="#c3ccd4" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M240 70 L240 110 M230 100 L240 110 L250 100" stroke="#4a5a68" stroke-width="3" fill="none" stroke-linecap="round"/>')

svg("buy/delivery_pickup.svg", "A phone screen with two choices: Delivery or Pickup",
    phone(105, 10, 110, 200,
          f'<text x="160" y="44" text-anchor="middle" {FONT} font-size="10" font-weight="700" fill="#22303c">Delivery or pickup?</text>'
          '<rect x="118" y="62" width="84" height="44" rx="8" fill="#fff" stroke="#2f5d7c" stroke-width="2"/>'
          '<rect x="130" y="76" width="22" height="14" rx="2" fill="#7a9cc6"/><rect x="152" y="80" width="10" height="10" rx="1" fill="#7a9cc6"/>'
          '<circle cx="136" cy="92" r="3" fill="#2b3036"/><circle cx="156" cy="92" r="3" fill="#2b3036"/>'
          f'<text x="184" y="90" text-anchor="middle" {FONT} font-size="10" fill="#22303c">Delivery</text>'
          '<rect x="118" y="116" width="84" height="44" rx="8" fill="#fff" stroke="#b8c2cc" stroke-width="2"/>'
          '<path d="M130 150 L130 132 L140 124 L150 132 L150 150 Z" fill="#e5a23a"/>'
          f'<text x="182" y="142" text-anchor="middle" {FONT} font-size="10" fill="#22303c">Pickup</text>'), counter=False)

svg("buy/confirmation.svg", "An order confirmation screen with a check mark",
    phone(105, 10, 110, 200,
          '<circle cx="160" cy="66" r="20" fill="#dff1e4" stroke="#6fae7c" stroke-width="3"/>'
          '<path d="M150 66 l7 7 l13 -14" fill="none" stroke="#4e8a5b" stroke-width="4" stroke-linecap="round"/>'
          f'<text x="160" y="108" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#22303c">Order placed</text>'
          f'<text x="160" y="126" text-anchor="middle" {FONT} font-size="9" fill="#4a5a68">Order number</text>'
          '<rect x="128" y="132" width="64" height="12" rx="3" fill="#e9edf0"/>'
          '<rect x="122" y="154" width="76" height="24" rx="12" fill="#fff" stroke="#2f5d7c" stroke-width="2"/>'
          f'<text x="160" y="170" text-anchor="middle" {FONT} font-size="10" fill="#22303c">Save</text>'), counter=False)

print("done")
