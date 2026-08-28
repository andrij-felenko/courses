void fra_print(const fra_point_t *p, int n)
{
    printf("   f, Hz |  |L|, dB |  phase, deg\n");
    printf("---------+---------+------------\n");
    for (int i = 0; i < n; i++)
        printf("%8.1f | %7.2f | %8.1f\n", p[i].f, p[i].mag_db, p[i].phase_deg);

    fra_margins_t m = fra_find_margins(p, n);
    if (m.ok) {
        printf("\nf_кросовера = %.1f Hz,  запас по фазі = %.1f°\n", m.fc, m.pm);
        if (m.f180 > 0.0f)
            printf("f(-180°)    = %.1f Hz,  запас по підсиленню = %.1f dB\n",
                   m.f180, m.gm_db);
        else
            printf("фаза не дійшла до -180° у смузі — запас по підсиленню «нескінченний»\n");
    } else {
        printf("\n|L| не перетнув 0 dB — кросовера в смузі нема (перевір діапазон/амплітуду)\n");
    }
}
