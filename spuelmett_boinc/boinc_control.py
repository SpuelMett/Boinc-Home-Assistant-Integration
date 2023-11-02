"""Boinc Control integration logic."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .pyboinc.pyboinc import init_rpc_client
from .pyboinc.pyboinc.rpc_client import Mode

from .const import BOINC_IP, PASSWORD, CHECKPOINTING


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback
) -> bool:
    ip = config[BOINC_IP]
    password = config[PASSWORD]
    checkpoint_time = config[CHECKPOINTING]

    await add_entities([BoincControl(ip, password, checkpoint_time)])


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
        print("Update Object")
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
        if results == '\n':
            return

        for result in results:
            project_url = result["project_url"]
            name = result["name"]
            await self.rpc_client.resume_result(project_url, name)
