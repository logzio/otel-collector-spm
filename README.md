# otel-collector-spm

This docker container runs OpenTelemetry collector with the most common receivers (`jaeger` `opencensus` `otlp` `zipkin`) and exports traces and span metrics to Logz.io for performance monitoring.

**This project is currently in beta and subject to breaking changes**

**NOTE: The monitor tab in logz.io tracing calculates statistics only for `server` span kind at the moment**

### Before you start you will need:
* Docker installed on your host
* Logz.io tracing account
* Logz.io span metrics account. **IMPORTANT: The account name should include your tracing account name, for example if your tracing account name is `tracing`, your metrics account should be named something like `tracing-metrics`**

## Quick start:
### Pull docker image:
```
docker pull logzio/otel-collector-spm
```

### Run the container

When running on a Linux host, use the `--network host` flag to publish the collector ports:

```
docker run --name logzio-spm \
-e LOGZIO_REGION=<<LOGZIO_REGION>> \
-e LOGZIO_TRACES_TOKEN=<<LOGZIO_TRACES_TOKEN>> \
-e LOGZIO_METRICS_TOKEN=<<LOGZIO_METRICS_TOKEN>> \
--network host \
logzio/otel-collector-spm
```

When running on MacOS or Windows hosts, publish the ports using the `-p` flag:

```
docker run --name logzio-spm \
-e LOGZIO_REGION=<<LOGZIO_REGION>> \
-e LOGZIO_TRACES_TOKEN=<<LOGZIO_TRACES_TOKEN>> \
-e LOGZIO_METRICS_TOKEN=<<LOGZIO_METRICS_TOKEN>> \
-p 55678-55680:55678-55680 \
-p 1777:1777 \
-p 9411:9411 \
-p 9943:9943 \
-p 6831:6831 \
-p 6832:6832 \
-p 14250:14250 \
-p 14268:14268 \
-p 4317:4317 \
-p 55681:55681 \
logzio/otel-collector-spm
```

### Environment variables configuration:
* `LOG_LEVEL` (Optional) : Defines the opentelemetry collector log level. One of either `info` or `debug`. Default: `info`

* `LATENCY_HISTOGRAM_BUCKETS` (Optional): Comma separated list of durations defining the latency histogram buckets. Default: `2ms, 8ms, 50ms, 100ms, 200ms, 500ms, 1s, 5s, 10s`

* `SPAN_METRICS_DIMENSIONS` (Optional) : Each metric will have at least the following dimensions because they are common across all spans: `Service name`,`Operation`,`Span kind`,`Status code`.  The input is comma separated list of dimensions to add together with the default dimensions (example: `region,http.url`). Each additional dimension is defined with a name which is looked up in the span's collection of attributes or resource attributes. If the named attribute is missing in the span, this dimension will be omitted from the metric.

* `SPAN_METRICS_DIMENSIONS_CACHE_SIZE` (Optional): the max items number of metric_key_to_dimensions_cache. If not provided, will use default value size 10000.

* `AGGREGATION_TEMPORALITY` (Optional) : Defines the aggregation temporality of the generated metrics. One of either `cumulative` or `delta`. Default: `cumulative`

### receiver ports

- Jaeger
    - thrift_compact : 6831
    - thrift_binary : 6832
    - grpc : 14250
    - thrift_http : 14268

- Opencensus
    - 55678
    
- Otlp
    - grpc : 4317
    - http : 55681

- Zipkin
    - 9411

## Changelog
**1.0.0**
- SPM container initial release

