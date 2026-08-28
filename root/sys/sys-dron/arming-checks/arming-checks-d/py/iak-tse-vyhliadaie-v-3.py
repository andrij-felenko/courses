# bit i у arming_check_mask == 1 → перевірку CHECKS[i] увімкнено.
def try_arm(arming_check_mask):
    global armed
    if not arm_command_present():            # немає свідомої команди — не арматимемо
        return False

    for i, chk in enumerate(CHECKS):
        # обов'язкову НЕ обійти бітом
        enabled = chk.mandatory or bool(arming_check_mask & (1 << i))
        if enabled:
            reason = chk.check()
            if reason is not None:
                gcs_send_text(f"PreArm: {reason}")   # сказати ЧОМУ не пускає
                return False                         # перша ж причина — і стоп
    armed = True                             # усі пройшли → ворота відчинено
    gcs_send_text("Armed")
    return True
