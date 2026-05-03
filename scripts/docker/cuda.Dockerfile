FROM rust AS builder
WORKDIR /work
COPY . .
RUN cargo build -r --bin sbv2_api -F cuda,cuda_tf32
FROM ubuntu:24.04 AS upx
WORKDIR /work
RUN apt update && apt-get install -y upx binutils
COPY --from=builder /work/target/release/sbv2_api /work/main
COPY --from=builder /work/target/release/*.so /work
RUN upx --best --lzma /work/main
RUN find /work -maxdepth 1 -name "*.so" -exec strip --strip-unneeded {} +
FROM nvidia/cuda:12.6.2-cudnn-runtime-ubuntu24.04
WORKDIR /work
COPY --from=upx /work/main /work/main
COPY --from=upx /work/*.so /work
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work
CMD ["/work/main"]
