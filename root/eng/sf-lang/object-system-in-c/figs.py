# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. c-oop-layout: Розкладка примірника та таблиці методів у C ─────────────
def fig_c_oop_layout():
    W, H = 820, 360
    p = []

    p.append(text(410, 24, "Двійкова розкладка примірника та vtable у C (префіксне вкладення)", size=15, bold=True, color=INK))

    # Instance Layout
    ix0 = 40
    iy0 = 70
    iw = 340
    ih = 240

    p.append(rect(ix0, iy0, iw, ih, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(ix0 + iw / 2, iy0 + 22, "Примірник: struct Button (у купі)", size=13, bold=True, color=INK))

    # Button fields
    # Field 0: Widget base (subobject)
    p.append(rect(ix0 + 15, iy0 + 36, iw - 30, 110, fill="#e8f4fc", stroke=NEG, sw=1.5, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 54, "Базовий під-об'єкт: struct Widget base (зсув 0)", size=11, bold=True, color=NEG))

    # Inside Widget base: klass pointer (offset 0)
    p.append(rect(ix0 + 25, iy0 + 64, iw - 50, 36, fill="#ffffff", stroke=POS, sw=1.4, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 82, "WidgetClass *klass (зсув 0, 8 байтів)", size=11, bold=True, color=POS))
    p.append(text(ix0 + iw / 2, iy0 + 95, "Вказівник на спільну таблицю класу", size=9, color=MUTED))

    # Inside Widget base: x, y, width, height
    p.append(rect(ix0 + 25, iy0 + 106, iw - 50, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(ix0 + iw / 2, iy0 + 126, "int x, y, w, h (зсув 8..24, 16 байтів)", size=10, color=INK))

    # Button own fields
    p.append(rect(ix0 + 15, iy0 + 154, iw - 30, 50, fill="#fdf2e9", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 172, "Власні поля Button: (зсув 24..40)", size=11, bold=True, color=FIELD))
    p.append(text(ix0 + iw / 2, iy0 + 192, "char *label · bool is_pressed · int state", size=10, color=INK))

    # Pointer markers
    p.append(text(ix0 + 15, iy0 + ih + 18, "Button* == Widget* == klass* == 0x2000 (нульовий зсув)", size=10, color=NEG, bold=True))

    # Class / Vtable Layout
    cx0 = 440
    cy0 = 70
    cw = 340
    ch = 240

    p.append(rect(cx0, cy0, cw, ch, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(cx0 + cw / 2, cy0 + 22, "Клас / vtable: struct ButtonClass (синглтон)", size=13, bold=True, color=INK))

    # WidgetClass base_class
    p.append(rect(cx0 + 15, cy0 + 36, cw - 30, 110, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(cx0 + cw / 2, cy0 + 54, "struct WidgetClass base_class (зсув 0)", size=11, bold=True, color=FIELD))

    # WidgetClass function pointers
    p.append(rect(cx0 + 25, cy0 + 64, cw - 50, 34, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(cx0 + cw / 2, cy0 + 85, "void (*draw)(Widget *self) → button_draw", size=10, color=INK))

    p.append(rect(cx0 + 25, cy0 + 104, cw - 50, 34, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(cx0 + cw / 2, cy0 + 125, "void (*event)(Widget *self, Event *e)", size=10, color=INK))

    # ButtonClass own methods
    p.append(rect(cx0 + 15, cy0 + 154, cw - 30, 50, fill="#fdf2e9", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx0 + cw / 2, cy0 + 172, "Власні методи ButtonClass: (зсув 16..24)", size=11, bold=True, color=POS))
    p.append(text(cx0 + cw / 2, cy0 + 192, "void (*clicked)(Button *self)", size=10, color=INK))

    p.append(text(cx0 + 15, cy0 + ch + 18, "Таблиця методів створюється один раз у пам'яті", size=10, color=MUTED))

    # Arrow from Instance klass pointer to Class struct
    p.append(arrow(ix0 + iw - 25, iy0 + 82, cx0 + 15, cy0 + 82, color=POS, sw=2.0))
    p.append(text((ix0 + iw + cx0) / 2, iy0 + 75, "klass", size=11, bold=True, color=POS))

    # Bottom explanation box
    b, _, _ = textbox(410, 335, "Динамічний виклик: ((Widget*)btn)->klass->draw((Widget*)btn)  [розв'язання через вказівник klass]", size=11, pad=6, fill="#f1f5f9", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "c-oop-layout.svg"), W, H, *p)


# ── 2. gobject-type-system: Архітектура GType, GTypeClass та GTypeInstance ───
def fig_gobject_type_system():
    W, H = 840, 370
    p = []

    p.append(text(420, 24, "Архітектура системи типів GObject: динамічний реєстр, клас і примірник", size=15, bold=True, color=INK))

    # 1. Registry Box (Left)
    rx0 = 30
    ry0 = 70
    rw = 220
    rh = 240

    p.append(rect(rx0, ry0, rw, rh, fill="#fdf2e9", stroke=POS, sw=1.5, rx=6))
    p.append(text(rx0 + rw / 2, ry0 + 22, "Реєстр GType (рантайм)", size=12, bold=True, color=POS))

    types = [
        ("G_TYPE_INVALID", "0x00"),
        ("G_TYPE_OBJECT", "0x50 (фундаментальний)"),
        ("GTK_TYPE_WIDGET", "0x58 (динамічний)"),
        ("MY_TYPE_BUTTON", "0x60 (динамічний)"),
    ]
    for i, (tname, tval) in enumerate(types):
        yy = ry0 + 42 + i * 46
        p.append(rect(rx0 + 10, yy, rw - 20, 38, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
        p.append(text(rx0 + 16, yy + 16, tname, size=10, bold=True, color=INK, anchor="start"))
        p.append(text(rx0 + 16, yy + 30, "ID: " + tval, size=9, color=MUTED, anchor="start"))

    # 2. GTypeClass Box (Center)
    cx0 = 290
    cy0 = 70
    cw = 240
    ch = 240

    p.append(rect(cx0, cy0, cw, ch, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(cx0 + cw / 2, cy0 + 22, "GTypeClass (синглтон класу)", size=12, bold=True, color=FIELD))

    p.append(rect(cx0 + 10, cy0 + 38, cw - 20, 40, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(cx0 + cw / 2, cy0 + 54, "GType g_type (MY_TYPE_BUTTON)", size=10, bold=True, color=FIELD))
    p.append(text(cx0 + cw / 2, cy0 + 69, "Зворотний зв'язок з реєстром", size=9, color=MUTED))

    p.append(rect(cx0 + 10, cy0 + 86, cw - 20, 68, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(cx0 + cw / 2, cy0 + 102, "Таблиця віртуальних функцій", size=10, bold=True, color=INK))
    p.append(text(cx0 + cw / 2, cy0 + 118, "parent_class vtable pointers", size=9, color=MUTED))
    p.append(text(cx0 + cw / 2, cy0 + 134, "overridden vtable pointers", size=9, color=MUTED))

    p.append(rect(cx0 + 10, cy0 + 162, cw - 20, 64, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(cx0 + cw / 2, cy0 + 180, "Метадані типу", size=10, bold=True, color=INK))
    p.append(text(cx0 + cw / 2, cy0 + 196, "GParamSpec (властивості)", size=9, color=MUTED))
    p.append(text(cx0 + cw / 2, cy0 + 212, "GSignal (ідентифікатори сигналів)", size=9, color=MUTED))

    # 3. GTypeInstance Box (Right)
    ix0 = 570
    iy0 = 70
    iw = 240
    ih = 240

    p.append(rect(ix0, iy0, iw, ih, fill="#e8f4fc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(ix0 + iw / 2, iy0 + 22, "GTypeInstance (об'єкт у купі)", size=12, bold=True, color=NEG))

    p.append(rect(ix0 + 10, iy0 + 38, iw - 20, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 54, "GTypeClass *g_class", size=10, bold=True, color=NEG))
    p.append(text(ix0 + iw / 2, iy0 + 70, "Вказівник на клас (зсув 0)", size=9, color=MUTED))

    p.append(rect(ix0 + 10, iy0 + 88, iw - 20, 40, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 105, "volatile gint ref_count", size=10, bold=True, color=INK))
    p.append(text(ix0 + iw / 2, iy0 + 120, "Атомарний лічильник посилань", size=9, color=MUTED))

    p.append(rect(ix0 + 10, iy0 + 136, iw - 20, 90, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 154, "Дані екземпляра", size=10, bold=True, color=INK))
    p.append(text(ix0 + iw / 2, iy0 + 172, "GData *qdata (асоційовані дані)", size=9, color=MUTED))
    p.append(text(ix0 + iw / 2, iy0 + 190, "Власні поля нащадка", size=9, color=MUTED))
    p.append(text(ix0 + iw / 2, iy0 + 208, "Private struct (якщо є)", size=9, color=MUTED))

    # Connectors
    # Arrow Registry -> Class
    p.append(arrow(rx0 + rw, ry0 + 185, cx0, ry0 + 185, color=POS, sw=1.8))
    # Arrow Instance -> Class
    p.append(arrow(ix0, iy0 + 58, cx0 + cw, cy0 + 58, color=NEG, sw=1.8))

    # Bottom summary box
    b, _, _ = textbox(420, 340, "g_object_new() виділяє пам'ять екземпляра, ініціалізує ref_count = 1 і зв'язує g_class із синглтоном класу", size=11, pad=6, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "gobject-type-system.svg"), W, H, *p)


# ── 3. linux-kobject-model: kobject, kset, ktype та макрос container_of ─────
def fig_linux_kobject_model():
    W, H = 840, 370
    p = []

    p.append(text(420, 24, "Об'єктна модель ядра Linux: вбудований struct kobject та container_of", size=15, bold=True, color=INK))

    # Device Box (Outer enclosing struct)
    dx0 = 40
    dy0 = 66
    dw = 320
    dh = 250

    p.append(rect(dx0, dy0, dw, dh, fill="#fdf2e9", stroke=POS, sw=1.5, rx=6))
    p.append(text(dx0 + dw / 2, dy0 + 20, "struct device (господар об'єкта)", size=12, bold=True, color=POS))

    # Header fields before kobject
    p.append(rect(dx0 + 10, dy0 + 32, dw - 20, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(dx0 + dw / 2, dy0 + 48, "struct device *parent · void *driver_data", size=9, color=INK))
    p.append(text(dx0 + dw / 2, dy0 + 61, "Зсув 0..32 байти від початку struct device", size=9, color=MUTED))

    # Embedded kobject at offset 32
    kx0 = dx0 + 10
    ky0 = dy0 + 74
    kw = dw - 20
    kh = 130

    p.append(rect(kx0, ky0, kw, kh, fill="#e8f4fc", stroke=NEG, sw=1.5, rx=4))
    p.append(text(kx0 + kw / 2, ky0 + 18, "struct kobject kobj (зсув offsetof = 32B)", size=11, bold=True, color=NEG))

    p.append(rect(kx0 + 10, ky0 + 26, kw - 20, 24, fill="#ffffff", stroke=LINE, sw=0.8, rx=3))
    p.append(text(kx0 + kw / 2, ky0 + 42, "const char *name · struct list_head entry", size=9, color=INK))

    p.append(rect(kx0 + 10, ky0 + 54, kw - 20, 24, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(kx0 + kw / 2, ky0 + 70, "struct kref kref (лічильник посилань)", size=9, bold=True, color=NEG))

    p.append(rect(kx0 + 10, ky0 + 82, kw - 20, 20, fill="#ffffff", stroke=LINE, sw=0.8, rx=3))
    p.append(text(kx0 + kw / 2, ky0 + 96, "struct kset *kset (групування в sysfs)", size=9, color=INK))

    p.append(rect(kx0 + 10, ky0 + 104, kw - 20, 20, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
    p.append(text(kx0 + kw / 2, ky0 + 118, "const struct kobj_type *ktype", size=9, bold=True, color=FIELD))

    # Trailer fields
    p.append(rect(dx0 + 10, dy0 + 210, dw - 20, 30, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(dx0 + dw / 2, dy0 + 229, "dev_t devt · struct bus_type *bus (інші поля)", size=9, color=INK))

    # Right Column: struct kobj_type (ktype) and sysfs_ops
    tx0 = 420
    ty0 = 66
    tw = 380
    th = 115

    p.append(rect(tx0, ty0, tw, th, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(tx0 + dw / 2 + 30, ty0 + 20, "struct kobj_type (поведінка та операції sysfs)", size=12, bold=True, color=FIELD))

    p.append(rect(tx0 + 10, ty0 + 32, tw - 20, 34, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(tx0 + tw / 2, ty0 + 48, "void (*release)(struct kobject *kobj)", size=10, bold=True, color=FIELD))
    p.append(text(tx0 + tw / 2, ty0 + 61, "Викликається при kref == 0 (деструктор)", size=9, color=MUTED))

    p.append(rect(tx0 + 10, ty0 + 70, tw - 20, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(tx0 + tw / 2, ty0 + 86, "const struct sysfs_ops *sysfs_ops", size=10, bold=True, color=INK))
    p.append(text(tx0 + tw / 2, ty0 + 100, "show() та store() для атрибутів у /sys", size=9, color=MUTED))

    # Right Column Bottom: struct kset
    sx0 = 420
    sy0 = 195
    sw = 380
    sh = 120

    p.append(rect(sx0, sy0, sw, sh, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(sx0 + sw / 2, sy0 + 20, "struct kset (ієрархія та каталог /sys)", size=12, bold=True, color=INK))

    p.append(rect(sx0 + 10, sy0 + 32, sw - 20, 34, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(sx0 + sw / 2, sy0 + 48, "struct list_head list — список усіх вкладених kobject", size=9, color=INK))
    p.append(text(sx0 + sw / 2, sy0 + 61, "Власний struct kobject kobj для каталогу", size=9, color=MUTED))

    p.append(rect(sx0 + 10, sy0 + 72, sw - 20, 38, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(sx0 + sw / 2, sy0 + 88, "const struct kset_uevent_ops *uevent_ops", size=9, color=INK))
    p.append(text(sx0 + sw / 2, sy0 + 103, "Надсилання подій (hotplug uevents) через netlink до udev", size=9, color=MUTED))

    # Arrows
    p.append(arrow(kx0 + kw, ky0 + 114, tx0, ty0 + 50, color=FIELD, sw=1.8))
    p.append(arrow(kx0 + kw, ky0 + 92, sx0, sy0 + 50, color=LINE, sw=1.8))

    # Bottom container_of formula box
    b, _, _ = textbox(420, 342, "container_of(ptr, struct device, kobj) = (struct device*)((char*)ptr - offsetof(struct device, kobj))", size=10, pad=6, fill="#fff7ed", stroke=POS)
    p.append(b)

    render(os.path.join(OUT, "linux-kobject-model.svg"), W, H, *p)


# ── 4. com-binary-layout: Двійковий інтерфейс COM, IUnknown та vtable ────────
def fig_com_binary_layout():
    W, H = 840, 360
    p = []

    p.append(text(420, 24, "Двійковий стандарт COM (Component Object Model): vtable у C та C++", size=15, bold=True, color=INK))

    # COM Instance (Left)
    ix0 = 40
    iy0 = 70
    iw = 320
    ih = 240

    p.append(rect(ix0, iy0, iw, ih, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(ix0 + iw / 2, iy0 + 22, "Примірник COM-об'єкта (вказівник pUnk)", size=12, bold=True, color=INK))

    p.append(rect(ix0 + 15, iy0 + 40, iw - 30, 48, fill="#e8f4fc", stroke=NEG, sw=1.5, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 58, "IMyInterfaceVtbl *lpVtbl (зсув 0)", size=11, bold=True, color=NEG))
    p.append(text(ix0 + iw / 2, iy0 + 76, "Вказівник на таблицю методів", size=9, color=MUTED))

    p.append(rect(ix0 + 15, iy0 + 98, iw - 30, 40, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 116, "LONG m_refCount (лічильник посилань)", size=10, bold=True, color=INK))
    p.append(text(ix0 + iw / 2, iy0 + 130, "Керується AddRef() та Release()", size=9, color=MUTED))

    p.append(rect(ix0 + 15, iy0 + 148, iw - 30, 70, fill="#fdf2e9", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(ix0 + iw / 2, iy0 + 168, "Внутрішні дані компонента", size=10, bold=True, color=FIELD))
    p.append(text(ix0 + iw / 2, iy0 + 186, "int m_data · HANDLE m_mutex", size=9, color=INK))
    p.append(text(ix0 + iw / 2, iy0 + 204, "Інкапсульовані приватні змінні", size=9, color=MUTED))

    # COM Vtable (Right)
    vx0 = 420
    vy0 = 70
    vw = 380
    vh = 240

    p.append(rect(vx0, vy0, vw, vh, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(vx0 + vw / 2, vy0 + 22, "IMyInterfaceVtbl (Таблиця функцій у пам'яті)", size=12, bold=True, color=FIELD))

    vmethods = [
        ("[0] HRESULT QueryInterface(REFIID riid, void **ppv)", POS, True),
        ("[1] ULONG AddRef(void)", POS, True),
        ("[2] ULONG Release(void)", POS, True),
        ("[3] HRESULT GetData(LONG *pVal)", INK, False),
        ("[4] HRESULT SetData(LONG val)", INK, False),
    ]

    for i, (mname, mcolor, is_iunk) in enumerate(vmethods):
        yy = vy0 + 38 + i * 38
        p.append(rect(vx0 + 10, yy, vw - 20, 32, fill="#ffffff", stroke=mcolor if is_iunk else LINE, sw=1.2 if is_iunk else 0.8, rx=3))
        prefix = "IUnknown: " if is_iunk else "Custom: "
        p.append(text(vx0 + 16, yy + 20, prefix + mname, size=9.5, bold=is_iunk, color=mcolor, anchor="start"))

    # Arrow from lpVtbl to Vtable
    p.append(arrow(ix0 + iw - 15, iy0 + 64, vx0 + 10, vy0 + 54, color=NEG, sw=2.0))

    # Bottom comparison call syntax
    b, _, _ = textbox(420, 338, "Виклик у C: p->lpVtbl->QueryInterface(p, ...)  ↔  Виклик у C++: p->QueryInterface(...)  [однаковий ABI]", size=10, pad=6, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "com-binary-layout.svg"), W, H, *p)


if __name__ == "__main__":
    fig_c_oop_layout()
    fig_gobject_type_system()
    fig_linux_kobject_model()
    fig_com_binary_layout()
    print("All figures generated successfully.")
