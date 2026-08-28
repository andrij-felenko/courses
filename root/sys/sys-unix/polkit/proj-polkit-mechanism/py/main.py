#!/usr/bin/env python3
# backlightd — той самий механізм; полкіт має інтроспекцію GObject,
# тож із Python доступний той самий libpolkit-gobject, що і з C.
import gi
gi.require_version("Polkit", "1.0")
from gi.repository import Gio, GLib, Polkit

DEV    = "/sys/class/backlight/intel_backlight"
NAME   = "org.example.Backlight"
ACTION = "org.example.backlightd.set-brightness"

NODE = Gio.DBusNodeInfo.new_for_xml("""
<node><interface name='org.example.Backlight'>
  <method name='SetBrightness'>
    <arg type='u' name='percent' direction='in'/>
  </method>
</interface></node>""")

authority = Polkit.Authority.get_sync(None)


def apply_percent(percent):
    with open(f"{DEV}/max_brightness") as f:
        raw = int(f.read()) * percent // 100
    # звичайний open("w") сюди годиться саме тому, що нічого розумного не робить:
    # не створює тимчасового файлу поруч, а кладе значення одним write()
    with open(f"{DEV}/brightness", "w") as f:
        f.write(str(raw))


def on_checked(auth, res, ctx):
    invocation, percent = ctx
    try:
        result = auth.check_authorization_finish(res)
    except GLib.Error as e:                     # спитати не вдалося = відмова
        invocation.return_dbus_error(f"{NAME}.Error.NotAuthorized", str(e))
        return
    if not result.get_is_authorized():
        invocation.return_dbus_error(f"{NAME}.Error.NotAuthorized",
                                     "полкіт відповів «ні»")
        return
    try:
        apply_percent(percent)
    except OSError as e:
        invocation.return_dbus_error(f"{NAME}.Error.Failed", str(e))
        return
    invocation.return_value(None)


def on_call(conn, sender, path, iface, method, params, invocation):
    if method != "SetBrightness":
        invocation.return_dbus_error(f"{NAME}.Error.Failed", "невідомий метод")
        return

    (percent,) = params.unpack()
    if percent > 100:                           # пароль питати нема за що
        invocation.return_dbus_error(f"{NAME}.Error.Failed",
                                     "відсотки поза межами 0…100")
        return

    subject = Polkit.SystemBusName.new(sender)  # особа — з імені з'єднання
    details = Polkit.Details()
    details.insert("brightness", str(percent))

    authority.check_authorization(
        subject, ACTION, details,
        Polkit.CheckAuthorizationFlags.ALLOW_USER_INTERACTION,
        None, on_checked, (invocation, percent))


def on_bus_acquired(conn, name):
    conn.register_object("/org/example/Backlight", NODE.interfaces[0],
                         on_call, None, None)


Gio.bus_own_name(Gio.BusType.SYSTEM, NAME, Gio.BusNameOwnerFlags.NONE,
                 on_bus_acquired, None, None)
GLib.MainLoop().run()
