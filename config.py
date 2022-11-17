import os
import re
import logging

import yaml

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def getListenerUrl() -> str:
    if os.getenv("LOGZIO_REGION") == 'us':
        return "https://listener.logz.io:8053"
    else:
        return "https://listener.logz.io:8053".replace("listener.", "listener-{}.".format(os.getenv("LOGZIO_REGION")))


# is_valid_logzio_token checks if a given token is a valid logz.io token
def is_valid_logzio_token(token):
    if type(token) is not str:
        raise TypeError("Token should be a string")
    regex = r"\b[a-zA-Z]{32}\b"
    match_obj = re.search(regex, token)
    if match_obj is not None and match_obj.group() is not None:
        if any(char.islower() for char in token) and any(char.isupper() for char in token):
            return True
    raise ValueError("Invalid token: {}".format(token))


# is_valid_logzio_region_code checks that a the region code is a valid logzio region code.
# an empty string ("") is also acceptable
def is_valid_logzio_region_code(logzio_region_code):
    if logzio_region_code is None or type(logzio_region_code) is not str:
        raise TypeError("Logzio region code should be a string")
    valid_logzio_regions = ["au", "ca", "eu", "nl", "uk", "us", "wa"]
    if logzio_region_code != "":
        if logzio_region_code not in valid_logzio_regions:
            raise ValueError("invalid logzio region code: {}. cannot start monitoring".format(logzio_region_code))
    return True


def is_valid_aggregation_temporality(aggregation_temporality):
    if type(aggregation_temporality) is not str:
        raise TypeError("AGGREGATION_TEMPORALITY should be a string")
    valid_aggregation_temporality = ["delta", "cumulative"]
    if aggregation_temporality != "":
        if aggregation_temporality not in valid_aggregation_temporality:
            raise ValueError(
                "invalid aggregation_temporality: {}. allowed values are {}".format(aggregation_temporality,
                                                                                    valid_aggregation_temporality))
    return True


def is_valid_log_level(log_level):
    if type(log_level) is not str:
        raise TypeError("LOG_LEVEL should be a string")
    valid_log_levels = ["info", "debug"]
    if log_level != "":
        if log_level not in valid_log_levels:
            raise ValueError(
                "invalid log level: {}. allowed values are {}".format(log_level,
                                                                      valid_log_levels))
    return True


def inputValidator():
    is_valid_logzio_region_code(os.getenv("LOGZIO_REGION"))
    is_valid_logzio_token(os.getenv("LOGZIO_TRACES_TOKEN"))
    is_valid_logzio_token(os.getenv("LOGZIO_METRICS_TOKEN"))
    if os.getenv("AGGREGATION_TEMPORALITY") is not None:
        is_valid_aggregation_temporality(os.getenv("AGGREGATION_TEMPORALITY"))
    if os.getenv("LOG_LEVEL") is not None:
        is_valid_log_level(os.getenv("LOG_LEVEL"))


if __name__ == '__main__':
    inputValidator()
    with open("/etc/otel/config.yaml") as f:
        config = yaml.safe_load(f)
    # Update logzio traces exporter
    logger.info('Updating logzio traces exporter')
    config["exporters"]["logzio"]["region"] = os.getenv("LOGZIO_REGION")
    config["exporters"]["logzio"]["account_token"] = os.getenv("LOGZIO_TRACES_TOKEN")
    # Update logzio metrics exporter
    logger.info('Updating logzio metrics exporter')
    config["exporters"]["prometheusremotewrite"]["endpoint"] = getListenerUrl()
    config["exporters"]["prometheusremotewrite"]["headers"][
        "Authorization"] = f'Bearer {os.getenv("LOGZIO_METRICS_TOKEN")}'
    # Update span metrics processor (optional parameters)
    if os.getenv("SPAN_METRICS_DIMENSIONS") is not None:
        logger.info('Updating span metrics dimensions')
        metricsDimensions = os.getenv("SPAN_METRICS_DIMENSIONS").replace(' ', '').split(',')
        for dim in metricsDimensions:
            config["processors"]["spanmetrics"]["dimensions"].append({'name': dim})
    else:
        logger.info('No span metrics dimensions found in environment variables, setting to default')

    if os.getenv("SPAN_METRICS_DIMENSIONS_CACHE_SIZE") is not None:
        logger.info('Updating span metrics dimensions_cache_size')
        config["processors"]["spanmetrics"]["dimensions_cache_size"] = int(
            os.getenv("SPAN_METRICS_DIMENSIONS_CACHE_SIZE"))
    else:
        logger.info('No span metrics dimensions_cache_size found in environment variables, setting to default: 100000')

    if os.getenv("LATENCY_HISTOGRAM_BUCKETS") is not None:
        logger.info('Updating span metrics latency_histogram_buckets')
        latencyBuckets = os.getenv("LATENCY_HISTOGRAM_BUCKETS").replace(' ', '').split(',')
        for buck in latencyBuckets:
            config["processors"]["spanmetrics"]["latency_histogram_buckets"].append(buck)
    else:
        logger.info('No span metrics latency_histogram_buckets found in environment variables, setting to default: ['
                    '2ms, 8ms, 50ms, 100ms, 200ms, 500ms, 1s, 5s, 10s]')

    if os.getenv("AGGREGATION_TEMPORALITY") is not None:
        logger.info('Updating span metrics aggregation_temporality')
        if os.getenv("AGGREGATION_TEMPORALITY") == 'delta':
            config["processors"]["spanmetrics"]["aggregation_temporality"] = "AGGREGATION_TEMPORALITY_DELTA"
    else:
        logger.info('No span metrics aggregation_temporality found in environment variables, setting to default: '
                    'AGGREGATION_TEMPORALITY_CUMULATIVE')

    if os.getenv("LOG_LEVEL") is not None:
        logger.info('Updating opentelemetry collector log level')
        logLevel = os.getenv("LOG_LEVEL")
        config["service"]["telemetry"]["logs"]["level"] = logLevel
    else:
        logger.info('No log level found in environment variables, setting to default: info')

    with open("/etc/otel/config.yaml", "w") as f:
        yaml.dump(config, f)
