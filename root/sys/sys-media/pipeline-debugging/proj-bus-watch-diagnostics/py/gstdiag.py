"""gstdiag.py — діагностична обв'язка для будь-якого конвеєра."""
import sys
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstPbutils", "1.0")
from gi.repository import Gst, GstPbutils, GLib


class Diag:
    def __init__(self, pipeline, tag, guard_sec=10):
        self.pipeline = pipeline
        self.bus = pipeline.get_bus()
        self.tag = tag
        self.guard_sec = guard_sec
        self.is_live = False          # джерело живе: прероллу не буде за визначенням
        self.qos_last = 0             # коли востаннє друкували QoS, монотонні мкс

        self.watch_id = self.bus.add_watch(GLib.PRIORITY_DEFAULT, self._on_message, None)
        if self.watch_id == 0:
            print("на шині вже висить чуже стеження — діагностика НЕ приєдналася",
                  file=sys.stderr)

        self.guard_id = (GLib.timeout_add_seconds(guard_sec, self._guard)
                         if guard_sec else 0)

    @staticmethod
    def _src_path(msg):
        """Повний шлях елемента в графі: /GstPipeline:pipeline0/GstQTDemux:qtdemux0."""
        return msg.src.get_path_string() if msg.src else "(без джерела)"

    def _dump(self, why):
        """Знімок графа з часовою міткою в імені."""
        Gst.debug_bin_to_dot_file_with_ts(self.pipeline, Gst.DebugGraphDetails.ALL,
                                          f"{self.tag}-{why}")
        print(f"  граф скинуто: $GST_DEBUG_DUMP_DOT_DIR/<час>-{self.tag}-{why}.dot",
              file=sys.stderr)

    def detach(self):
        if self.guard_id:
            GLib.source_remove(self.guard_id)
            self.guard_id = 0
        if self.watch_id:
            self.bus.remove_watch()
            self.watch_id = 0
