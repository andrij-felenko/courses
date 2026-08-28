def upload_clip(sys, clip_id: str, crash: bool) -> None:
    try:
        with transaction(sys.db) as tx:
            tx.insert("clips", {"id": clip_id, "state": "raw"})                 # бізнес-запис
            sys.enqueue(Job("transcode", {"clip_id": clip_id},
                            f"transcode:{clip_id}"), tx)                        # задача В ТУ САМУ tx
            if crash:
                raise RuntimeError("збій перекодувального пайплайна до commit")
    except RuntimeError:
        pass  # транзакція вже відкотилась у контекст-менеджері


sys = make_system()
count = lambda t: len(sys.db.table(t))

upload_clip(sys, "clip-A", True)                                             # впало по дорозі
print("після ВІДКАТУ →  clips:", count("clips"), " jobs:", count("jobs"))
upload_clip(sys, "clip-B", False)                                           # дійшло до кінця
print("після COMMIT  →  clips:", count("clips"), " jobs:", count("jobs"))
