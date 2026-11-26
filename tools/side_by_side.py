#!/usr/bin/env python3
"""Stack two contact sheets (reference on top, our cut below) for the parity review.

Usage: python3 tools/side_by_side.py REF_SHEET.jpg OUR_SHEET.jpg OUT.jpg
"""
import sys
from PIL import Image, ImageDraw

if len(sys.argv) != 4:
    sys.exit(__doc__)
a, b = (Image.open(p).convert("RGB") for p in sys.argv[1:3])
w = max(a.width, b.width)
out = Image.new("RGB", (w, a.height + b.height + 60), "black")
d = ImageDraw.Draw(out)
d.text((10, 8), "REFERENCE", fill="white")
out.paste(a, (0, 30))
d.text((10, a.height + 38), "OUR CUT", fill="white")
out.paste(b, (0, a.height + 60))
out.save(sys.argv[3], quality=88)
print(sys.argv[3])
