case M_DCP_SEEN:                        /* BC1.2 сказав: перед нами DCP     */
    dpdm_set((struct code){ DAC_0V6, DAC_HIZ });   /* D+ тримаємо, D− слухаємо */
    go(M_DP_HOLD, now);
    break;

case M_DP_HOLD:
    if (now - t_mark < T_DP_HOLD_MS) break;        /* 1.25 с — і ані мілісекунди менше */
    go(M_DM_CHECK, now);
    break;

case M_DM_CHECK:
    /* Блок мав розімкнути перемичку й притягти D− донизу через ≈20 кОм.  */
    if (dm_below_325mv()) go(M_QC_YES, now);       /* перемичку знято: говорити безпечно */
    else                  go(M_QC_NO,  now);       /* мовчить → перемичка на місці → не чіпати */
    break;
