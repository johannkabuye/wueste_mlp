#!/usr/bin/env python3
"""Create Molipe SVG logo"""

SVG_CONTENT = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 120 120" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
    <g transform="matrix(1,0,0,1,-153.477,-65.226)">
        <g transform="matrix(312.5,0,0,312.5,278.883,294.601)">
        </g>
        <text x="146.071px" y="294.601px" style="font-family:'Sunflower-Bold', 'Sunflower';font-weight:700;font-size:312.5px;fill:#ffffff;">*</text>
    </g>
</svg>'''

if __name__ == "__main__":
    with open("/tmp/molipe-logo.svg", "w") as f:
        f.write(SVG_CONTENT)
    print("✓ Created /tmp/molipe-logo.svg")
