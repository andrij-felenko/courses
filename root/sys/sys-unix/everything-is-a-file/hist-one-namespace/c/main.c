/* Plan 9: набрати TCP-з'єднання самими лише файловими операціями */
char buf[16], path[64];

int cfd = open("/net/tcp/clone", ORDWR);   /* виділяє вільне з'єднання */
int n = read(cfd, buf, sizeof buf - 1);    /* його номер, текстом: "3"  */
buf[n] = '\0';

fprint(cfd, "connect 10.0.0.2!80");        /* дієслово — рядком у ctl   */

snprint(path, sizeof path, "/net/tcp/%s/data", buf);
int dfd = open(path, ORDWR);               /* далі — звичайні read/write */
