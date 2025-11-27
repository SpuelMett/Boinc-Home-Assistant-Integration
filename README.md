# Boinc Control for Home Assistant

This Home Assistant integration let's you start and stop BOINC running on another machine on your network from Home Assistant, which means that it allows you to create automations that:
* Use exess solar to benefit science.
* Instead of using direct electric heating for a room, use the heat from your BOINC server to heat a room, and benefit science. 

If you are looking to run BOINC on your Home Assistant host, use the [BOINC add-on](https://github.com/hectorespert/boinc-addons)).

Features:
* Start BOINC service
* Hard and soft stop
* Control the usage of GPU separately (if desired)
* Sensors for *total tasks*, *running tasks* and *average progress rate*
* Control multiple BOINC servers (if you have multiple BOINC hosts on your network)

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

## Start BOINC
Sets the run mode of your remote BOINC machine to "run based on preferences".

You start BOINC by calling the service ```spuelmett_boinc.start_boinc_<hostname>```.

## Stop BOINC
Sets the run mode of your remote BOINC machine to "never". This will stop any running task immediately (wasting some energy), a.k.a a hard stop.

You stop BOINC by calling the service ```spuelmett_boinc.stop_boinc_<hostname>```.

## Soft stop BOINC
When different BOINC projects run, they will on a regular basis perform a *checkpoint*. A checkpoint is used to secure the data already computed. When the client is stopped, all compute done after a checkpoint will be lost, having to be re-computed next time BOINC resumes. The frequency of checkpoints varies by project and task. 

This integration implements a _soft stop_ by waiting until next checkpoint (a simplified description, see next chapter for details).

You soft stop BOINC by calling the service ```spuelmett_boinc.soft_stop_boinc_<hostname>```.

Once checkpoint has been reached, the run mode of of your remote BOINC machine is set to "never".

### Optimizing soft stop
Since each BOINC project and task differs in how often checkpoints are made, there can be scenarios where you'd like to optimize the soft stop. To do so, you need to understand how the soft stop works in this integration.

The when calling the soft stop, the integration will check when the last checkpoint was made:

* If the last checkpoint was made less than 120 seconds ago, then the integration will request the host to stop computations. This means that a maximum of 120 seconds of computations will be lost. The 120 seconds are the default when you setup this integration. You can change it afterwards in the options of the integration.
* If the last checkpoint was made longer than 120 minutes ago, the integration will not stop the processing (meaning the calculations continue running), and wait 60 seconds before checking again when the last checkpoint was made.

If you know the checkpoint interval of your BOINC task, changing this option may help you to stop task earlier or run them longer. For example if a task only creates checkpoint every hour you may want to stop it even 5 Minutes after the last checkpoint so it doesnt run another 55 minutes.

If you would not like to rely on the automatic check of checkpoints (every 60 seconds), but would like to control when it's done, you can do so by calling the service ```spuelmett_boinc.soft_stop_boinc_<hostname>```.

# Example configurations

## Automation
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

## Switch for turning computations on/off

It can be useful to have a simple on/off switch for turning on/off the computations.

Go to Home Assistant -> Integrations -> Add -> Ping. Set the IP of your BOINC host, and name it in the same way as you named it when setting up this integration.

Add the following to ```configuration.yaml```

```yaml
switch:
  - platform: template
    switches:
      boinc:
        friendly_name: "Boinc start/soft stop"
        unique_id: "boinc"
        value_template: "{{is_state('binary_sensor.<hostname>', 'on') and has_value('sensor.spuelmett_boinc_<hostname>_running_task') and (states('sensor.spuelmett_boinc_<hostname>_running_task')|float)>0 }}"
        availability_template: "{{is_state('binary_sensor.<hostname>', 'on') and has_value('sensor.spuelmett_boinc_<hostname>_running_task')}}"
        turn_on:
          service: spuelmett_boinc.start_boinc_<hostname>
        turn_off:
          service: spuelmett_boinc.soft_stop_boinc_<hostname>
```

Please note that with a soft stop, there is a significant lag between turning the switch off, and it actually getting the state "off".

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
* Document the GPU services
* Add HACS support
