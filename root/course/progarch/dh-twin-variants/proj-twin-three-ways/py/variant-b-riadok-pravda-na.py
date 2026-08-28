# ВЕРСІЯ РЯДКА (оптимістично): запис проходить, лише якщо version та сама, що прочитали
def apply_cas(db, home_id, cmd):
    while True:
        row = db.get("device_state", home_id)
        changed = db.update(
            "device_state",
            where={"home_id": home_id, "version": row["version"]},   # ← умова CAS
            set={
                "bolt": "locked" if cmd["kind"] == "lock" else "unlocked",
                "version": row["version"] + 1,
                "last_cmd": f"{cmd['by']}#{cmd['seq']}",
            },
        )
        if changed == 1:            # ми виграли — рівно ми бумкнули version
            return
        # changed == 0: хтось бумкнув version між read і write → повторити
