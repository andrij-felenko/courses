const RC_TIMEOUT_MS = 500;   // 0.5 с без валідного кадру = втрата

// викликається з основного циклу польотного контролера (~раз на такт)
function rcFailsafeTick(nowMs) {
    if (nowMs - gLastRcFrameMs > RC_TIMEOUT_MS) {
        enterFailsafe(FS_RTL);            // повернення додому (RTL)
    }
}
// приймач: щойно прийшов валідний кадр керування — оновлюємо мітку часу
function onRcFrameValid(nowMs) { gLastRcFrameMs = nowMs; }
