#!/usr/bin/env python3
"""
Generates a standalone Windows .ico file (scrcpy_cpl.ico) with ZERO third-party dependencies.
Uses Option 1 (Official scrcpy Jade & Charcoal) combining the Phone Mirror Frame + 3 Control Panel Sliders.
"""

import struct

def generate_ico(filename: str = "scrcpy_cpl.ico", size: int = 64):
    s = size / 24.0

    # Initialize transparent RGBA buffer (size x size)
    pixels = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]

    def hex_to_rgba(h: str):
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

    def fill_rounded_rect(x0, y0, x1, y1, radius, color_hex):
        rgba = hex_to_rgba(color_hex)
        ix0, iy0 = int(round(x0 * s)), int(round(y0 * s))
        ix1, iy1 = int(round(x1 * s)), int(round(y1 * s))
        r = radius * s
        for y in range(max(0, iy0), min(size, iy1)):
            for x in range(max(0, ix0), min(size, ix1)):
                # Corner distance check
                dx = max(ix0 + r - x, 0, x - (ix1 - 1 - r))
                dy = max(iy0 + r - y, 0, y - (iy1 - 1 - r))
                if dx * dx + dy * dy <= r * r:
                    pixels[y][x] = rgba

    def fill_circle(cx, cy, radius, color_hex):
        rgba = hex_to_rgba(color_hex)
        icx, icy = cx * s, cy * s
        r = radius * s
        for y in range(size):
            for x in range(size):
                if (x - icx) ** 2 + (y - icy) ** 2 <= r * r:
                    pixels[y][x] = rgba

    # 1. Jade Rounded Square Base (#166534 border + #1f7a54 fill)
    fill_rounded_rect(0.5, 0.5, 23.5, 23.5, 4.5, "#166534")
    fill_rounded_rect(1.5, 1.5, 22.5, 22.5, 3.8, "#1f7a54")

    # 2. Style 2: Phone Mirror Frame (White border + #134e35 screen)
    fill_rounded_rect(3.0, 2.5, 15.0, 21.0, 2.2, "#ffffff")
    fill_rounded_rect(4.4, 3.9, 13.6, 19.6, 1.2, "#134e35")
    # Speaker notch
    fill_rounded_rect(7.2, 4.8, 10.8, 5.7, 0.4, "#ffffff")

    # 3. Style 1: Control Panel Sliders Badge overlapping right (#ffffff border + #18181b fill)
    fill_rounded_rect(9.0, 7.2, 21.5, 19.8, 2.4, "#ffffff")
    fill_rounded_rect(10.1, 8.3, 20.4, 18.7, 1.6, "#18181b")

    # 3 Slider tracks (#71717a)
    fill_rounded_rect(11.6, 10.3, 18.9, 11.3, 0.5, "#71717a")
    fill_rounded_rect(11.6, 13.0, 18.9, 14.0, 0.5, "#71717a")
    fill_rounded_rect(11.6, 15.7, 18.9, 16.7, 0.5, "#71717a")

    # 3 Slider Knobs (#4ade80, #ffffff, #4ade80)
    fill_circle(14.0, 10.8, 1.55, "#4ade80")
    fill_circle(17.1, 13.5, 1.55, "#ffffff")
    fill_circle(14.7, 16.2, 1.55, "#4ade80")

    # Pack as uncompressed 32-bit BGRA BMP inside ICO container
    bmp_header = struct.pack(
        "<IIIHHIIIIII",
        40,             # biSize
        size,           # biWidth
        size * 2,       # biHeight (XOR + AND mask)
        1,              # biPlanes
        32,             # biBitCount
        0,              # biCompression (BI_RGB)
        size * size * 4,
        0,
        0,
        0,
        0,
    )

    xor_bytes = bytearray()
    # BMP rows are stored bottom-up
    for y in range(size - 1, -1, -1):
        for x in range(size):
            r, g, b, a = pixels[y][x]
            xor_bytes.extend((b, g, r, a))

    and_row_bytes = ((size + 31) // 32) * 4
    and_bytes = bytes(and_row_bytes * size)

    img_data = bmp_header + xor_bytes + and_bytes
    ico_header = struct.pack("<HHH", 0, 1, 1)
    ico_dir_entry = struct.pack(
        "<BBBBHHII",
        size if size < 256 else 0,
        size if size < 256 else 0,
        0,
        0,
        1,
        32,
        len(img_data),
        6 + 16,
    )

    with open(filename, "wb") as f:
        f.write(ico_header + ico_dir_entry + img_data)


if __name__ == "__main__":
    generate_ico()
    print("Generated scrcpy_cpl.ico successfully.")
