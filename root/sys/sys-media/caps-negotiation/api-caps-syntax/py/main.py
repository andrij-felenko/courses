import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)

# у Python немає new_simple (варіативні функції не інтроспектуються) —
# caps будують з рядка або через new_empty_simple + set_value
src = Gst.Caps.from_string(
    "video/x-raw, format={ NV12, YUY2 }, width=[ 320, 1920 ], "
    "height=[ 240, 1080 ], framerate=[ 1/1, 60/1 ]")
sink = Gst.Caps.from_string(
    "video/x-raw, format=NV12, width=[ 16, 4096 ], height=[ 16, 4096 ]")

both = src.intersect_full(sink, Gst.CapsIntersectMode.FIRST)
if both.is_empty():
    raise SystemExit("спільного формату немає — тут і виникає not-negotiated")

print("перетин:", both.to_string())

fixed = both.copy().fixate()        # copy(), бо fixate забирає посилання
assert fixed.is_fixed()

st = fixed.get_structure(0)
ok_w, w = st.get_int("width")       # геттери віддають пару (успіх, значення)
ok_h, h = st.get_int("height")
ok_f, num, den = st.get_fraction("framerate")
print("обрано: %s %dx%d @ %d/%d" % (st.get_string("format"), w, h, num, den))
