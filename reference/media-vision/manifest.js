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
        { slug: "pipeline-model", title: "Конвеєр: елементи, зв'язки й потік даних", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pads-and-linking", title: "Пади і з'єднання елементів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "caps-negotiation", title: "Узгодження caps: як елементи домовляються про формат", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "states-lifecycle", title: "Стани конвеєра й переходи між ними", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "buffers-and-memory", title: "Буфери й пам'ять: передача кадру без копіювання", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "clock-and-sync", title: "Годинник, мітки часу й синхронізація потоків", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "latency-and-buffering", title: "Затримка й буферизація в конвеєрі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "bus-and-messages", title: "Шина повідомлень: події й помилки конвеєра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "appsink-appsrc", title: "appsink і appsrc: міст між конвеєром і власним кодом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "network-sources", title: "Мережеві джерела: RTSP, UDP і депейлоадинг RTP", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "hardware-decode-elements", title: "Апаратне декодування: VA-API, NVDEC, V4L2, MediaCodec", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "plugin-model", title: "Модель плагінів і реєстр елементів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pipeline-debugging", title: "Діагностика конвеєра: графи, рівні журналу, типові затики", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "opencv", title: "OpenCV як бібліотека", scope: "Вузько: володіння даними, пам'ять і стик із відеоконвеєром. Алгоритми зору — у book/algorithms.",
      topics: [
        { slug: "opencv-structure", title: "Будова OpenCV: модулі, версії, як її збирають", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mat-memory-model", title: "cv::Mat: пам'ять, лічильник посилань і володіння", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mat-views-no-copy", title: "Види без копії: ROI і заголовок над чужим буфером", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "frame-interop", title: "Стик із відеоконвеєром: формати пікселів і передача кадру", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "opencv-backends", title: "Бекенди й прискорення: UMat, OpenCL, апаратна збірка", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
