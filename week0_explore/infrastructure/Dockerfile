FROM debian:bookworm-slim AS build

ARG TBAMUD_REF=master

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone --depth 1 --branch "$TBAMUD_REF" \
    https://github.com/tbamud/tbamud.git circlemud

WORKDIR /tmp/circlemud
RUN ./configure \
    && make -c src

FROM debian:bookworm-slim

RUN apt-get update \
    apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/circlemud
COPY --from=build /tmp/circlemud /opt/circlemud/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN cp -a /opt/circlemud/lib /opt/circlemud/lib.dist \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 4000

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD [ "bin/circle", "-q", "4000" ]
