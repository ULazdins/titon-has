# Titon Aura-T for Home Assistant

Home Assistant integration for [Titon Aura-T](https://www.titon.com/) heat
recovery ventilation units.

The unit has no local API. It holds an outbound connection to Titon's relay at
`app.manageiaq.com:6275`, and is addressed there by its MAC address. This
integration talks that protocol via the [`titon`](https://pypi.org/project/titon/)
library.

> Reverse engineered from the vendor app. Unofficial, unaffiliated with Titon,
> and liable to break if they change the protocol.

## Entities

| Platform | Entity | Notes |
| --- | --- | --- |
| `select` | Fan speed | Speed 0–4 |
| `number` | Kitchen timer | Boost timer, in minutes |
| `number` | Humidity threshold | Percent |
| `binary_sensor` | Filter change | Polled every 10s |
| `binary_sensor` | Summer boost | Polled every 10s |
| `binary_sensor` | Frost protection | Polled every 10s |

## Install via HACS

1. HACS → ⋮ → **Custom repositories**
2. Add `https://github.com/ULazdins/titon-has`, category **Integration**
3. Install **Titon Aura-T**, then restart Home Assistant
4. **Settings → Devices & services → Add integration → Titon Aura-T**
5. Enter your unit's MAC address, formatted `AA-BB-CC-11-22-33`

## Manual install

Copy `custom_components/titon_integration/` into your Home Assistant
`config/custom_components/` directory and restart. Home Assistant installs the
`titon` dependency from PyPI automatically on first setup.

## Configuration

The MAC address is the only setting. It can be changed later via the
integration's **Configure** option without re-adding the integration.

> Your unit's MAC is effectively its credential on Titon's relay — the protocol
> carries no other authentication. Don't publish it.

## Known issues

- Polling is driven by a bare `asyncio` task created in `binary_sensor.py`
  rather than a Home Assistant `DataUpdateCoordinator`.
- All entities register under a single hardcoded device identifier, so two
  units in one Home Assistant instance would collide.
- The binary sensors read status flags off `TitonGeneralInfo` rather than the
  dedicated `TitonFilter` and `TitonSummer` classes the library now provides.

## License

MIT
