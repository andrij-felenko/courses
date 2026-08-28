def report(sync, overdue) -> int:
    def show(title, vs):
        print(f"\n{title}")
        if not vs:
            print("  чисто"); return
        for vid, detail in vs:
            print(f"  ✗ {vid:<7} {detail}")
    show("СИНХРОНІЗАЦІЯ КОД ↔ ЖУРНАЛ", sync)
    show("СТРОКИ (тригер проти знімка метрик)", overdue)
    n = len(sync) + len(overdue)
    print(f"\n{n} порушень → борг вийшов з-під контролю, CI падає" if n
          else "\nборг під контролем — CI зелений")
    return 1 if n else 0


# У CI:  markers = scan_markers(Path("src"));  metrics = read_snapshot()
# Тут — відтворюваний знімок того, що вони повернули б.
MARKERS = [("DH-014", "panel/energy.py:42"), ("DH-031", "export/report.py:17"),
           ("DH-022", "panel/energy.py:31"), ("DH-007", "panel/legacy.py:88")]
METRICS = {"panel_p95_ms": 930, "max_devices_per_home": 4200, "rule_types": 4}

if __name__ == "__main__":
    sys.exit(report(check_sync(MARKERS, JOURNAL), check_overdue(JOURNAL, METRICS)))
