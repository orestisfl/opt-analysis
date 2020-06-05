from deadpool_dca import TracerGrind


def _ches2016_processinput(iblock, blocksize):
    p = "%0*x" % (2 * blocksize, iblock)
    return None, [p[j * 2 : (j + 1) * 2] for j in range(len(p) // 2)]


def _ches2016_processoutput(output, _):
    return int(
        "".join(
            [x for x in output.split("\n") if x.find("OUTPUT") == 0][0][10:].split(" ")
        ),
        16,
    )


def _nsc2013_processinput(iblock, blocksize):
    return None, ["%0*x" % (2 * blocksize, iblock)]


def _nsc2013_processoutput(output, blocksize):
    return int(
        "".join(
            [x for x in output.split("\n") if x.find("Output") == 0][0][10:57].split(
                " "
            )
        ),
        16,
    )


def _kryptologik_processinput(iblock, blocksize):
    p = "%0*x" % (2 * blocksize, iblock)
    return None, [p[j * 2 : (j + 1) * 2] for j in range(len(p) // 2)]


def _kryptologik_processoutput(output, blocksize):
    return int(output, 16)


TARGETS = {
    "kryptologik": (_kryptologik_processinput, _kryptologik_processoutput),
    "ches2016": (_ches2016_processinput, _ches2016_processoutput),
    "nsc2013": (_nsc2013_processinput, _nsc2013_processoutput),
}
BIN2DAREDEVIL = {
    "kryptologik": {"algorithm": "AES", "position": "LUT/AES_AFTER_SBOX"},
    "ches2016": {
        "attack_sbox": {"algorithm": "AES", "position": "LUT/AES_AFTER_SBOX"},
        "attack_multinv": {"algorithm": "AES", "position": "LUT/AES_AFTER_MULTINV",},
    },
    "nsc2013": {"algorithm": "AES", "position": "LUT/AES_AFTER_SBOX"},
}
CONFIGS = {
    "kryptologik": "mem_addr1_rw1",
    "ches2016": "mem_addr1_rw1",
    "nsc2013": "mem_data_rw1",
}
KEYS = {
    "kryptologik": "0D9BE960C438FF85F656BD48B78A0EE2",
    "ches2016": "dec1a551f1eddec0de4b1dae5c0de511",
    "nsc2013": "4b45595f4b45595f4b45595f4b45595f",
}
