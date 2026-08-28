function uploadClip(sys: ReturnType<typeof makeSystem>, clipId: string, crash: boolean): void {
  try {
    withTransaction(sys.db, (tx) => {
      tx.insert("clips", { id: clipId, state: "raw" });                       // бізнес-запис
      sys.enqueue({ cls: "transcode", key: `transcode:${clipId}`,
                    payload: { clipId } }, tx);                               // задача В ТУ САМУ tx
      if (crash) throw new Error("збій перекодувального пайплайна до commit");
    });
  } catch { /* транзакція вже відкотилась у withTransaction */ }
}

const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;

uploadClip(sys, "clip-A", true);                                             // впало по дорозі
console.log("після ВІДКАТУ →  clips:", count("clips"), " jobs:", count("jobs"));
uploadClip(sys, "clip-B", false);                                           // дійшло до кінця
console.log("після COMMIT  →  clips:", count("clips"), " jobs:", count("jobs"));
