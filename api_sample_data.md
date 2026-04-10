# AZRouter API — Sample Data

Captured from `LOGGER.debug("Coordinator data: %s", data)` on 2026-04-10.

## `cloud/status`

```json
{
  "status": "online",
  "url": "https://new.azrouter.cloud/e831cd308360"
}
```

## `status`

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

## `power`

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

Notes:
- `input.power` values are in **W**, negative = export to grid (ids 0–2 = L1–L3, id 3 = always 0)
- `input.voltage` values are in **mV** (÷1000 → V)
- `input.current` values are in **mA** (÷1000 → A), negative = export
- `output.power` — per-output W (ids 0–3, meaning TBD)
- `output.energy` — per-output energy (unit TBD, ids 0–4)

## `devices`

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
    },
    "settings": ["...omitted for brevity..."]
  }
]
```

Notes:
- `charge.current` is a plain array (not id/value objects): `[L1_mA, L2_mA, L3_mA]`
- `charge.temperature` in °C
- `charge.status`: 2 = charging (enum TBD)
- `charge.circuitBreaker`: max current in A
