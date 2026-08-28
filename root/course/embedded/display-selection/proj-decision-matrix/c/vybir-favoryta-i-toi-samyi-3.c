int main(void)
{
    int n_crit = sizeof(crit_field) / sizeof(crit_field[0]);
    int n_cand = sizeof(cand_field) / sizeof(cand_field[0]);

    printf("Сценарій 1 — вуличний давач:\n");
    int w1 = pick_winner(crit_field, n_crit, cand_field, n_cand);
    printf("  → фаворит: %s\n\n", cand_field[w1].name);

    printf("Сценарій 2 — кухонний прилад:\n");
    /* n_crit той самий — критеріїв стільки ж, лише ваги інші */
    int w2 = pick_winner(crit_kitchen, n_crit, cand_field, n_cand);
    printf("  → фаворит: %s\n", cand_field[w2].name);
    return 0;
}
