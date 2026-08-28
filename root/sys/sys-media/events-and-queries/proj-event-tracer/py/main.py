#!/usr/bin/env python3
import threading, time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)
T0 = time.monotonic()
ms = lambda: int((time.monotonic() - T0) * 1000)

_names, _lock = {}, threading.Lock()
def tag():
    with _lock:
        return _names.setdefault(threading.get_ident(), 'T%d' % (len(_names) + 1))

sent_at, count = {}, {}

def trace(pad, info, point):
    t = info.type
    if t & (Gst.PadProbeType.BUFFER | Gst.PadProbeType.BUFFER_LIST):
        count[point] = count.get(point, 0) + 1
        return Gst.PadProbeReturn.OK

    up = t & (Gst.PadProbeType.EVENT_UPSTREAM | Gst.PadProbeType.QUERY_UPSTREAM)
    extra = ''
    if t & (Gst.PadProbeType.EVENT_DOWNSTREAM | Gst.PadProbeType.EVENT_UPSTREAM
            | Gst.PadProbeType.EVENT_FLUSH):
        obj, kind = info.get_event(), 'подія '
        ser = obj.type.get_flags() & Gst.EventTypeFlags.SERIALIZED
        if obj.type in sent_at:
            extra = '   ← у дорозі %d мс' % (ms() - sent_at[obj.type])
    else:
        obj = info.get_query()
        kind = 'запит←' if t & Gst.PadProbeType.PULL else 'запит→'
        ser = obj.type.get_flags() & Gst.QueryTypeFlags.SERIALIZED
    print('%6d мс | %-10s | %-3s | %-6s %-5s %-4s | %-22s | буфер #%-4d%s'
          % (ms(), point, tag(), kind, 'вгору' if up else 'вниз',
             'сер.' if ser else 'поз.', obj.type.get_name(),
             count.get(point, 0), extra))
    return Gst.PadProbeReturn.OK

pipeline = Gst.parse_launch(
    'videotestsrc num-buffers=150 '
    '! video/x-raw,width=320,height=240,framerate=30/1 '
    '! queue name=q max-size-time=200000000 max-size-buffers=0 max-size-bytes=0 '
    '! fakesink sync=true')

MASK = (Gst.PadProbeType.BUFFER | Gst.PadProbeType.BUFFER_LIST
        | Gst.PadProbeType.EVENT_BOTH | Gst.PadProbeType.EVENT_FLUSH
        | Gst.PadProbeType.QUERY_BOTH)
q = pipeline.get_by_name('q')
for name in ('sink', 'src'):
    q.get_static_pad(name).add_probe(MASK, trace, 'queue.' + name)

def send_marks():
    print('\n--- %d мс: шлемо дві власні події поспіль ---' % ms())
    for etype in (Gst.EventType.CUSTOM_DOWNSTREAM, Gst.EventType.CUSTOM_DOWNSTREAM_OOB):
        sent_at[etype] = ms()
        pipeline.send_event(Gst.Event.new_custom(etype,
                                                 Gst.Structure.new_empty('tracer-mark')))
    return False

loop = GLib.MainLoop()
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect('message::eos', lambda *_: loop.quit())
pipeline.set_state(Gst.State.PLAYING)
GLib.timeout_add(1500, send_marks)
loop.run()
