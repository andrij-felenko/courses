enum WinKind {
    WIN_OK,          // обидва краї вікна — справжні межі ока
    WIN_CLIP_LO,     // вікно впирається у код 0 — око тягнеться нижче діапазону
    WIN_CLIP_HI,     // вікно впирається у range_max-1 — око тягнеться вище
    WIN_NONE         // вікна нема (усе F)
};

WinKind classify(Window w, int n)
{
    if (w.width == 0)          return WIN_NONE;
    if (w.lo == 0)             return WIN_CLIP_LO;   // почалось на самому краю
    if (w.hi == n - 1)         return WIN_CLIP_HI;   // дійшло до самого краю
    return WIN_OK;
}
