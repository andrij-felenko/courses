/* знайти запис про адресу addr в адресному просторі mm */
pgd_t *pgd = pgd_offset(mm, addr);
if (pgd_none(*pgd) || pgd_bad(*pgd))
        return NULL;

p4d_t *p4d = p4d_offset(pgd, addr);   /* на 4 рівнях — тотожність */
if (p4d_none(*p4d) || p4d_bad(*p4d))
        return NULL;

pud_t *pud = pud_offset(p4d, addr);
if (pud_none(*pud) || pud_bad(*pud))
        return NULL;

pmd_t *pmd = pmd_offset(pud, addr);
if (pmd_none(*pmd) || pmd_bad(*pmd))
        return NULL;

return pte_offset_kernel(pmd, addr);  /* запис про саму сторінку */
