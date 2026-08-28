// Викликається, коли вивід ALERT притягнув лінію переривання.
void tcpc_on_alert(void) {
    uint16_t alert = r16(REG_ALERT);

    if (alert & ALRT_CC_STATUS) {              // з'явився/зник партнер, змінилась роль
        uint8_t cc = r8(REG_CC_STATUS);
        //   біти [1:0] — стан CC1, [3:2] — стан CC2;
        //   ненульове = бачу термінацію партнера на цьому виводі.
        tcpm_on_cc_change(cc);                 // далі веде машина станів (TCPM)
    }
    if (alert & ALRT_FAULT) {
        uint8_t f = r8(REG_FAULT_STATUS);
        //   сюди прилітають VConnOCFault, VbusOCFault, VbusOVFault…
        tcpm_on_fault(f);
    }
    // ... тут же дивляться POWER_STATUS і прийняте PD-повідомлення.

    w16(REG_ALERT, alert);                     // скинути опрацьовані біти (запис-1-скидає)
}
