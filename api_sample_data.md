# AZRouter API — Sample Data

Router: `http://192.168.21.98/` · user: `admin`  
Captured from `LOGGER.debug("Coordinator data: %s", data)` on 2026-04-10.

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
| `status` | string | Cloud reachability: `"online"` / (presumably `"offline"`) |
| `url` | string | Cloud dashboard URL for this specific router (suffix = MAC address) |

---

## `GET /api/v1/status`

```json
{
  "system": {
    "status": 0,
    "hdo": 1,
    "mode": 0,
    "temperature": 35,
    "time": 1775849781,
    "masterBoost": 0,
    "uptime": 1724756823,
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
| `hdo` | int | HDO (ripple control) signal state: `1` = active, `0` = inactive |
| `mode` | int | Operating mode: `0` = normal (TBD: other values) |
| `temperature` | int | Router board temperature in °C |
| `time` | int | Current Unix timestamp on the router |
| `masterBoost` | int | Master boost enabled: `1` = on, `0` = off |
| `uptime` | int | System uptime in milliseconds |
| `hw` | int | Hardware revision (e.g. `202`) |
| `sn` | string | Serial number (`"N/A"` if not set) |
| `mac` | string | Router MAC address (also used as unique identifier) |
| `fw` | string | Firmware version string |
| `www` | string | Web UI firmware version string |

### `status.cloud`

| Field | Type | Meaning |
|---|---|---|
| `status` | int | Cloud connection state: `4` = fully connected and registered |
| `reachable` | int | Cloud server reachable: `1` = yes, `0` = no |
| `registered` | int | Router registered with cloud: `1` = yes, `0` = no |

### `status.activeDevice`

| Field | Type | Meaning |
|---|---|---|
| `id` | int | ID of the currently active/controlling device |
| `maxPower` | int | Maximum power of the active device in W |
| `name` | string | Human-readable name of the active device |

---

## `GET /api/v1/power`

```json
{
  "output": {
    "power": [
      {"id": 0, "value": 460},
      {"id": 1, "value": 575},
      {"id": 2, "value": 345},
      {"id": 3, "value": 1380}
    ],
    "energy": [
      {"id": 0, "value": 4063},
      {"id": 1, "value": 2479},
      {"id": 2, "value": 217},
      {"id": 3, "value": 114},
      {"id": 4, "value": 26}
    ]
  },
  "input": {
    "power": [
      {"id": 0, "value": 22},
      {"id": 1, "value": 72},
      {"id": 2, "value": -72},
      {"id": 3, "value": 0}
    ],
    "voltage": [
      {"id": 0, "value": 240620},
      {"id": 1, "value": 240440},
      {"id": 2, "value": 240490},
      {"id": 3, "value": 0}
    ],
    "current": [
      {"id": 0, "value": 825},
      {"id": 1, "value": 1690},
      {"id": 2, "value": -848},
      {"id": 3, "value": 0}
    ],
    "status": [
      {"id": 0, "value": 0},
      {"id": 1, "value": 0},
      {"id": 2, "value": 0},
      {"id": 3, "value": 0}
    ]
  },
  "lastUpdate": 1775849737
}
```

### `power.input` — grid/meter measurements (ids 0–2 = L1–L3, id 3 = unused/total)

| Field | Unit | Notes |
|---|---|---|
| `power[n].value` | W | Positive = consuming from grid, negative = exporting to grid |
| `voltage[n].value` | mV | Divide by 1000 for V (e.g. `240620` → 240.62 V) |
| `current[n].value` | mA | Divide by 1000 for A; negative = export direction |
| `status[n].value` | int | Meter status per phase: `0` = OK |

### `power.output` — per-output channel measurements

| Field | Unit | Notes |
|---|---|---|
| `power[n].value` | W | Per-output power (id 0–2 = likely L1–L3, id 3 = total: 460+575+345 ≈ 1380 ✓) |
| `energy[n].value` | Wh (TBD) | Cumulative energy per output (5 channels, meaning TBD) |

| Field | Type | Meaning |
|---|---|---|
| `lastUpdate` | int | Unix timestamp of the last meter reading |

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
      "signal": -51,
      "type": 4,
      "sn": "N/A",
      "fw": "002.001.000.0306",
      "hw": 200
    },
    "charge": {
      "status": 2,
      "state": 0,
      "current": [2000, 2500, 1500],
      "temperature": 0,
      "boost": 0,
      "boostSource": 0,
      "circuitBreaker": 32,
      "triggerPhase": 0,
      "totalPower": 1442
    }
  }
]
```

### `devices[n].common`

| Field | Type | Meaning |
|---|---|---|
| `priority` | int | Scheduling priority among multiple chargers |
| `id` | int | Unique device ID (used in API write calls) |
| `name` | string | Human-readable charger name |
| `status` | int | Device connection status: `4` = online/connected |
| `signal` | int | WiFi RSSI in dBm (e.g. `-51` = good signal) |
| `type` | int | Device type code: `4` = AZ Charger (mirrors `deviceType`) |
| `sn` | string | Serial number (`"N/A"` if not set) |
| `fw` | string | Charger firmware version |
| `hw` | int | Hardware revision |

### `devices[n].charge`

| Field | Type | Meaning |
|---|---|---|
| `status` | int | Charger status: `2` = actively charging |
| `state` | int | Charge state: `0` = normal (TBD: fault codes) |
| `current` | int[3] | Per-phase charging current in mA: `[L1, L2, L3]` |
| `temperature` | int | Charger board temperature in °C |
| `boost` | int | Boost active: `1` = on, `0` = off |
| `boostSource` | int | Source triggering boost: `0` = none (TBD: other values) |
| `circuitBreaker` | int | Max allowed current from circuit breaker in A (here: 32 A) |
| `triggerPhase` | int | Phase that triggered charging decision: `0` = none/all |
| `totalPower` | int | Total charging power in W across all phases |
