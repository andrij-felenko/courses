#include <stdio.h>
#include <assert.h>

static uint8_t sim_flash[2048 * 1024];

static bool sim_read(uint32_t addr, uint8_t *dst, uint32_t len) {
    if (addr + len > sizeof(sim_flash)) return false;
    memcpy(dst, &sim_flash[addr], len);
    return true;
}

static bool sim_write(uint32_t addr, const uint8_t *src, uint32_t len) {
    if (addr + len > sizeof(sim_flash)) return false;
    for (uint32_t i = 0; i < len; ++i) {
        sim_flash[addr + i] &= src[i];
    }
    return true;
}

static bool sim_erase_sector(uint32_t sector_addr) {
    if (sector_addr + ML_FLASH_SECTOR_SIZE > sizeof(sim_flash)) return false;
    memset(&sim_flash[sector_addr], 0xFF, ML_FLASH_SECTOR_SIZE);
    return true;
}

static const ml_flash_driver_t sim_driver = {
    .read = sim_read,
    .write = sim_write,
    .erase_sector = sim_erase_sector
};

static bool test_model_eval(const uint8_t *data, uint32_t size) {
    (void)data;
    if (size == 12345) return false; /* Симуляція збою інференсу */
    return true;
}

int main(void) {
    memset(sim_flash, 0xFF, sizeof(sim_flash));

    ml_ota_context_t ota;
    ml_ota_status_t st = ml_ota_init(&ota, &sim_driver,
                                     0x000D0000, 0x000D8000, 0x00158000,
                                     64 * 1024);
    assert(st == ML_OTA_OK);
    assert(ota.meta.active_slot == ML_SLOT_A);

    ml_model_header_t bad_hdr;
    memset(&bad_hdr, 0, sizeof(bad_hdr));
    bad_hdr.magic = ML_MODEL_MAGIC;
    bad_hdr.header_version = ML_HEADER_VERSION;
    bad_hdr.payload_size = 12345;
    bad_hdr.required_arena_size = 32 * 1024;

    st = ml_ota_process_chunk(&ota, 0, (const uint8_t*)&bad_hdr, sizeof(bad_hdr));
    assert(st == ML_OTA_OK);

    uint8_t dummy_chunk[128];
    memset(dummy_chunk, 0xAA, sizeof(dummy_chunk));
    uint32_t written = 0;
    while (written < bad_hdr.payload_size) {
        uint32_t chunk = (bad_hdr.payload_size - written > sizeof(dummy_chunk)) ?
                         sizeof(dummy_chunk) : (bad_hdr.payload_size - written);
        st = ml_ota_process_chunk(&ota, sizeof(bad_hdr) + written, dummy_chunk, chunk);
        assert(st == ML_OTA_OK);
        written += chunk;
    }

    st = ml_ota_finalize_and_stage(&ota);
    assert(st == ML_OTA_OK);
    assert(ota.meta.active_slot == ML_SLOT_B);
    assert(ota.meta.slot_state[ML_SLOT_B] == ML_STATE_TRIAL);

    /* 3 невдалі спроби старту */
    bool ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.trial_boots_remaining == 2);

    ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.trial_boots_remaining == 1);

    ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.active_slot == ML_SLOT_A);
    assert(ota.meta.slot_state[ML_SLOT_B] == ML_STATE_FAILED);

    printf("Усі перевірки OTA-оновлення та відкату пройшли успішно!\n");
    return 0;
}
