import math
from dataclasses import dataclass
from typing import List

@dataclass
class AnchorEvent:
    name: str
    t_boot_us: int
    t_gcs_ms: int

@dataclass
class AlignmentModel:
    alpha_drift: float
    beta_offset_ms: float
    residual_rms_ms: float

class LogFusionEngine:
    @staticmethod
    def calculate_time_warp(anchors: List[AnchorEvent]) -> AlignmentModel:
        p = len(anchors)
        if p < 2:
            return AlignmentModel(1.0, 0.0, 0.0)

        tb_list = [a.t_boot_us / 1000.0 for a in anchors]
        tg_list = [float(a.t_gcs_ms) for a in anchors]

        mean_tb = sum(tb_list) / p
        mean_tg = sum(tg_list) / p

        cov = sum((tb - mean_tb) * (tg - mean_tg) for tb, tg in zip(tb_list, tg_list))
        var_tb = sum((tb - mean_tb) ** 2 for tb in tb_list)

        alpha = (cov / var_tb) if var_tb > 1e-9 else 1.0
        beta = mean_tg - alpha * mean_tb

        sum_sq = sum((tg - (alpha * tb + beta)) ** 2 for tb, tg in zip(tb_list, tg_list))
        return AlignmentModel(alpha, beta, math.sqrt(sum_sq / p))
