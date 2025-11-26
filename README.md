# Boinc-Home-Assistant-Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![Validate](https://github.com/SpuelMett/Boinc-Home-Assistant-Integration/workflows/Validate/badge.svg)

This project lets you start and stop Boinc from Home Assistant and lets you monitor basic information about your boinc client. 
This can be used, for example, to run Boinc only on solar energy.
It is a custom integration for home assistant that provides services that can be used in scripts or automations.
This project also uses [pyboinc](https://github.com/nielstron/pyboinc/tree/dev/pyboinc) from Nielstron.

Current version 0.0.7 is tested with Home Assistant 2025.6.0
The old version 0.0.3 is not working correctly since Home Assistant 2024.11.

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/SpuelMett/Boinc-Home-Assistant-Integration` as repository
   - Select "Integration" as category
3. Click "Install" on the Boinc Control integration
4. Restart Home Assistant
5. Go to Settings → Devices & Services → Add Integration
6. Search for "Boinc Control" and follow the configuration steps

### Manual Installation

1. Copy the `spuelmett_boinc` folder into the `custom_components` folder in your Home Assistant config directory
2. If the `custom_components` folder doesn't exist, create it
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Boinc Control" and follow the configuration steps

## Services

The provided Services are:

### start boinc
Set the run mode to "run based on preferences".

### stop boinc
Set the run mode to "never". This will stop are running task immediately.

### soft stop boinc
Lets all tasks run until they reach a checkpoint to avoid wasting energy when stopping.  
Set the run mode to "never" if all running tasks are suspended. 

Pausing of task after a soft stop is checked every minute. You can specify the seconds after a checkpoint where task will be suspended in soft stop.
For example, if this is set to 120 and a pause check is done:
```
A task that made a checkpoint 119 seconds ago will be paused immediately.
A task that made a checkpoint 121 seconds ago will not be paused.
```
Because the stop check is made every 60 seconds this value needs to be greater than 60

### soft stop check
Lets you manually check for the soft stop. This will be done automatically every minute.

## Configuration

After installing the integration (via HACS or manually), you need to configure it:

- Go to Settings → Devices & Services → Add Integration
- Search for the newly added "Boinc Control" integration
- Fill in a name, the IP address and the remote password of your boinc client. The name can be chosen freely.
- Optionally change the checkpointing time 

## Usage

The services can be used in automations and scripts. The naming of the services is `spuelmett_boinc.<service>_<name>` where service is: 
- start_boinc
- stop_boinc
- soft_stop_boinc
- soft_stop_check

and `name` is what you chose in the config. 

### Example Automation

Here is an example automation in the automations.yaml. It starts boinc if my energy consumption from grid is under -10 watts for 5 minutes. 
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

# Sensors
Entities are visible form the integration menu and can be added to the Dashboard.

# Changelog

### 0.0.7
* Added start and stop actions for GPU
* Improved Soft Stop feature to Stop all non-running task immediately to avoid starting them for a few seconds
* Minor bug fixes

### 0.0.6
* Added basic sensor information about "total tasks", "running tasks" and "average progress rate"

### 0.0.5
* Add Input validation for Integration Name to prevent error due to service naming.
* You may need to delete and read your integration in case you used special characters

### 0.0.4
* Update deprecated stuff for Home Assistant 2025.6.0


# Roadmap
* Add more sensors (Let me know what you want and i could try to implement it)
* Add Availability sensor to check if boinc is running and the remote access works
