# AZRouter API — Sample Data & Discovery

Router: `http://192.168.21.98/` · user: `admin`  
Captured via live API calls on 2026-04-10.

---

## Authentication

```
POST /api/v1/login
Body: {"data":{"username":"admin","password":"azrouteradmin"}}
Response: <token string>
Subsequent requests: Cookie: token=<token>
```

---

## `GET /api/v1/cloud/status`

```json
{
  "status": "online",
  "url": "https://new.azrouter.cloud/e831cd308360"
}
```

| Field | Type | Meaning |
|---|---|---|
| `status` | string | Cloud reachability: `"online"` / `"offline"` |
| `url` | string | Cloud dashboard URL (suffix = MAC address) |

---

## `GET /api/v1/status`

```json
{
  "system": {
    "status": 0,
    "hdo": 1,
    "mode": 0,
    "temperature": 34,
    "time": 1775865823,
    "masterBoost": 0,
    "uptime": 1740798364,
    "hw": 202,
    "sn": "N/A",
    "mac": "e831cd308360",
    "fw": "AZMaster-v2-7-49-0829.bin",
    "www": "AZWeb-v2-7-13-0763.bin"
  },
  "cloud": {
    "status": 4,
    "reachable": 1,
    "registered": 1
  },
  "activeDevice": {
    "id": 24,
    "maxPower": 7360,
    "name": "AZ Charger"
  }
}
```

### `status.system`

| Field | Type | Meaning |
|---|---|---|
| `status` | int | Router operational status: `0` = OK |
| `hdo` | int | HDO (ripple control) signal: `1` = active, `0` = inactive |
| `mode` | int | Operating mode: `0` = normal |
| `temperature` | int | Router board temperature in °C |
| `time` | int | Current Unix timestamp on the router |
| `masterBoost` | int | Master boost enabled: `1` = on, `0` = off |
| `uptime` | int | System uptime in **milliseconds** |
| `hw` | int | Hardware revision (e.g. `202`) |
| `sn` | string | Serial number (`"N/A"` if not set) |
| `mac` | string | Router MAC address (unique identifier) |
| `fw` | string | Firmware version string |
| `www` | string | Web UI firmware version string |

### `status.cloud`

| Field | Type | Meaning |
|---|---|---|
| `status` | int | Cloud connection state: `4` = fully connected |
| `reachable` | int | Cloud server reachable: `1` = yes, `0` = no |
| `registered` | int | Router registered with cloud: `1` = yes, `0` = no |

### `status.activeDevice`

| Field | Type | Meaning |
|---|---|---|
| `id` | int | ID of the currently active device |
| `maxPower` | int | Maximum power of the active device in W |
| `name` | string | Name of the active device |

---

## `GET /api/v1/power`

```json
{
  "output": {
    "power": [
      {"id": 0, "value": 345},
      {"id": 1, "value": 230},
      {"id": 2, "value": 345},
      {"id": 3, "value": 920}
    ],
    "energy": [
      {"id": 0, "value": 4068},
      {"id": 1, "value": 2484},
      {"id": 2, "value": 222},
      {"id": 3, "value": 119},
      {"id": 4, "value": 0}
    ]
  },
  "input": {
    "power": [
      {"id": 0, "value": -16},
      {"id": 1, "value": 100},
      {"id": 2, "value": -40},
      {"id": 3, "value": 0}
    ],
    "voltage": [
      {"id": 0, "value": 242820},
      {"id": 1, "value": 242640},
      {"id": 2, "value": 243430},
      {"id": 3, "value": 0}
    ],
    "current": [
      {"id": 0, "value": -931},
      {"id": 1, "value": 829},
      {"id": 2, "value": -912},
      {"id": 3, "value": 0}
    ],
    "status": [
      {"id": 0, "value": 0},
      {"id": 1, "value": 0},
      {"id": 2, "value": 0},
      {"id": 3, "value": 0}
    ]
  },
  "lastUpdate": 1775865817
}
```

### `power.input` — grid/meter (ids 0–2 = L1–L3, id 3 = unused)

| Field | Unit | Notes |
|---|---|---|
| `power[n].value` | W | Positive = import from grid, negative = export |
| `voltage[n].value` | mV | ÷1000 → V (e.g. `242820` → 242.82 V) |
| `current[n].value` | mA | ÷1000 → A; negative = export direction |
| `status[n].value` | int | Meter status per phase: `0` = OK |

### `power.output` — per-output channel

