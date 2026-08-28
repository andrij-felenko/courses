/* Перемкнути в ручний: задати вихід, який тримати руками */
void pid_set_manual(pid_t *c, float manual_output)
{
    c->manual  = true;
    c->man_out = manual_output;
}

/* Повернути в автомат: нічого спеціального робити НЕ треба —
   I_term уже відстежив ручний вихід, тож перехід безстрибковий. */
void pid_set_auto(pid_t *c)
{
    c->manual = false;
}

/* Зміна коефіцієнтів на льоту — теж безстрибково:
   I_term тримається в одиницях виходу, тож нові Kp/Ti його не масштабують. */
void pid_set_tunings(pid_t *c, float Kp, float Ti, float Td)
{
    c->Kp = Kp;
    c->Ti = Ti;
    c->Td = Td;
    if (Ti > 0.0f && Td > 0.0f)
        c->Tt = sqrtf(Ti * Td);      /* √(Ti·Td) — усталене правило */
    else
        c->Tt = (Ti > 0.0f) ? Ti : 0.0f;   /* для чистого PI: Tt ≈ Ti */
}
