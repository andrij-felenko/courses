static int new_picture(const slice_t *c, const slice_t *p)
{
    /* Найдешевша ознака: слайс почався з нульового макроблока. Вона
       працює, бо всі поширені кодувальники видають слайси кадру
       в порядку зростання номерів макроблоків. */
    if (c->first_mb == 0) return 1;

    /* А це вже точний перелік зі стандарту — на випадок, коли слайси
       йдуть не по порядку або в потік домішано надлишкові копії. */
    if (c->frame_num        != p->frame_num)        return 1;
    if (c->pps_id           != p->pps_id)           return 1;
    if (c->field_pic        != p->field_pic)        return 1;
    if (c->bottom_field     != p->bottom_field)     return 1;
    if ((c->ref_idc == 0)   != (p->ref_idc == 0))   return 1;
    if (c->poc_lsb          != p->poc_lsb)          return 1;
    if (c->delta_poc_bottom != p->delta_poc_bottom) return 1;
    if (c->delta_poc0       != p->delta_poc0)       return 1;
    if (c->delta_poc1       != p->delta_poc1)       return 1;
    if ((c->type == 5)      != (p->type == 5))      return 1;
    if (c->type == 5 && c->idr_pic_id != p->idr_pic_id) return 1;
    return 0;
}
