FROM alpine:latest as certs
RUN apk --update add ca-certificates

FROM python:3.7-slim
COPY ./otel-config.yml /etc/otel/config.yaml
RUN pip install pyyaml
COPY ./config.py config.py
COPY ./entrypoint.sh entrypoint.sh
COPY --from=certs /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY otelcol-contrib /otelcontribcol
EXPOSE 4317 55680 55679 8888 6060 7276 9411 9943 1234 6831 6832 14250 14268 4317 55681 8888
RUN ["chmod", "+x", "/entrypoint.sh"]
RUN ["chmod", "+x", "/otelcontribcol"]
ENTRYPOINT ["/entrypoint.sh"]

