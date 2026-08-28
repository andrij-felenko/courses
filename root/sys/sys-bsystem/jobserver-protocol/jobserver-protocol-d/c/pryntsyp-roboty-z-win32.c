/* Win32 C API: створення та синхронізація семафора */
HANDLE create_jobserver_sem(const char *name, int max_jobs) {
    return CreateSemaphoreA(NULL, max_jobs - 1, max_jobs - 1, name);
}

HANDLE open_jobserver_sem(const char *name) {
    return OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, name);
}

int acquire_sem_token(HANDLE hSem, DWORD timeout_ms) {
    return WaitForSingleObject(hSem, timeout_ms) == WAIT_OBJECT_0;
}

void release_sem_token(HANDLE hSem) {
    ReleaseSemaphore(hSem, 1, NULL);
}
