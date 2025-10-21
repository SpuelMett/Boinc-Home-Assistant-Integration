# Boinc Control for Home Assistant

This Home Assistant integration let's you start and stop BOINC from Home Assistant, which means that it allows you to create automations that:
* Use exess solar to benefit science.
* Instead of using direct electric heating for a room, use the heat from your BOINC server to heat a room, and benefit science. 

You can have BOINC running on a separate machine on your network (in contrast to for example add-ons like "Folding@Home" that runs on your Home Assistant host).

Features:
* Start BOINC service
* Hard and soft stop
* Control the usage of GPU separately (if desired)
* Sensors for *total tasks*, *running tasks* and *average progress rate*
* Control multiple BOINC servers (if you have multiple BOINC hosts)

# Installation

1. Configure Boinc to allow remote control. This typically includes editing ```remote_hosts.cfg``` and ```gui_rpc_auth.cfg``` and restarting BOINC.
1. Copy the ```/spuelmett_boinc``` folder from this project into your Home Assistant's folder ```config/custom_components```.
2. Restart Home Assistant
3. Add integration "Boinc Control"
4. Enter a name, the IP-adress (no port) and the password you have set in ```gui_rpc_auth.cfg```
1. If the connection was successful you'll get a message about it. If it was unsuccessful, then do some network troubleshooting 
2. Verify that the integration works. Go to Developer Tools -> Actions -> search for "boinc". Start and stop Boinc to see that BOINC is responding as expected.
1. Create your automations of choice using the new BOINC control services available in your Home Assistant.

# Understanding the BOINC control services

## Start boinc
Sets the run mode of BOINC to "run based on preferences".

## Stop boinc
Set the run mode to "never". This will stop any running task immediately (wasting some energy), a.k.a a hard stop.

## Soft stop boinc
Lets all tasks run until they reach a checkpoint to avoid wasting energy when stopping.
If all running tasks are already suspended, it sets the run mode to "never". 

Pausing of task after a soft stop is checked every minute. You can specify the seconds after a checkpoint where task will be suspended in soft stop.
For example, if this is set to 120 and a pause check is done:
```
A task that made a checkpoint 119 seconds ago will be paused immediately.
A task that made a checkpoint 121 seconds ago will not be paused.
```
Because the stop check is made every 60 seconds this value needs to be greater than 60

### soft stop check
Lets you manually check for the soft stop. This will be done automatically every minute.

# Example automation
An example automation that starts BOINC if the energy consumption from grid is under -10 watts for 5 minutes. 
```yaml
- id: '1111111111111'
  alias: Start Boinc
  description: ''
  trigger:
  - platform: numeric_state
    entity_id: sensor.energymetermqtt_sml_curr_w
    for:
      hours: 0
      minutes: 5
      seconds: 0
    below: -10
  condition: []
  action:
  - service: spuelmett_boinc.start_boinc_name
    data: {}
  mode: single
```

# Troubleshooting connectivity

* Double check ```remote_hosts.cfg``` and ```gui_rpc_auth.cfg```
* Can you connect from the HA host to the BOINC machine?
* Is there a firewall on the BOINC server blocking you?
* If you use Docker - have you allowed port 31416?

# Credit
This project uses [pyboinc](https://github.com/nielstron/pyboinc/tree/dev/pyboinc) from Nielstron.

# Changelog

## 0.0.7
* Added start and stop actions for GPU
* Improved Soft Stop feature to Stop all non-running task immediately to avoid starting them for a few seconds
* Minor bug fixes
* Tested with Home Assistant 2025.6.0

## 0.0.6
* Added basic sensor information about "total tasks", "running tasks" and "average progress rate"

## 0.0.5
* Add Input validation for Integration Name to prevent error due to service naming.
* You may need to delete and read your integration in case you used special characters

## 0.0.4
* Update deprecated stuff for Home Assistant 2025.6.0

# Roadmap
* Add more sensors (Let me know what you want and i could try to implement it)
* Add Availability sensor to check if boinc is running and the remote access works
