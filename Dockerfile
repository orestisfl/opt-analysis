from ubuntu:18.04

# Install basic stuff
run apt-get update -qq \
    && apt-get full-upgrade -y \
    && apt-get install -y automake build-essential cmake git software-properties-common wget zip python3-termcolor python3-tqdm

# Install llvm 10.x
# See https://apt.llvm.org/
add https://apt.llvm.org/llvm-snapshot.gpg.key llvm.key
run apt-key add llvm.key \
    && echo 'deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-10 main' >> /etc/apt/sources.list \
    && apt-get update -qq \
    && apt-get install -qq clang-10 llvm-10
env PATH="/usr/lib/llvm-10/bin:$PATH"

run apt-get install -y libtool \
    && git clone --depth 1 https://github.com/csmith-project/csmith \
    && cd csmith \
    && autoreconf -fi \
    && ./configure --prefix=/usr \
    && make install -j10 \
    && make install -C runtime install -j
