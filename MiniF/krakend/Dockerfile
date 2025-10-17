FROM krakend/builder:2.7.1 AS builder

WORKDIR /build/plugins
COPY plugins/ .

RUN go mod init internal-call && \
    go build -buildmode=plugin -o internal-call.so .

FROM devopsfaith/krakend:2.7.1

COPY --from=builder /build/plugins/internal-call.so /etc/krakend/plugins/
COPY krakend.json /etc/krakend/krakend.json

EXPOSE 8080
CMD ["run", "-c", "/etc/krakend/krakend.json"]
