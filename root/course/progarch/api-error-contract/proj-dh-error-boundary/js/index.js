// клієнт (панель) розбирає конверт помилки — перелік кодів ВІДКРИТИЙ
switch (problem.code) {
  case "device_unavailable":
  case "rate_limited":
    scheduleRetry(retryAfterSeconds(res));   // повторюване — назад через Retry-After
    break;
  case "device_not_found":
    forgetDevice();
    break;
  case "invalid_command":
    highlightField(problem.field);           // сервер сказав, ЯКЕ поле
    break;
  default:                                    // ← рятує від БУДЬ-ЯКОГО нового коду
    showGenericError(problem.detail);        // detail — для ока, не для гілок
}
