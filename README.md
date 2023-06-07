# Boinc-Home-Assistant-Integration

This project lets you start and stop Boinc from Home Assistant. 
This can be used for example to run Boinc only on solar energy.
It is a custom integration for home assistant that provides services that can be used in scripts or automations.
It is an improved version of this [project](https://github.com/SpuelMett/Boinc-Home-Assistant-Control).
This project also uses [pyboinc](https://github.com/nielstron/pyboinc/tree/dev/pyboinc).

The provided Services are:

### start boinc
Sets the run mode to "run based on preferences".

### stop boinc
Sets the run mode to "never". This will stop are running task immediately.

### soft stop boinc
Lets all tasks run until they reach a checkpoint to avoid wasting energy when stopping.  
Sets the run mode to "never" if all running tasks are suspended. 

Pausing of task after a soft stop is checked every minute. You can specify the seconds after a checkpoint where task will be suspended in soft stop.
For example if this is set to 120 and a pause check is done:
```
A task that made a checkpoint 119 seconds ago will be paused immediately.
A task that made a checkpoint 121 seconds ago will not be paused.
```
Because the stop check is made every 60 seconds this value needs to be greater than 60

### soft stop check
Lets you manually check for the soft stop. This will be done automatically every minute.


# Usage
- Copy the spuelmett_boinc folder into the custom_components folder. This folder should be inside the config folder of home assistant. If this folder does not exist yet, create it. 
- Restart Home Assistant
- Search for the newly added "Boinc Contorl" integration
- Fill in the ip and remote password of your boinc client
- Optionally change the checkpointing time  
