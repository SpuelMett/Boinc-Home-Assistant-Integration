import asyncio

from spuelmett_boinc.pyboinc import init_rpc_client

IP_BOINC = "192.168.178.77"
PASSWORD_BOINC = "VHV1uMEBEZW8ohWeSYTg"


async def main():
    rpc_client = await init_rpc_client(IP_BOINC, PASSWORD_BOINC)

    authorize_response = await rpc_client.authorize()

    # Get status of current and older tasks
    results = await rpc_client.get_results()
    print(results)
    print(await rpc_client.get_project_status())
    print(await rpc_client.get_cc_status())

    # Get last three messages
    c = await rpc_client.get_message_count()
    print(c)
    print(await rpc_client.get_messages(c-3))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
