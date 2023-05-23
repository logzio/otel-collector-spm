FROM alpine:latest as certs
RUN apk --update add ca-certificates

FROM python:3.7-slim
ARG TARGETARCH
COPY ./otel-config.yml /etc/otel/config.yaml
RUN pip install pyyaml
RUN apt-get update
RUN apt-get -y install curl
COPY ./config.py config.py
COPY ./entrypoint.sh entrypoint.sh
COPY --from=certs /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt    
ENV OPENTELEMETRY_COLLECTOR_VERSION 0.64.0
RUN curl --fail -L https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v$OPENTELEMETRY_COLLECTOR_VERSION/otelcol-contrib_$OPENTELEMETRY_COLLECTOR_VERSION_linux_$TARGETARCH.tar.gz -o otelcol-contrib.tar.gz
RUN tar -xf otelcol-contrib.tar.gz otelcol-contrib
RUN mv otelcol-contrib otelcontribcol
EXPOSE 4317 55680 55679 8888 6060 7276 9411 9943 1234 6831 6832 14250 14268 4317 4318 8888
RUN ["chmod", "+x", "/entrypoint.sh"]
RUN ["chmod", "+x", "/otelcontribcol"]
ENTRYPOINT ["/entrypoint.sh"]

