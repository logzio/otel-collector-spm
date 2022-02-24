## Exaple usage:
Run `logzio/otel-collector-spm` container:
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
### Send traces with `hotrod`:
Run hotrod container:
```
docker run \
  --rm \
  --link logzio-spm \
  --env JAEGER_AGENT_HOST=logzio-spm \
  --env JAEGER_AGENT_PORT=6831 \
  -p8080-8083:8080-8083 \
  jaegertracing/example-hotrod:latest \
  all
```
Then open [http://127.0.0.1:8080](http://127.0.0.1:8080) and start generating traces
