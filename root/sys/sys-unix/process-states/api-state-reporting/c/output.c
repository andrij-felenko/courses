/* procps-ng, ps/output.c — літера з ядра плюс шість модифікаторів самої ps */
static int pr_stat(char *restrict const outbuf, const proc_t *restrict const pp){
    int end = 0;
    outbuf[end++] = pp->state;
    if(pp->nice < 0)            outbuf[end++] = '<';
    if(pp->nice > 0)            outbuf[end++] = 'N';
    if(pp->vm_lock)             outbuf[end++] = 'L';
    if(pp->session == pp->tgid) outbuf[end++] = 's';
    if(pp->nlwp > 1)            outbuf[end++] = 'l';
    if(pp->pgrp == pp->tpgid)   outbuf[end++] = '+';
    outbuf[end] = '\0';
    return end;
}
