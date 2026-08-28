/* backlightd.c
   gcc backlightd.c -o backlightd $(pkg-config --cflags --libs gio-2.0 polkit-gobject-1) */
#include <gio/gio.h>
#include <polkit/polkit.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define DEV    "/sys/class/backlight/intel_backlight"
#define ACTION "org.example.backlightd.set-brightness"

static PolkitAuthority *authority;

static const gchar *IFACE_XML =
  "<node><interface name='org.example.Backlight'>"
  "  <method name='SetBrightness'>"
  "    <arg type='u' name='percent' direction='in'/>"
  "  </method>"
  "</interface></node>";

typedef struct { GDBusMethodInvocation *inv; guint32 percent; } Request;

/* sysfs не терпить «атомарного» запису через тимчасовий файл і rename,
   тому g_file_set_contents() тут не годиться: значення йде одним write(). */
static gboolean apply_percent(guint32 percent, GError **err)
{
    g_autofree gchar *max_s = NULL;
    if (!g_file_get_contents(DEV "/max_brightness", &max_s, NULL, err))
        return FALSE;

    guint64 raw = g_ascii_strtoull(max_s, NULL, 10) * percent / 100;
    g_autofree gchar *out = g_strdup_printf("%" G_GUINT64_FORMAT, raw);

    int fd = open(DEV "/brightness", O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        g_set_error(err, G_IO_ERROR, g_io_error_from_errno(errno),
                    "brightness: %s", g_strerror(errno));
        return FALSE;
    }
    gboolean ok = write(fd, out, strlen(out)) > 0;
    int saved = errno;
    close(fd);
    if (!ok)
        g_set_error(err, G_IO_ERROR, g_io_error_from_errno(saved),
                    "write: %s", g_strerror(saved));
    return ok;
}

static void on_checked(GObject *src, GAsyncResult *res, gpointer data)
{
    Request *r = data;
    GError *err = NULL;
    PolkitAuthorizationResult *ar =
        polkit_authority_check_authorization_finish(POLKIT_AUTHORITY(src), res, &err);

    /* Одна гілка на «ні» і на «спитати не вдалося»: невідома особа — це відмова.
       Саме розділення цих двох випадків коштувало полкітові CVE-2021-3560. */
    if (ar == NULL || !polkit_authorization_result_get_is_authorized(ar)) {
        g_dbus_method_invocation_return_error(r->inv, G_DBUS_ERROR,
            G_DBUS_ERROR_ACCESS_DENIED, "Змінювати яскравість не дозволено (%s)",
            err ? err->message : "полкіт відповів «ні»");
    } else if (!apply_percent(r->percent, &err)) {
        g_dbus_method_invocation_return_gerror(r->inv, err);
    } else {
        g_dbus_method_invocation_return_value(r->inv, NULL);
    }

    g_clear_error(&err);
    g_clear_object(&ar);
    g_free(r);
}

static void handle_call(GDBusConnection *conn, const gchar *sender,
                        const gchar *path, const gchar *iface,
                        const gchar *method, GVariant *params,
                        GDBusMethodInvocation *inv, gpointer user_data)
{
    guint32 percent;

    if (g_strcmp0(method, "SetBrightness") != 0) {
        g_dbus_method_invocation_return_error_literal(inv, G_DBUS_ERROR,
            G_DBUS_ERROR_UNKNOWN_METHOD, method);
        return;
    }

    g_variant_get(params, "(u)", &percent);
    if (percent > 100) {                       /* пароль питати нема за що */
        g_dbus_method_invocation_return_error_literal(inv, G_DBUS_ERROR,
            G_DBUS_ERROR_INVALID_ARGS, "відсотки поза межами 0…100");
        return;
    }

    /* Особа — з імені з'єднання; клієнт про себе не каже нічого. */
    PolkitSubject *subject = polkit_system_bus_name_new(sender);
    PolkitDetails *details = polkit_details_new();
    g_autofree gchar *shown = g_strdup_printf("%u", percent);
    polkit_details_insert(details, "brightness", shown);

    Request *r = g_new0(Request, 1);
    r->inv = inv;
    r->percent = percent;

    polkit_authority_check_authorization(
        authority, subject, ACTION, details,
        POLKIT_CHECK_AUTHORIZATION_FLAGS_ALLOW_USER_INTERACTION,
        NULL /* GCancellable */, on_checked, r);

    g_object_unref(details);
    g_object_unref(subject);
}

static const GDBusInterfaceVTable VTABLE = { handle_call, NULL, NULL, { 0 } };

static void on_bus_acquired(GDBusConnection *conn, const gchar *name, gpointer u)
{
    GDBusNodeInfo *node = g_dbus_node_info_new_for_xml(IFACE_XML, NULL);
    g_dbus_connection_register_object(conn, "/org/example/Backlight",
                                      node->interfaces[0], &VTABLE,
                                      NULL, NULL, NULL);
}

int main(void)
{
    GError *err = NULL;

    authority = polkit_authority_get_sync(NULL, &err);
    if (authority == NULL) {
        g_printerr("немає арбітра: %s\n", err->message);
        return 1;              /* без полкіта ця служба не працює — і не мусить */
    }

    g_bus_own_name(G_BUS_TYPE_SYSTEM, "org.example.Backlight",
                   G_BUS_NAME_OWNER_FLAGS_NONE,
                   on_bus_acquired, NULL, NULL, NULL, NULL);
    g_main_loop_run(g_main_loop_new(NULL, FALSE));
    return 0;
}
