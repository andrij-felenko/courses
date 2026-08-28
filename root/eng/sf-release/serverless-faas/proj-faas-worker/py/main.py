import asyncio
import time
import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class ExecutionResult:
    success: bool
    timed_out: bool
    exit_code: int
    response: str
    error_log: str
    duration_ms: float
    was_cold_start: bool

class AsyncSandbox:
    def __init__(self, binary_path: str, function_id: str):
        self.binary_path = binary_path
        self.function_id = function_id
        self.process: Optional[asyncio.subprocess.Process] = None
        self.is_alive = False

    async def spawn(self):
        env = os.environ.copy()
        env["AWS_LAMBDA_FUNCTION_NAME"] = self.function_id
        env["LAMBDA_TASK_ROOT"] = "/tmp"

        self.process = await asyncio.create_subprocess_exec(
            self.binary_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        self.is_alive = True

    async def invoke(self, payload: str, timeout_sec: float) -> ExecutionResult:
        if not self.is_alive or self.process is None:
            return ExecutionResult(False, False, -1, "", "Sandbox not active", 0.0, False)

        start_time = time.perf_counter()
        timed_out = False
        stdout_data, stderr_data = b"", b""
        exit_code = 0

        try:
            input_bytes = (payload + "\n").encode("utf-8")
            stdout_data, stderr_data = await asyncio.wait_for(
                self.process.communicate(input_bytes),
                timeout=timeout_sec
            )
            exit_code = self.process.returncode or 0
            self.is_alive = False  # Процес завершив роботу
        except asyncio.TimeoutError:
            timed_out = True
            await self.terminate()

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        success = (exit_code == 0) and not timed_out

        return ExecutionResult(
            success=success,
            timed_out=timed_out,
            exit_code=exit_code,
            response=stdout_data.decode("utf-8", errors="replace"),
            error_log=stderr_data.decode("utf-8", errors="replace"),
            duration_ms=duration_ms,
            was_cold_start=False
        )

    async def terminate(self):
        if self.process and self.is_alive:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.returncode is None:
                    self.process.kill()
            except ProcessLookupError:
                pass
            self.is_alive = False

class AsyncFaaSPool:
    def __init__(self, max_warm: int = 4):
        self.max_warm = max_warm
        self.pools: Dict[str, List[AsyncSandbox]] = {}

    async def dispatch(self, function_id: str, binary_path: str, payload: str, timeout_sec: float) -> ExecutionResult:
        pool = self.pools.setdefault(function_id, [])
        sandbox = None
        was_cold = False

        while pool:
            candidate = pool.pop(0)
            if candidate.is_alive:
                sandbox = candidate
                break

        if sandbox is None:
            was_cold = True
            sandbox = AsyncSandbox(binary_path, function_id)
            await sandbox.spawn()

        res = await sandbox.invoke(payload, timeout_sec)
        res.was_cold_start = was_cold
        return res
