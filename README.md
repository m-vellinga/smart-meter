# Smart Meter
Collecting data from a DSMR meter and pushing the data to influxdb.

## Requirements

* Python >=3.7
* Poetry

## Configuring
See src/config.py for configuration options. Create a .env file with your configuration. See .env.example for an example.

## Running

```
poetry install --no-dev --no-root
poetry run smart_meter.py --help
```
