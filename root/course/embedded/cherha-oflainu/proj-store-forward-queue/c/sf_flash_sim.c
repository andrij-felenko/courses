#include "sf_flash_sim.h"

#include <string.h>

static sf_flash_err_t sim_read(void *ctx, uint32_t addr, void *dst, uint32_t len)
{
    sf_flash_sim_t *sim = (sf_flash_sim_t *)ctx;

    if (addr + len > sim->capacity) {
        return SF_FLASH_EPARAM;
    }
    if (!sim->powered) {
        return SF_FLASH_EIO;
    }
    memcpy(dst, sim->mem + addr, len);
    return SF_FLASH_OK;
}

static sf_flash_err_t sim_program(void *ctx, uint32_t addr, const void *src, uint32_t len)
{
    sf_flash_sim_t *sim = (sf_flash_sim_t *)ctx;
    const uint8_t *p = (const uint8_t *)src;

    if (addr + len > sim->capacity) {
        return SF_FLASH_EPARAM;
    }
    if (!sim->powered) {
        return SF_FLASH_EIO;
    }

    sim->program_count++;

    for (uint32_t i = 0; i < len; i++) {
        if (sim->write_budget == 0u) {
            /* Напруга просіла посеред сторінки. Байти, які вже пішли
             * в кристал, там і лишились — саме ця половинка кадру потім
             * не зійдеться за CRC. */
            sim->powered = false;
            return SF_FLASH_EIO;
        }
        if (sim->write_budget != SF_SIM_UNLIMITED) {
            sim->write_budget--;
        }
        /* Програмування вміє лише гасити біти. */
        sim->mem[addr + i] &= p[i];
    }
    return SF_FLASH_OK;
}

static sf_flash_err_t sim_erase_sector(void *ctx, uint32_t addr)
{
    sf_flash_sim_t *sim = (sf_flash_sim_t *)ctx;

    if (addr % sim->sector_size != 0u || addr + sim->sector_size > sim->capacity) {
        return SF_FLASH_EPARAM;
    }
    if (!sim->powered) {
        return SF_FLASH_EIO;
    }

    memset(sim->mem + addr, 0xFF, sim->sector_size);
    sim->erase_count++;
    return SF_FLASH_OK;
}

void sf_flash_sim_init(sf_flash_sim_t *sim, uint8_t *storage, uint32_t capacity,
                       uint32_t sector_size, uint32_t page_size, sf_flash_dev_t *dev)
{
    sim->mem = storage;
    sim->capacity = capacity;
    sim->sector_size = sector_size;
    sim->page_size = page_size;
    sim->write_budget = SF_SIM_UNLIMITED;
    sim->powered = true;
    sim->erase_count = 0;
    sim->program_count = 0;

    dev->read = sim_read;
    dev->program = sim_program;
    dev->erase_sector = sim_erase_sector;
    dev->ctx = sim;
    dev->sector_size = sector_size;
    dev->page_size = page_size;
    dev->capacity = capacity;
}

void sf_flash_sim_bulk_erase(sf_flash_sim_t *sim)
{
    memset(sim->mem, 0xFF, sim->capacity);
    sim->erase_count++;
}

void sf_flash_sim_cut_power_after(sf_flash_sim_t *sim, uint32_t n)
{
    sim->write_budget = n;
}

void sf_flash_sim_power_up(sf_flash_sim_t *sim)
{
    sim->powered = true;
    sim->write_budget = SF_SIM_UNLIMITED;
}
