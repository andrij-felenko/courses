/* Критерії виключення шляху з активної маршрутизації */
static bool nvme_path_is_disabled(struct nvme_ns *ns)
{
    /* 1. Контролер має перебувати у стані LIVE */
    if (ns->ctrl->state != NVME_CTRL_LIVE)
        return true;
        
    /* 2. Стан ANA не повинен бути Inaccessible або Persistent Loss */
    if (ns->ana_state == NVME_ANA_INACCESSIBLE ||
        ns->ana_state == NVME_ANA_PERSISTENT_LOSS)
        return true;
        
    /* 3. Перевірка, чи не заморожено чергу введення-виведення */
    if (test_bit(NVME_NS_REMOVING, &ns->flags))
        return true;
        
    return false;
}