| Field | Unit | Notes |
|---|---|---|
| `power[0-2].value` | W | Per-phase output power (L1, L2, L3) |
| `power[3].value` | W | Total output power (verified: 345+230+345 = 920 ✓) |
| `energy[0-3].value` | Wh | Cumulative energy per output channel (increases over time) |
| `energy[4].value` | Wh | Likely reset/session energy (can be 0) |

| Field | Meaning |
|---|---|
| `lastUpdate` | Unix timestamp of last meter reading |

---

## `GET /api/v1/devices`

```json
[
  {
    "deviceType": "4",
    "common": {
      "priority": 1,
      "id": 24,
      "name": "AZ Charger",
      "status": 4,
      "signal": -49,
      "type": 4,
      "sn": "N/A",
      "fw": "002.001.000.0306",
      "hw": 200
    },
    "charge": {
      "status": 1,
      "state": 0,
      "current": [1500, 1000, 1500],
      "temperature": 0,
      "boost": 0,
      "boostSource": 0,
      "circuitBreaker": 32,
      "triggerPhase": 0,
      "totalPower": 971
    }
  }
]
```

### `devices[n].common`

| Field | Type | Meaning |
|---|---|---|
| `priority` | int | Scheduling priority among chargers |
| `id` | int | Unique device ID (used in write API calls) |
| `name` | string | Human-readable charger name |
| `status` | int | Connection status: `4` = online/connected, others = offline |
| `signal` | int | WiFi RSSI in dBm |
| `type` | int | Device type: `4` = AZ Charger |
| `sn` | string | Serial number |
| `fw` | string | Charger firmware version |
| `hw` | int | Hardware revision |

### `devices[n].charge`

| Field | Type | Meaning |
|---|---|---|
| `status` | int | Charger status: `1` = standby/ready, `2` = actively charging |
| `state` | int | Fault/state code: `0` = normal |
| `current` | int[3] | Per-phase charging current in mA: `[L1, L2, L3]` |
| `temperature` | int | Charger board temperature in °C |
| `boost` | int | Boost active: `1` = on, `0` = off |
| `boostSource` | int | Boost trigger source: `0` = none |
| `circuitBreaker` | int | Physical circuit breaker limit in A (static config: 32 A) |
| `triggerPhase` | int | Phase that triggered the charge decision: `0` = none/all |
| `totalPower` | int | Total charging power across all phases in W |

---

## `GET /api/v1/settings`

```json
{
  "version": "AZSettings-v2-1-0-0",
  "wifi": {
    "mode": 1,
    "ssid": "Swamp"
  },
  "system": {
    "language": 0,
    "measurement_source": 0,
    "server_part": 0,
    "update_hour": 1
  },
  "regulation": {
    "gain": 1,
    "period": 1000,
    "max_current": 32,
    "target_power_w": 150,
    "power_offset_w": 0
  },
  "cloud": {
    "url": "aztraders.germanywestcentral.cloudapp.azure.com",
    "update_url": "ota.aztraders.cz",
    "account_url": "azrouter.cloud",
    "port": 8080,
    "update_port": 80,
    "sampling_period": 10000,
    "send_samples": 20
  }
}
```

### `settings.regulation` — key tunable parameters

| Field | Type | Meaning |
|---|---|---|
| `max_current` | int | Maximum allowed current in A (mirrors `circuitBreaker`) |
| `target_power_w` | int | Target grid import power in W (regulation setpoint, e.g. 150W) |
| `power_offset_w` | int | Power measurement offset correction in W |
| `gain` | int | Regulation gain factor |
| `period` | int | Regulation loop period in ms (1000 = 1 s) |

### `settings.system`

| Field | Type | Meaning |
|---|---|---|
| `language` | int | UI language: `0` = default |
| `measurement_source` | int | Which meter is used as input source |
| `update_hour` | int | Hour of day for firmware OTA update check |

---

## Write API (POST endpoints)

| Endpoint | Body example | Effect |
|---|---|---|
| `POST /api/v1/login` | `{"data":{"username":"…","password":"…"}}` | Returns auth token |
| `POST /api/v1/system/boost` | `{"data":{"boost":1}}` | Enable/disable master boost |
| `POST /api/v1/device/boost` | `{"data":{"boost":1,"device":{"common":{"id":24}}}}` | Enable/disable charger boost |

`PUT/PATCH /api/v1/settings` → 405. Settings appear read-only via REST (configured via web UI only).

---

## Possible future sensors / number entities

| Entity type | Field | Path |
|---|---|---|
| `sensor` | Output Energy L1–L4 | `power.output.energy.{0-3}.value` (Wh, total_increasing) |
| `number` | Target Power | `settings.regulation.target_power_w` (W, if write API found) |
| `number` | Power Offset | `settings.regulation.power_offset_w` (W) |
