FROM rust AS builder
WORKDIR /work
COPY . .
RUN cargo build -r --bin sbv2_api
FROM ubuntu:24.04 AS upx
WORKDIR /work
RUN apt update && apt-get install -y upx binutils
COPY --from=builder /work/target/release/sbv2_api /work/main
COPY --from=builder /work/target/release/*.so /work
RUN upx --best --lzma /work/main
RUN find /work -maxdepth 1 -name "*.so" -exec strip --strip-unneeded {} +
RUN find /work -maxdepth 1 -name "*.so" -exec upx --best --lzma {} +
FROM ubuntu:24.04
WORKDIR /work
COPY --from=upx /work/main /work/main
COPY --from=upx /work/*.so /work
CMD ["/work/main"]
