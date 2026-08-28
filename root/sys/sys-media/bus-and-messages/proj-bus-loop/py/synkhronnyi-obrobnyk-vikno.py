gi.require_version("GstVideo", "1.0")
from gi.repository import GstVideo

def on_sync_message(bus, msg, handle):
    if not GstVideo.is_video_overlay_prepare_window_handle_message(msg):
        return Gst.BusSyncReply.PASS      # решта — звичайним шляхом, у чергу

    msg.src.set_window_handle(handle)     # unref тут не потрібен: його робить зв'язувач
    return Gst.BusSyncReply.DROP

# поруч із add_watch(), до першого set_state
bus.set_sync_handler(on_sync_message, window_handle)
