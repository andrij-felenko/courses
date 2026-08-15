# -*- coding: utf-8 -*-
import sys, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgcheck

files = glob.glob(os.path.join(os.path.dirname(__file__), 'img', '*.svg'))
out_lines = []
for f in files:
    warns = list(svgcheck.check_svg(f))
    out_lines.append(f"{os.path.basename(f)}: {len(warns)} warnings")
    for w in warns:
        out_lines.append(f"  - {w}")

res_text = "\n".join(out_lines)
with open(os.path.join(os.path.dirname(__file__), 'svg_check_result.txt'), 'w', encoding='utf-8') as out:
    out.write(res_text)

print(res_text)
