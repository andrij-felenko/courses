import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)

cands = Gst.ElementFactory.list_get_elements(
    Gst.ELEMENT_FACTORY_TYPE_DECODER | Gst.ELEMENT_FACTORY_TYPE_MEDIA_VIDEO,
    Gst.Rank.MARGINAL)

caps = Gst.Caps.from_string("video/x-h264")
fit = Gst.ElementFactory.list_filter(cands, caps, Gst.PadDirection.SINK, False)

for f in sorted(fit, key=lambda f: f.get_rank(), reverse=True):
    print("%-18s rank %u" % (f.get_name(), f.get_rank()))
