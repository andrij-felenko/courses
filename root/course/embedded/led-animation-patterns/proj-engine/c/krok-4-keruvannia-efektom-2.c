void animPause(int idx) {
    if (idx < 0 || anims[idx].mode == ANIM_OFF) return;
    if (anims[idx].pausedAt == 0)
        anims[idx].pausedAt = millis();      // зафіксували момент заморозки
}

void animResume(int idx) {
    if (idx < 0 || anims[idx].mode == ANIM_OFF) return;
    if (anims[idx].pausedAt != 0) {
        uint32_t frozen = millis() - anims[idx].pausedAt;  // скільки простояли
        anims[idx].start += frozen;          // посунули базу — фаза не стрибне
        anims[idx].pausedAt = 0;             // знову біжить
    }
}

void animStop(int idx) {
    if (idx >= 0) anims[idx].mode = ANIM_OFF;   // звільнити слот негайно
}
