/* Той самий зсув-плюс, що в hashmap.c самого ncurses. */
static uint64_t row_hash(const Cell *row)
{
        uint64_t h = 0;

        for (int x = 0; x < COLS; x++) {
                h += (h << 5) + row[x].ch;
                h += (h << 5) + row[x].attr;
        }
        return h;
}

static int uniq(const uint64_t *h, int i)
{
        for (int k = 0; k < ROWS; k++)
                if (k != i && h[k] == h[i])
                        return 0;
        return 1;
}

typedef struct { int d, top, bot; } Shift;   /* d > 0 — вміст поїхав УНИЗ */

static Shift find_shift(const Screen *cur, const Screen *ns)
{
        uint64_t ho[ROWS], hn[ROWS];
        Shift none = { 0, 0, 0 }, s = { 0, 0, 0 };
        int best_d = 0, votes = 0, run = 0, blen = 0, bot = 0;

        for (int y = 0; y < ROWS; y++) {
                ho[y] = row_hash(cur->c[y]);
                hn[y] = row_hash(ns->c[y]);
        }

        /* Голосують лише рядки, неповторні з обох боків. */
        for (int d = -(ROWS - 1); d <= ROWS - 1; d++) {
                int v = 0;

                if (d == 0)
                        continue;
                for (int y = 0; y < ROWS; y++) {
                        int src = y - d;

                        if (src < 0 || src >= ROWS)
                                continue;
                        if (hn[y] == ho[src] && uniq(hn, y) && uniq(ho, src))
                                v++;
                }
                if (v > votes) {
                        votes = v;
                        best_d = d;
                }
        }
        if (votes == 0)
                return none;

        /* Найдовша суцільна смуга при цьому зсуві — уже без вимоги неповторності. */
        for (int y = 0; y < ROWS; y++) {
                int src = y - best_d;

                if (src >= 0 && src < ROWS && hn[y] == ho[src]) {
                        if (++run > blen) {
                                blen = run;
                                bot = y;
                        }
                } else {
                        run = 0;
                }
        }
        if (blen < 3)            /* дрібний збіг команди прокручування не вартий */
                return none;

        s.d = best_d;
        s.bot = bot;
        s.top = bot - blen + 1;
        return s;
}

/* Смуга прокручування, одна команда — і та сама зміна у власній копії. */
static void scroll_lines(Wire *w, Screen *cur, Shift s)
{
        Screen old = *cur;
        Cell blank = { ' ', 0 };
        char b[24];
        int n;
        int rtop = s.top < s.top - s.d ? s.top : s.top - s.d;   /* і приймачі, */
        int rbot = s.bot > s.bot - s.d ? s.bot : s.bot - s.d;   /* і джерела    */

        if (rtop < 0)
                rtop = 0;
        if (rbot > ROWS - 1)
                rbot = ROWS - 1;

        n = snprintf(b, sizeof b, "\033[%d;%dr", rtop + 1, rbot + 1);  /* смуга */
        put(w, b, (size_t) n);
        cup(w, rtop, 0);
        n = snprintf(b, sizeof b, "\033[%d%c", s.d > 0 ? s.d : -s.d,
                     s.d > 0 ? 'L' : 'M');                            /* вставити / вилучити */
        put(w, b, (size_t) n);
        put(w, "\033[r", 3);                                          /* смуга назад */
        w->cx = -1;              /* куди IL і DL лишають курсор — не вгадуємо */

        for (int y = rtop; y <= rbot; y++) {
                int src = y - s.d;

                for (int x = 0; x < COLS; x++)
                        cur->c[y][x] = (src >= rtop && src <= rbot) ? old.c[src][x] : blank;
        }
}
