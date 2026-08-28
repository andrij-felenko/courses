import sys
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib


class Player:
    def __init__(self, uri):
        self.loop = GLib.MainLoop()
        self.target = Gst.State.PLAYING   # чого ми хочемо; буферизація цього не змінює
        self.is_live = False              # живий конвеєр: паузою не керуємо взагалі
        self.buffering = False            # зараз усередині набору запасу
        self.exit_code = 0

        self.pipeline = Gst.Pipeline.new("player")
        dec = Gst.ElementFactory.make("uridecodebin", "dec")
        if dec is None:
            raise RuntimeError("немає елемента uridecodebin — не встановлено gst-plugins-base")
        dec.set_property("uri", uri)
        dec.set_property("use-buffering", True)
        self.pipeline.add(dec)
        dec.connect("pad-added", self.on_pad_added)

        self.bus = self.pipeline.get_bus()
        self.watch_id = self.bus.add_watch(GLib.PRIORITY_DEFAULT, self.on_message, None)
