/* reference/media-vision/manifest.js — ДОВІДНИК «Медіа й зір: GStreamer і OpenCV» (тип "reference").
   Довідник — 4-й вид книги (AUTHORING §1): рукотворні бібліотеки з версіями, API й поведінкою.

   МЕЖА (§1). Теорія кодування (JPEG, міжкадрове, ентропійне) і алгоритми зору (згортки,
   детектори, трекінг, ArUco) уже живуть у book/algorithms — там їх 89 тем, і ми їх НЕ дублюємо.
   Транспорт (RTP/RTCP, RTSP/SDP) — у book/communications/protocols як протоколи.
   Сюди йде ЛИШЕ «бібліотека як система»: конвеєр GStreamer та модель пам'яті OpenCV.
   Тому розділ `opencv` навмисно ВУЗЬКИЙ — про володіння даними й стик із конвеєром,
   а не про алгоритми обробки зображень.

   18 тем у 2 розділах. Усі заведено як detailed:pending (basic — за потреби, §3). */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "reference", slug: "media-vision", title: "Медіа й зір: GStreamer і OpenCV",
  sections: [
    { slug: "gstreamer", title: "GStreamer", scope: "Конвеєр як модель обробки медіа: з чого складається, як домовляється про формат і де виникає затримка.",
      topics: [
        { slug: "pipeline-model", title: "Конвеєр: елементи, зв'язки й потік даних", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-gstreamer-birth.md", status: "done" }] , proj: [{ file: "proj-first-pipeline.md", status: "done" }] , api: [{ file: "api-gst-launch-syntax.md", status: "done" }] },
        { slug: "pads-and-linking", title: "Пади і з'єднання елементів", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-dynamic-linking.md", status: "done" }] , api: [{ file: "api-pads.md", status: "done" }] },
        { slug: "caps-negotiation", title: "Узгодження caps: як елементи домовляються про формат", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-caps-syntax.md", status: "done" }] , proj: [{ file: "proj-transform-caps.md", status: "done" }] , hist: [{ file: "hist-negotiation-1-0.md", status: "done" }] },
        { slug: "states-lifecycle", title: "Стани конвеєра й переходи між ними", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-state-api.md", status: "done" }] , proj: [{ file: "proj-state-driver.md", status: "done" }] },
        { slug: "buffers-and-memory", title: "Буфери й пам'ять: передача кадру без копіювання", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-memory-model-rewrite.md", status: "done" }] , proj: [{ file: "proj-zero-copy-map.md", status: "done" }] , api: [{ file: "api-buffer-memory.md", status: "done" }] },
        { slug: "clock-and-sync", title: "Годинник, мітки часу й синхронізація потоків", basic: { status: "empty" }, detailed: { status: "done" } , math: [{ file: "math-running-time.md", status: "done" }] , proj: [{ file: "proj-net-clock-sync.md", status: "done" }] , api: [{ file: "api-clock-and-time.md", status: "done" }] },
        { slug: "latency-and-buffering", title: "Затримка й буферизація в конвеєрі", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-latency-probe.md", status: "done" }] , api: [{ file: "api-latency-controls.md", status: "done" }] },
        { slug: "bus-and-messages", title: "Шина повідомлень: події й помилки конвеєра", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-bus.md", status: "done" }] , proj: [{ file: "proj-bus-loop.md", status: "done" }] },
        { slug: "appsink-appsrc", title: "appsink і appsrc: міст між конвеєром і власним кодом", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-appsink-appsrc.md", status: "done" }] , proj: [{ file: "proj-frame-loop.md", status: "done" }] },
        { slug: "network-sources", title: "Мережеві джерела: RTSP, UDP і депейлоадинг RTP", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-fu-a-reassembly.md", status: "done" }] , math: [{ file: "math-jitter-latency.md", status: "done" }] , api: [{ file: "api-network-source-elements.md", status: "done" }] },
        { slug: "hardware-decode-elements", title: "Апаратне декодування: VA-API, NVDEC, V4L2, MediaCodec", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-acceleration-apis.md", status: "done" }] , api: [{ file: "api-v4l2-m2m.md", status: "done" }] , proj: [{ file: "proj-verify-zero-copy.md", status: "done" }] },
        { slug: "plugin-model", title: "Модель плагінів і реєстр елементів", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-plugin-model.md", status: "done" }] , api: [{ file: "api-registry.md", status: "done" }] , proj: [{ file: "proj-own-element.md", status: "done" }] },
        { slug: "pipeline-debugging", title: "Діагностика конвеєра: графи, рівні журналу, типові затики", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-gst-debug.md", status: "done" }] , proj: [{ file: "proj-bus-watch-diagnostics.md", status: "done" }] },
        { slug: "gobject-basics", title: "GObject: об'єктна система, на якій стоїть GStreamer", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "threads-and-queues", title: "Потоки виконання й черги: де конвеєр міняє потік", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "events-and-queries", title: "Події й запити на падах: сигналізація вздовж конвеєра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "autoplug-decodebin", title: "Автодобір елементів: decodebin і вибір за caps", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "seeking-and-flush", title: "Перемотування і скидання конвеєра: seek-події та флаш", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pipeline-events", title: "Події конвеєра: seek, flush, segment і EOS у потоці даних", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "streaming-threads", title: "Потоки передавання: хто рухає дані конвеєром", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "opencv", title: "OpenCV як бібліотека", scope: "Вузько: володіння даними, пам'ять і стик із відеоконвеєром. Алгоритми зору — у book/algorithms.",
      topics: [
        { slug: "opencv-structure", title: "Будова OpenCV: модулі, версії, як її збирають", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-opencv-origin.md", status: "done" }] , api: [{ file: "api-build-options.md", status: "done" }] , proj: [{ file: "proj-inspect-build.md", status: "done" }] },
        { slug: "mat-memory-model", title: "cv::Mat: пам'ять, лічильник посилань і володіння", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-mat-vs-iplimage.md", status: "done" }] , proj: [{ file: "proj-gst-frame-to-mat.md", status: "done" }] , api: [{ file: "api-mat-ownership.md", status: "done" }] },
        { slug: "mat-views-no-copy", title: "Види без копії: ROI і заголовок над чужим буфером", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-gst-mat-zero-copy.md", status: "done" }] , api: [{ file: "api-mat-views.md", status: "done" }] , hist: [{ file: "hist-iplimage-roi.md", status: "done" }] },
        { slug: "frame-interop", title: "Стик із відеоконвеєром: формати пікселів і передача кадру", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-bgr-order.md", status: "done" }] , api: [{ file: "api-frame-map.md", status: "done" }] , proj: [{ file: "proj-zero-copy-bridge.md", status: "done" }] },
        { slug: "opencv-backends", title: "Бекенди й прискорення: UMat, OpenCL, апаратна збірка", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-tapi-birth.md", status: "done" }] , proj: [{ file: "proj-umat-boundaries.md", status: "done" }] , api: [{ file: "api-tapi-controls.md", status: "done" }] },
        { slug: "input-output-array", title: "InputArray і OutputArray: спільний вхід для Mat, UMat і вектора", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
