def renumber(records):
    """Прохід 3: номер — це позиція в остаточному масиві, рахуючи від нуля."""
    for i, rec in enumerate(records):
        rec.seq     = i
        rec.current = 1 if i == 0 else 0


def retarget_jumps(records):
    """Прохід 4: ім'я doJumpId → теперішній номер. Тільки після перенумерації."""
    seq_by_name = {}
    for rec in records:
        if rec.do_jump_id < 0:
            continue
        if rec.do_jump_id in seq_by_name:
            raise PlanError(
                f"ім'я doJumpId {rec.do_jump_id} трапляється двічі — "
                "стрибок став би двозначним")
        seq_by_name[rec.do_jump_id] = rec.seq

    for rec in records:
        if rec.command != MAV_CMD_DO_JUMP:
            continue
        if math.isnan(rec.params[0]):
            raise PlanError("DO_JUMP без цілі: у param1 лежить NaN")

        name = int(rec.params[0])
        if name not in seq_by_name:
            raise PlanError(f"DO_JUMP посилається на ім'я {name}, якого в плані немає")
        rec.params[0] = float(seq_by_name[name])
