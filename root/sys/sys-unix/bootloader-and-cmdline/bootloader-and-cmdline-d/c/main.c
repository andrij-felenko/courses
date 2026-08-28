static int __init loglevel(char *str)
{
        int newlevel;

        /* значення міняємо лише тоді, коли рядок справді розібрався:
           тихий нуль замість рівня журналу дуже важко потім знайти */
        if (get_option(&str, &newlevel)) {
                console_loglevel = newlevel;
                return 0;
        }

        return -EINVAL;         /* у журналі буде «Malformed early option» */
}

early_param("loglevel", loglevel);
