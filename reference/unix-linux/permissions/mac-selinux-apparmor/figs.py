# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Дві незалежні брами на шляху одного open() ───────────────────────────
def fig_two_gates():
    W, H = 1180, 830
    p = []

    CX, BX, BW = 330, 70, 520

    p.append(fitbox(BX, 64, BW, 54, "процес викликає open()", size=15))
    p.append(fitbox(BX, 142, BW, 54, "розбір шляху: знайти inode", size=15))
    p.append(fitbox(BX, 220, BW, 54, "монтування: чи не лише для читання", size=15))
    p.append(fitbox(BX, 298, BW, 68,
                    "класична перевірка\nдев'ять бітів · ACL · мандати",
                    size=15, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(BX, 402, BW, 68,
                    "гачок LSM\nsecurity_inode_permission()",
                    size=15, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(BX, 566, BW, 54, "операція виконується", size=15))

    for y1, y2 in [(118, 142), (196, 220), (274, 298), (366, 402), (470, 566)]:
        p.append(arrow(CX, y1, CX, y2))

    # бічна гілка відмови від класичної перевірки
    p.append(arrow(BX + BW, 332, 700, 332, color=POS))
    p.append(fitbox(706, 300, 420, 64,
                    "EACCES — і гачок\nне викликають узагалі",
                    size=15, fill=RED_FILL, stroke=POS))

    # права панель: що робить модуль
    p.append(rect(706, 398, 420, 176, fill=BG, stroke=NEG))
    p.append(fitbox(720, 410, 392, 44, "модуль політики", size=15,
                    fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(720, 462, 392, 44,
                    "трійка: тип джерела · тип цілі · клас", size=14))
    p.append(fitbox(720, 514, 392, 44,
                    "кеш векторів доступу (AVC)", size=14))
    p.append(arrow(BX + BW, 436, 702, 452))

    p.append(fitbox(706, 616, 420, 56, "0 (дозволено) або −EACCES",
                    size=15, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(916, 574, 916, 616))
    p.append(arrow(702, 644, 596, 606))

    p.append(fitbox(70, 706, 1056, 96,
                    "Обидві брами мають сказати «так», і кожна вміє лише відмовити:\n"
                    "жоден етап не перетворює чужу відмову на дозвіл — тому політика здатна тільки звужувати.",
                    size=15, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'two-gates.svg'), W, H, *p,
           title="Два питання про одне відкриття файлу")


# ── 2. Мітка на об'єкті проти шляху як імені ────────────────────────────────
def fig_label_vs_path():
    W, H = 1180, 600
    p = []

    p.append(fitbox(60, 120, 300, 160,
                    "inode 2359303\n\nsecurity.selinux =\n…:httpd_sys_content_t",
                    size=15, fill=BLUE_FILL, stroke=NEG))
    p.append(text(210, 312, "один об'єкт, два імені", size=14, color=MUTED))

    p.append(fitbox(430, 100, 330, 60, "/var/www/html/index.html", size=14))
    p.append(fitbox(430, 230, 330, 60, "/home/alice/page.html", size=14))
    p.append(arrow(362, 186, 426, 136))
    p.append(arrow(362, 214, 426, 254))

    p.append(text(978, 92, "SELinux питає мітку", size=15, bold=True, color=NEG))
    p.append(fitbox(818, 104, 322, 96,
                    "обидва імені ведуть\nдо одного типу —\nвідповідь одна",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(text(978, 244, "AppArmor питає шлях", size=15, bold=True, color=POS))
    p.append(fitbox(818, 256, 322, 110,
                    "перше ім'я збігається\nз правилом, друге — ні:\nвідповіді дві",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(arrow(764, 128, 814, 146))
    p.append(arrow(764, 262, 814, 296))

    p.append(fitbox(60, 420, 1080, 100,
                    "Мітка є властивістю об'єкта: переживає перейменування, однакова для всіх жорстких посилань.\n"
                    "Шлях є властивістю запису в каталозі — а таких записів у одного об'єкта може бути скільки завгодно.",
                    size=15, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'label-vs-path.svg'), W, H, *p,
           title="Чим назвати сторони: міткою чи шляхом")


# ── 3. Звідки береться домен процесу ────────────────────────────────────────
def fig_domain_transition():
    W, H = 1180, 720
    p = []

    p.append(fitbox(180, 70, 300, 78, "процес init\nдомен init_t",
                    size=15, fill=FILL, stroke=LINE))
    p.append(arrow(484, 109, 546, 109))
    p.append(fitbox(552, 64, 380, 90,
                    "exec /usr/sbin/httpd\nмітка файлу httpd_exec_t",
                    size=15, fill=WARM_FILL, stroke=WARM))

    p.append(rect(310, 206, 560, 196, fill=BG, stroke=NEG))
    p.append(fitbox(326, 218, 528, 42, "політика вирішує, ким стане процес",
                    size=15, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(326, 266, 528, 40, "1 · type_transition для цієї пари", size=14))
    p.append(fitbox(326, 310, 528, 40, "2 · джерелу дозволено перехід", size=14))
    p.append(fitbox(326, 354, 528, 40, "3 · файл визнано входом (entrypoint)", size=14))
    p.append(arrow(742, 156, 640, 202))

    p.append(fitbox(90, 460, 470, 104,
                    "усі три умови виконано —\nновий процес працює в домені httpd_t",
                    size=15, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(620, 460, 470, 128,
                    "запустили копію того самого файлу\nз іншою міткою: входу нема,\n"
                    "переходу нема — процес лишається в init_t",
                    size=15, fill=RED_FILL, stroke=POS))
    p.append(arrow(470, 404, 330, 456))
    p.append(arrow(710, 404, 852, 456))

    p.append(fitbox(90, 626, 1000, 62,
                    "UID процесу в обох випадках той самий: домен призначає політика, а не той, хто запускає.",
                    size=15, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'domain-transition.svg'), W, H, *p,
           title="Домен призначають на exec, і не за проханням процесу")


# ── 4. Два сховища мітки: база відповідностей і xattr на inode ──────────────
def fig_label_stores():
    W, H = 1180, 560
    p = []

    p.append(fitbox(60, 70, 330, 88,
                    "semanage fcontext -a -t тип\n«зразок шляху»",
                    size=15, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(394, 114, 464, 114))
    p.append(fitbox(470, 56, 400, 116,
                    "база відповідностей\nfile_contexts і локальні додатки\nзразок шляху → тип",
                    size=15, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(670, 172, 670, 266))
    p.append(fitbox(898, 178, 252, 88,
                    "restorecon -Rv\nчитає базу\nй переписує мітку",
                    size=14, fill=FILL, stroke=LINE))

    p.append(fitbox(470, 268, 400, 116,
                    "мітка на самому inode\nxattr security.selinux\nце й читає ядро на перевірці",
                    size=15, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(60, 282, 330, 88,
                    "chcon -t тип файл\nпише мітку напряму",
                    size=15, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(394, 326, 464, 326))

    p.append(fitbox(60, 436, 1060, 96,
                    "Переставляння міток (restorecon -R, fixfiles, /.autorelabel) бере тип із бази\n"
                    "і переписує ним xattr — тому мітка від chcon, не занесена в базу, зникає.",
                    size=15, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'label-stores.svg'), W, H, *p,
           title="Де живе мітка і яка команда куди пише")


# ── 5. Маршрут розбору відмови: від Permission denied до модуля ─────────────
def fig_denial_triage():
    W, H = 1240, 1054
    p = []

    BX, BW, CX = 60, 520, 320
    RX, RW = 660, 520

    def step(y, h, s, fill=FILL, stroke=LINE, bold=False):
        p.append(fitbox(BX, y, BW, h, s, size=15, fill=fill, stroke=stroke, bold=bold))

    def side(y, h, s, fill=FILL, stroke=LINE):
        p.append(fitbox(RX, y, RW, h, s, size=15, fill=fill, stroke=stroke))
        p.append(arrow(BX + BW + 6, y + h / 2, RX - 6, y + h / 2))

    step(40, 56, "служба дістає Permission denied",
         fill=RED_FILL, stroke=POS, bold=True)

    step(130, 72, "sudo -u <користувач> читає той самий файл?\n"
                  "так → дев'ять бітів і ACL тут ні до чого")
    side(130, 72, "ні → відмова класична: біти, ACL,\nмонтування лише для читання",
         fill=WARM_FILL, stroke=WARM)

    step(236, 72, "semanage permissive -a <домен>\nповторити спробу — тепер проходить?")
    side(236, 72, "ні → винна не політика", fill=WARM_FILL, stroke=WARM)

    step(342, 72, "ausearch -m AVC -ts recent\nчи є запис про відмову?")
    side(342, 72, "запису нема → semodule -DB зніме\nглушники dontaudit; повторити",
         fill=BLUE_FILL, stroke=NEG)

    step(448, 76, "restorecon -n -v <ціль>\nчи пропонує іншу мітку?")
    side(448, 76, "так → діагноз «мітка»:\nsemanage fcontext -a -t … ; restorecon -Rv",
         fill=GREEN_FILL, stroke=FIELD)

    step(558, 76, "ні → мітка вже така, як має бути\naudit2why: чи закриває це якийсь булеан?")
    side(558, 76, "булеан є → setsebool -P … on;\nвласний модуль не потрібен",
         fill=GREEN_FILL, stroke=FIELD)

    step(668, 76, "audit2allow -M <ім'я>\nпрочитати .te очима, викинути широкі правила",
         fill=WARM_FILL, stroke=WARM, bold=True)

    step(778, 56, "semodule -i <ім'я>.pp")

    step(868, 76, "semanage permissive -d <домен>\nперевірити в Enforcing: журнал чистий",
         fill=GREEN_FILL, stroke=FIELD)

    for y1, y2 in [(96, 130), (202, 236), (308, 342), (414, 448),
                   (524, 558), (634, 668), (744, 778), (834, 868)]:
        p.append(arrow(CX, y1, CX, y2))

    p.append(fitbox(60, 964, 1120, 56,
                    "setenforce 0 у цьому ланцюжку не потрібен жодного разу: "
                    "дозвільним стає рівно один домен.",
                    size=15, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'denial-triage.svg'), W, H, *p,
           title="Від Permission denied до правила: два діагнози й одна розвилка")


if __name__ == '__main__':
    fig_two_gates()
    fig_label_vs_path()
    fig_domain_transition()
    fig_label_stores()
    fig_denial_triage()
    print("ok")
