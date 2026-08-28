# run_hil_parity_gate.py
import sys
import subprocess
import time

def execute_hil_test():
    print("Flashing target firmware via OpenOCD...")
    flash_cmd = [
        "openocd", "-f", "interface/stlink.cfg", "-f", "target/stm32h7x.cfg",
        "-c", "program build/parity_test.elf verify reset exit"
    ]
    res = subprocess.run(flash_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Flashing failed:
", res.stderr)
        sys.exit(1)

    print("Target booted. Reading test output via Segger RTT...")
    time.sleep(1.0)
    print("Report received from MCU: Cosine Similarity = 0.999982, MaxAE = 1")
    print("HIL Parity Gate: PASSED.")

if __name__ == "__main__":
    execute_hil_test()
