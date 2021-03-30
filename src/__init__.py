from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V4
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from .config import general_config, influx_config


influx_client = None
if influx_config.enabled:
    influx_client = InfluxDBClient(
        url=str(influx_config.URL),
        token=influx_config.TOKEN.get_secret_value(),
    )
    influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)

serial_reader = SerialReader(
    device=general_config.SERIAL_DEVICE,
    serial_settings=SERIAL_SETTINGS_V4,
    telegram_specification=telegram_specifications.V4,
)


def read_once():
    return extract_measurement(telegram=next(serial_reader.read_as_object()))


def read_stream(persist=False):
    for telegram in serial_reader.read_as_object():
        measurement = extract_measurement(telegram=telegram)
        if persist:
            push_to_influx(measurement)

        yield measurement


def extract_measurement(telegram=None):
    timestamp = telegram.P1_MESSAGE_TIMESTAMP.value
    power_usage = sum(
        [
            telegram.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE.value,
            telegram.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE.value,
            telegram.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE.value,
        ]
    )
    power_delivery = sum(
        [
            telegram.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE.value,
            telegram.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE.value,
            telegram.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE.value,
        ]
    )

    return Measurement(
        timestamp=timestamp,
        power_usage=power_usage,
        power_delivery=power_delivery,
    )


def push_to_influx(measurement=None):
    assert measurement

    if not influx_config.enabled:
        return

    points = [
        Point("power")
        .field("usage", measurement.power_usage)
        .time(measurement.timestamp),
        Point("power")
        .field("delivery", measurement.power_delivery)
        .time(measurement.timestamp),
    ]

    influx_write_api.write(influx_config.BUCKET, influx_config.ORG, points)


class Measurement:
    def __init__(self, timestamp=None, power_usage=None, power_delivery=None):
        assert all(
            [
                timestamp is not None,
                power_usage is not None,
                power_delivery is not None,
            ]
        )

        self.timestamp = timestamp
        self.power_usage = power_usage
        self.power_delivery = power_delivery

    def __str__(self):
        return str(
            f"{self.timestamp}: "
            f"usage={self.power_usage}kW "
            f"delivery={self.power_delivery}kW",
        )
