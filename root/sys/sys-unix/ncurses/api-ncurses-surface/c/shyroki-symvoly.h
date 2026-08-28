typedef struct {
    attr_t  attr;                  /* ознаки й номер пари */
    wchar_t chars[CCHARW_MAX];     /* CCHARW_MAX = 5: основний знак + комбінаційні */
    int     ext_color;             /* номер пари понад 255 */
} cchar_t;

int setcchar(cchar_t *wch, const wchar_t *wc, attr_t attrs, short pair, const void *opts);
int getcchar(const cchar_t *wch, wchar_t *wc, attr_t *attrs, short *pair, void *opts);

int wadd_wch(WINDOW *, const cchar_t *wch);          /* один складений знак */
int waddnwstr(WINDOW *, const wchar_t *wstr, int n); /* рядок широких символів */
int wget_wch(WINDOW *, wint_t *wch);                 /* див. нижче: три різні відповіді */
