import math

class RfUnitConverter:
    THERMAL_NOISE_FLOOR_DBM_HZ = -173.98
    DIPOLE_OFFSET_DBI = 2.15

    @staticmethod
    def dbm_to_mw(dbm: float) -> float:
        return 10.0 ** (dbm / 10.0)

    @staticmethod
    def mw_to_dbm(mw: float) -> float:
        if mw <= 0:
            raise ValueError("Потужність повинна бути більшою за нуль.")
        return 10.0 * math.log10(mw)

    @staticmethod
    def dbm_to_dbw(dbm: float) -> float:
        return dbm - 30.0

    @staticmethod
    def dbmuv_to_dbm(dbmuv: float, impedance: int = 50) -> float:
        k = 108.75 if impedance == 75 else 106.99
        return dbmuv - k

    @staticmethod
    def dbm_to_dbmuv(dbm: float, impedance: int = 50) -> float:
        k = 108.75 if impedance == 75 else 106.99
        return dbm + k

    @staticmethod
    def dbd_to_dbi(dbd: float) -> float:
        return dbd + RfUnitConverter.DIPOLE_OFFSET_DBI

    @staticmethod
    def calculate_cn0(signal_dbm: float, bandwidth_hz: float) -> float:
        if bandwidth_hz <= 0:
            raise ValueError("Смуга частот повинна бути більшою за нуль.")
        return signal_dbm - RfUnitConverter.THERMAL_NOISE_FLOOR_DBM_HZ


if __name__ == "__main__":
    p_dbm = 20.0
    print("=== RF Unit Converter (Python) ===")
    print(f"Потужність: {p_dbm} dBm = {RfUnitConverter.dbm_to_mw(p_dbm):.2f} мВт")
    print(f"Напруга у 50 Ом: {p_dbm} dBm = {RfUnitConverter.dbm_to_dbmuv(p_dbm, 50):.2f} dBuV")
    print(f"C/N0 при -90 dBm: {RfUnitConverter.calculate_cn0(-90.0, 20e6):.2f} dBHz")
