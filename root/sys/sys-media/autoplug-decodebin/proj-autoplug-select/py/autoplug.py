#!/usr/bin/env python3
"""autoplug.py — керований автодобір: журнал кандидатів і вето на декодер.
   ./autoplug.py кіно.mkv --skip=vah264dec
   ./autoplug.py https://приклад.org/кіно.webm --no-hw
"""
import sys, threading
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstPbutils", "1.0")
from gi.repository import Gst, GstPbutils, GLib

# GstAutoplugSelectResult оголошено в gstplay-enum.h — усередині плагіна
# playback. Плагінних заголовків не встановлюють і в GIR їх немає, тож
# Gst.AutoplugSelectResult не існує: три значення переписуємо до себе.
TRY, EXPOSE, SKIP = 0, 1, 2

VIDEO_TAIL = ("queue", "videoconvert", "autovideosink")
AUDIO_TAIL = ("queue", "audioconvert", "audioresample", "autoaudiosink")


class Autoplug:
    def __init__(self, target, veto, no_hw):
        self.veto, self.no_hw = veto, no_hw
        self.lock = threading.Lock()          # журнал пишуть потоки даних
        self.journal = []
        self.n_try = self.n_skip = self.n_branches = 0
        self.missing = None
        self.exit_code = 0
        self.loop = GLib.MainLoop()

        self.pipeline = Gst.Pipeline.new("autoplug")
        if Gst.uri_is_valid(target):
            self.dec = Gst.ElementFactory.make("uridecodebin", "dec")
            self.dec.props.uri = target
            self.pipeline.add(self.dec)
        else:
            src = Gst.ElementFactory.make("filesrc", None)
            src.props.location = target
            self.dec = Gst.ElementFactory.make("decodebin", "dec")
            self.pipeline.add(src)
            self.pipeline.add(self.dec)
            if not src.link(self.dec):
                raise RuntimeError("filesrc → decodebin не з'єдналися")

        # G_CONNECT_AFTER (тобто connect_after) до autoplug-select чіпляти
        # не можна: такий обробник не викличуть ніколи.
        self.dec.connect("autoplug-select", self.on_select)
        self.dec.connect("pad-added", self.on_pad_added)
        self.dec.connect("no-more-pads", self.on_no_more_pads)
        self.dec.connect("unknown-type", self.on_unknown_type)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()                # повідомлення підуть у головний цикл
        bus.connect("message", self.on_message)

    def note(self, line, tried=0, skipped=0, branches=0):
        with self.lock:
            self.journal.append(line)
            self.n_try += tried
            self.n_skip += skipped
            self.n_branches += branches

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass
        self.pipeline.set_state(Gst.State.NULL)
        print("\n── журнал автодобору ────────────────────────")
        print("\n".join(self.journal))
        print("спроб дозволено: %d, пропущено: %d, гілок під'єднано: %d"
              % (self.n_try, self.n_skip, self.n_branches))
        return self.exit_code


def main(argv):
    Gst.init(None)
    veto = [a[len("--skip="):] for a in argv[1:] if a.startswith("--skip=")]
    no_hw = "--no-hw" in argv[1:]
    rest = [a for a in argv[1:] if not a.startswith("--")]
    if not rest:
        print("вжиток: %s <файл|URI> [--skip=ім'я]… [--no-hw]" % argv[0])
        return 1
    return Autoplug(rest[0], veto, no_hw).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
