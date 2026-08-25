# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Одне повідомлення програє перегони, пара start/end — ні ───────────────
def fig_invalidate_window():
    W, H = 1360, 660
    p = []

    ROWS = [158, 248, 338, 428]
    RH = 76

    p.append(text(38, 132, "час", size=12, color=MUTED))
    p.append(arrow(38, 150, 38, 500, MUTED, sw=1.4))
    p.append(line(672, 40, 672, 610, MUTED, sw=1.1, dash="5,5"))

    # ── ліва половина: одноточкове повідомлення ──
    p.append(fitbox(70, 40, 560, 50,
                    "одне повідомлення в мить зміни",
                    size=14.5, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(fitbox(70, 104, 270, 38, "ядро", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))
    p.append(fitbox(360, 104, 270, 38, "драйвер", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    left = [
        ("ущільнення вирішує\nперенести сторінку",
         "збій пристрою: читає\nтаблиці, бачить кадр K"),
        ("править запис таблиці,\nскидає TLB",
         ""),
        ("кличе зворотний виклик\n«кадру K тут немає»",
         "витирає кадр K,\nякого ще не записав"),
        ("кадр K уже виданий\nкомусь іншому",
         "дописує кадр K\nзі свого прочитаного"),
    ]
    for i, (k, d) in enumerate(left):
        y = ROWS[i]
        p.append(fitbox(70, y, 270, RH, k, size=12,
                        fill=SOFT, stroke=NEG, sw=1.4, color=INK))
        if d:
            p.append(fitbox(360, y, 270, RH, d, size=12,
                            fill="#fff", stroke=POS, sw=1.4, color=INK))

    p.append(fitbox(70, 520, 560, 84,
                    "пристрій пише за старим номером кадру —\nу пам'ять, яка вже належить іншому",
                    size=13.5, fill=WARM, stroke=POS, sw=1.8, color=INK))

    # ── права половина: пара start/end ──
    p.append(fitbox(714, 40, 560, 50,
                    "пара start / end огороджує весь час зміни",
                    size=14.5, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(fitbox(714, 104, 270, 38, "ядро", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))
    p.append(fitbox(1004, 104, 270, 38, "драйвер", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    right = [
        ("invalidate_range_start:\nсторінки ще на місці",
         "знімає свої записи\nй закриває вхід"),
        ("править записи, скидає\nTLB, звільняє кадри",
         "збій пристрою тут\nвідступає й чекає"),
        ("invalidate_range_end",
         "вхід у діапазон\nзнову відкрито"),
        ("",
         "перечитує таблиці\nй будує за новим"),
    ]
    for i, (k, d) in enumerate(right):
        y = ROWS[i]
        if k:
            p.append(fitbox(714, y, 270, RH, k, size=12,
                            fill=SOFT, stroke=NEG, sw=1.4, color=INK))
        p.append(fitbox(1004, y, 270, RH, d, size=12,
                        fill="#fff", stroke=FIELD, sw=1.4, color=INK))

    p.append(fitbox(714, 520, 560, 84,
                    "усередині вікна жодне прочитане з таблиць значення\nне має шансу осісти в табличці пристрою",
                    size=13.5, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    return render(os.path.join(OUT, "invalidate-window.svg"), W, H, *p,
                  title="Чому скасування має бути проміжком, а не миттю")


# ── 2. Два різні протоколи для двох різних апаратур ─────────────────────────
def fig_two_protocols():
    W, H = 1340, 700
    p = []

    cols = [
        (70, "має ВЛАСНУ копію відображень", NEG, COOL,
         "гість віртуальної машини,\nграфічний прискорювач",
         "своя табличка адрес\nі свій кеш перекладів",
         "розібрати свої записи\nй не пускати нових,\nдоки триває зміна",
         "пара invalidate_range_start\n/ invalidate_range_end",
         "однієї точки замало: між\nчитанням таблиць і записом\nу свою табличку встигає\nвклинитися перенесення"),
        (710, "ходить у ТІ САМІ таблиці, що й процесор", FIELD, GREENF,
         "IOMMU зі спільною\nвіртуальною адресацією",
         "таблиць своїх немає,\nє лише кеш перекладів",
         "скинути кеш перекладів\nрівно там, де ядро скидає\nTLB процесора",
         "arch_invalidate_secondary_tlbs\n(до ядра 6.6 — invalidate_range)",
         "start зарано: запис ще\nчинний і його перечитають;\nend запізно: сторінку вже\nвіддано іншому"),
    ]

    for x, head, accent, fillc, who, has, todo, call, wrong in cols:
        p.append(fitbox(x, 44, 560, 52, head, size=14.5,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 116, 560, 66, who, size=12.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(x, 202, 560, 66, has, size=12.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(x, 288, 560, 88, todo, size=12.5,
                        fill="#fff", stroke=accent, sw=1.5, color=INK))
        p.append(fitbox(x, 396, 560, 70, call, size=12.5,
                        fill=fillc, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(x, 486, 560, 104, wrong, size=12.5,
                        fill=WARM, stroke=POS, sw=1.4, color=INK))

    p.append(text(660, 154, "хто це", size=12, color=MUTED))
    p.append(text(660, 240, "що має", size=12, color=MUTED))
    p.append(text(660, 336, "що робить", size=12, color=MUTED))
    p.append(text(660, 435, "який виклик", size=12, color=MUTED))
    p.append(text(660, 542, "чому не інший", size=12, color=MUTED))

    p.append(fitbox(70, 610, 1200, 60,
                    "плутанина між цими двома шляхами й була джерелом тихих псувань пам'яті — саме тому виклик перейменували",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "two-protocols.svg"), W, H, *p,
                  title="Копія відображень і спільні таблиці вимагають різних місць вклинення")


# ── 3. Узгодження обробника збою зі скасуваннями через послідовний лічильник ──
def fig_interval_retry():
    W, H = 1340, 700
    p = []

    p.append(fitbox(70, 40, 540, 50, "обробник збою пристрою", size=14,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(730, 40, 540, 50, "зворотний виклик скасування", size=14,
                    fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    ROWS = [110, 194, 278, 362, 446]
    RH = 72

    left = [
        "seq = mmu_interval_read_begin()\nчекає, якщо зміна саме триває",
        "читає таблиці процесу,\nзнаходить кадри",
        "бере ЗАМОК ДРАЙВЕРА",
        "mmu_interval_read_retry(seq)?\nтак → усе спочатку",
        "ставить записи в табличку\nпристрою, віддає замок",
    ]
    right = [
        "ядро змінює відображення\nв зареєстрованому проміжку",
        "бере ТОЙ САМИЙ\nзамок драйвера",
        "mmu_interval_set_seq(cur_seq)",
        "знімає свої записи\nдля цього діапазону",
        "віддає замок",
    ]
    for i in range(5):
        y = ROWS[i]
        p.append(fitbox(70, y, 540, RH, left[i], size=12.5,
                        fill=SOFT if i != 3 else "#fff",
                        stroke=NEG, sw=1.4 if i != 3 else 1.8, color=INK))
        p.append(fitbox(730, y, 540, RH, right[i], size=12.5,
                        fill=SOFT if i != 2 else "#fff",
                        stroke=POS, sw=1.4 if i != 2 else 1.8, color=INK))

    for i in range(4):
        p.append(arrow(340, ROWS[i] + RH, 340, ROWS[i + 1], MUTED, sw=1.4))
        p.append(arrow(1000, ROWS[i] + RH, 1000, ROWS[i + 1], MUTED, sw=1.4))

    p.append(fitbox(70, 542, 1200, 60,
                    "число змінюють під тим самим замком, під яким його звіряють",
                    size=14, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(fitbox(70, 618, 1200, 60,
                    "тому між звіркою і встановленням записів скасування не встигає вклинитися, а сутичка коштує лише повтору",
                    size=13, fill="#fff", stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "interval-retry.svg"), W, H, *p,
                  title="Як обробник збою драйвера узгоджується зі скасуваннями")


# ── 4. Три різні часи життя: структура mm, адресний простір, підписка ────────
def fig_mirror_lifetime():
    W, H = 1372, 624
    p = []

    COLS = [330, 588, 846, 1104]
    CW = 250
    LX, LW = 28, 286

    heads = [
        "ioctl ATTACH\nна діапазон процесу",
        "робота:\nзбої пристрою",
        "процес завершився\n(exit_mmap)",
        "close(fd) →\n.release",
    ]
    p.append(fitbox(LX, 40, LW, 78, "що коли живе", size=13,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED, bold=True))
    for x, h in zip(COLS, heads):
        p.append(fitbox(x, 40, CW, 78, h, size=12.5,
                        fill=COOL, stroke=NEG, sw=1.7, color=NEG, bold=True))

    rows = [
        (132, "структура mm_struct\n(mmgrab / mmdrop)",
         [("mmgrab() — беремо\nдовге посилання", GREENF, FIELD),
          ("жива", SOFT, MUTED),
          ("жива: тримаємо\nїї МИ", GREENF, FIELD),
          ("mmdrop() —\nаж тепер звільнено", SOFT, MUTED)]),
        (228, "адресний простір:\nVMA й таблиці сторінок",
         [("живий", SOFT, MUTED),
          ("mmget_not_zero()\nвдається — читаємо\nтаблиці", GREENF, FIELD),
          ("розібрано;\nmmget_not_zero() → 0,\nзбій віддає -EFAULT", WARM, POS),
          ("—", PALE, MUTED)]),
        (324, "сповіщувач діапазону\n(insert / remove)",
         [("insert() — вузол\nв інтервальному дереві", GREENF, FIELD),
          ("приходять\nзворотні виклики", SOFT, MUTED),
          ("ще в дереві, але\nскасувань більше\nне буде", WARM, POS),
          ("remove(): гарантія,\nщо викликів немає\nй не буде", GREENF, FIELD)]),
    ]
    RH = 86
    for y, label, cells in rows:
        p.append(fitbox(LX, y, LW, RH, label, size=12.5,
                        fill=PALE, stroke=MUTED, sw=1.3, color=INK, bold=True))
        for x, (s, fillc, strokec) in zip(COLS, cells):
            p.append(fitbox(x, y, CW, RH, s, size=12,
                            fill=fillc, stroke=strokec, sw=1.4, color=INK))

    p.append(fitbox(LX, 430, 1326, 76,
                    "mmgrab тримає СТРУКТУРУ mm_struct, mmget — сам АДРЕСНИЙ ПРОСТІР:\n"
                    "перше дешеве й на весь час підписки, друге — лише на час читання таблиць",
                    size=13, fill="#fff", stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(LX, 518, 1326, 76,
                    "смерть процесу не знімає підписку: зняти її мусить .release —\n"
                    "і саме тому структуру mm треба тримати живою аж до нього",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "mirror-lifetime.svg"), W, H, *p,
                  title="Час життя структури mm, адресного простору й підписки не збігаються")


if __name__ == "__main__":
    print(fig_invalidate_window())
    print(fig_two_protocols())
    print(fig_interval_retry())
    print(fig_mirror_lifetime())
