typedef struct statsblk {
    double grpsize1;       /* Порядок групи Aut(G) = grpsize1 * 10^(grpsize2) */
    int grpsize2;          /* Порядок степеня 10 для великих груп */
    int numorbits;         /* Кількість орбіт вершин під дією Aut(G) */
    int numgenerators;     /* Кількість знайдених генераторів Aut(G) */
    unsigned long numnodes;/* Кількість відвіданих вузлів у дереві пошуку */
    unsigned long numbadleaves; /* Кількість некорисних листків */
    int maxlevel;          /* Максимальна глибина рекурсивного дерева */
    unsigned long canupdates;   /* Кількість оновлень канонічного підпису */
    int invarcounts;       /* Кількість викликів важкого інваріанта */
    int invarlevel;        /* Рівень, на якому інваріант був ефективним */
} statsblk;
