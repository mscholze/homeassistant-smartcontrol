# homeassistant-smartcontrol
homeassistant-smartcontrol is a custom component for HomeAssistant to integrate power consumption(W) and energy consumption in total (kWh) from smartcontrol.eon.de. For more information regarding the products and requirements visit https://www.eon.de/de/pk/smarthome/control.html


To enable after installation, add this lines to your sensor configuration:

```yaml
- platform: smart_control
  username: "EMAIL-ADDRESS"
  password: "PASSWORD"
```

| WARNING: this is still under developement, the sensor.py was created with the help of ChatGPT, so it is not perfect, but works at this stage for me.
