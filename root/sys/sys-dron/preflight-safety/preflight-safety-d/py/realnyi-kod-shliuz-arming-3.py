_armed = False

# Спроба озброїтися. Обидві застави мусять пропустити.
def try_arm(operator_requested: bool) -> bool:
    global _armed
    # Застава 2: чи цього СВІДОМО хтось захотів (стік/кнопка/вимикач)?
    if not operator_requested:       return False
    if not safety_switch_pressed():  return False   # апаратний запобіжник

    # Застава 1: чи система ПРИДАТНА (усі передпольотні перевірки)?
    why = prearm_first_failure()
    if why is not None:
        # Відмова — не попередження: лишаємось обеззброєними, причина названа.
        return False                 # _armed НЕ змінюємо

    _armed = True                    # єдине місце, де апарат стає озброєним
    motors_enable()                  # тільки тепер двигуни можуть крутитися
    gcs_send_text("Armed")
    return True

def is_armed() -> bool:
    return _armed
