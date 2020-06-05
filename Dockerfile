from ubuntu:18.04

# Install basic stuff
run apt-get update -qq \
    && apt-get full-upgrade -y \
    && apt-get install -y automake build-essential cmake git software-properties-common wget zip \
                          python python-pip python-tqdm ipython

# Install llvm 10.x
# See https://apt.llvm.org/
add https://apt.llvm.org/llvm-snapshot.gpg.key llvm.key
run apt-key add llvm.key \
    && echo 'deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-10 main' >> /etc/apt/sources.list \
    && apt-get update -qq \
    && apt-get install -qq clang-10 llvm-10
env PATH="/usr/lib/llvm-10/bin:$PATH"

run mkdir sidechannel \
    && cd sidechannel \
    && git clone --depth 1 https://github.com/SideChannelMarvels/Tracer \
    && apt-get install -y automake libcapstone-dev libsqlite3-dev \
    && cd Tracer/TracerGrind \
    && wget https://sourceware.org/pub/valgrind/valgrind-3.15.0.tar.bz2 \
    && tar xf valgrind-3.15.0.tar.bz2 \
    && cp -r tracergrind valgrind-3.15.0/ \
    && patch -p0 < valgrind-3.15.0.diff \
    && cd valgrind-3.15.0/ \
    && ./autogen.sh \
    && ./configure --prefix=/usr \
    && make -j10 \
    && make install \
    && cd ../texttrace/ \
    && make \
    && make install

run cd sidechannel \
    && git clone --depth 1 https://github.com/SideChannelMarvels/Daredevil \
    # && apt-get install -y libomp-dev \
    && cd Daredevil \
    && make -j \
    && make install

# Install package globally
add . /opt-analysis
run cd /opt-analysis && pip install -U .
