// Отримання дескриптора синхронного доступу всередині Dedicated Worker
const root: FileSystemDirectoryHandle = await navigator.storage.getDirectory();
const fileHandle = await root.getFileHandle("document.wal", { create: true });
const accessHandle: FileSystemSyncAccessHandle = await fileHandle.createSyncAccessHandle();

// Синхронний запис порції даних у заданий зсув
const bytesWritten: number = accessHandle.write(buffer, { at: offset });

// Примусова синхронізація з енергонезалежним носієм (аналог fsync)
accessHandle.flush();

// Атомарна зміна розміру (обрізання журналу після чекпойнта)
accessHandle.truncate(0);

// Закриття ексклюзивного доступу
accessHandle.close();
