    @classmethod
    def validate_acceleration_envelope(
        cls,
        spec: HarmonicDriveSpec,
        cycle: List[MotionSegment],
        motor_inertia_kgm2: float
    ) -> tuple[bool, List[str]]:
        warnings = []
        is_safe = True
        
        for idx, seg in enumerate(cycle):
            n_in = abs(seg.output_speed_rpm) * spec.ratio
            t_out = abs(seg.output_torque_nm)
            
            # Перевірка абсолютної граничної швидкості хвильового генератора
            if n_in > spec.max_input_speed:
                is_safe = False
                warnings.append(
                    f"Сегмент {idx + 1}: швидкість входу {n_in:.0f} об/хв перевищує паспортний ліміт {spec.max_input_speed} об/хв"
                )
            
            # Перевірка допустимого пікового моменту прискорення/гальмування
            if t_out > spec.limit_accel_torque:
                is_safe = False
                warnings.append(
                    f"Сегмент {idx + 1}: піковий момент {t_out:.1f} Н·м перевищує ліміт розгону {spec.limit_accel_torque} Н·м"
                )
                
            # Перевірка комбінованого фактора: при наближенні до максимальної швидкості
            # допустимий момент прискорення знижується через нагрів мастила та підшипника
            speed_ratio = n_in / spec.max_input_speed if spec.max_input_speed > 0 else 0
            if speed_ratio > 0.8:
                derated_accel_torque = spec.limit_accel_torque * (1.0 - 0.5 * (speed_ratio - 0.8) / 0.2)
                if t_out > derated_accel_torque:
                    warnings.append(
                        f"Сегмент {idx + 1}: робоча точка ({n_in:.0f} об/хв, {t_out:.1f} Н·м) перевищує термодинамічну межу {derated_accel_torque:.1f} Н·м"
                    )
        
        return is_safe, warnings
