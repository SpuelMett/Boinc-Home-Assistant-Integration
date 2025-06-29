"""Boinc Control integration logic."""

from __future__ import annotations

from datetime import timedelta

from .pyboinc.pyboinc import init_rpc_client
from .pyboinc.pyboinc.rpc_client import Mode


class BoincControl:
    def __init__(self, host: str, password: str, checkpoint_time: int) -> None:
        self.current_soft_stop_state = False
        self.host = host
        self.password = password
        self.checkpoint_time = checkpoint_time
        self.rpc_client = None

    async def connect(self):
        self.rpc_client = await init_rpc_client(self.host, self.password)
        await self.rpc_client.authorize()

    def set_checkpoint_time(self, checkpoint_time):
        self.checkpoint_time = checkpoint_time

    @property
    def soft_stop_state(self):
        return self.current_soft_stop_state

    async def start_boinc(self):
        await self.connect()
        self.current_soft_stop_state = False
        await self.resume_all_task()
        await self.rpc_client.set_run_mode(Mode.AUTO, 0)

    async def stop_boinc(self):
        await self.connect()
        await self.rpc_client.set_run_mode(Mode.NEVER, 0)

    def soft_stop_boinc(self):
        self.current_soft_stop_state = True

    async def update(self):
        await self.connect()

        # Do nothing if it should not stop
        if self.current_soft_stop_state is False:
            return

        one_task_running = False  # Default

        results = await self.rpc_client.get_results()
        for result in results:
            # check if the result is an active task
            if "active_task" in result:
                active_task = result["active_task"]
                checkpoint_cpu_time = active_task["checkpoint_cpu_time"]
                current_cpu_time = active_task["current_cpu_time"]
                project_url = result["project_url"]
                name = result["name"]

                # Check if last checkpoint was longer ago than the configured value
                if current_cpu_time - checkpoint_cpu_time < timedelta(
                    seconds=self.checkpoint_time
                ):
                    # Suspend task
                    await self.rpc_client.suspend_result(project_url, name)
                else:
                    one_task_running = True

        # if all task are suspended set run mode to suspend
        if one_task_running is False:
            await self.rpc_client.set_run_mode(Mode.NEVER, 0)

    async def resume_all_task(self):
        results = await self.rpc_client.get_results()

        # if no task are there, results is a string
        if results == "\n":
            return

        for result in results:
            project_url = result["project_url"]
            name = result["name"]
            await self.rpc_client.resume_result(project_url, name)

    async def get_results(self):
        # make sure rpc client is available
        await self.connect()

        # get results
        return await self.rpc_client.get_results()

    def get_running_task_count(self, results):
        # if no task are there, results is a string
        if results == "\n" or type(results) is not dict:
            return 0

        print(results)

        count = 0
        for result in results:
            # check if running
            if "active_task" not in result:
                continue

            # active task is 1, otherwise it is 0
            activeState = result["active_task"]["active_task_state"]
            if activeState == 1:
                count += 1

        return count

    def get_total_task_count(self, results):
        # if no task are there, results is a string
        if results == "\n":
            return 0

        return len(results)

    def average_progress_rate(self, results):
        total_active_tasks = 0
        total_progress_rate = 0

        for result in results:
            if "active_task" not in result:
                continue

            if "progress_rate" not in result["active_task"]:
                continue

            total_progress_rate += result["active_task"]["progress_rate"]
            total_active_tasks += 1

        if total_active_tasks == 0:
            return 0

        return total_progress_rate / total_active_tasks
