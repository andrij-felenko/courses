static void case_dup(void)
{
    int a = fresh(0);
    int b = dup(a);                 /* новий номер, той самий опис */
    write(a, "AAAAA", 5);
    write(b, "BBBBB", 5);
    witness("dup", getpid(), a, getpid(), b);
    close(a); close(b);
}

static void case_two_opens(void)
{
    int a = fresh(0);
    int b = open(PROBE, O_WRONLY);  /* БЕЗ O_TRUNC: інакше зітремо доказ */
    write(a, "AAAAA", 5);
    write(b, "BBBBB", 5);
    witness("open + open", getpid(), a, getpid(), b);
    close(a); close(b);
}
