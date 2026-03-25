from typing import List
from constants import (
    EC_TABLE, GALOIS_ANTILOG, GALOIS_LOG,
    GENERATOR_POLYNOMIALS, EC_CODEWORDS
)

def split_data(data_codewords: List[int], version: int, ec_level: str) -> List[List[List[int]]]:
    """
    Splits the data codewords into groups and blocks based on version and EC level.
    """
    config = EC_TABLE[ec_level][version]
    group1 = config["group1"]
    group2 = config["group2"]

    groups = []
    blocks = []
    index = 0

    for _ in range(group1[0]):
        block_size = group1[1]
        blocks.append(data_codewords[index:index + block_size])
        index += block_size

    groups.append(blocks)

    if group2:
        blocks = []
        for _ in range(group2[0]):
            block_size = group2[1]
            blocks.append(data_codewords[index:index + block_size])
            index += block_size
        groups.append(blocks)

    return groups

def get_ecc(dividend: List[int], codewords: int) -> List[int]:
    """
    Generates Error Correction codewords for a block of data using polynomial division in Galois Field.
    """
    def galois_multiplication(x: int, y: int) -> int:
        if x == 0:
            return 0
        return GALOIS_ANTILOG[(GALOIS_LOG[x] + GALOIS_LOG[y]) % 255]

    dividend.extend([0] * codewords)
    divisor = GENERATOR_POLYNOMIALS[codewords]

    msg_out = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = msg_out[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                msg_out[i + j] ^= galois_multiplication(divisor[j], coef)

    return msg_out[-(len(divisor) - 1):]

def structure_final_message(encoded_data: str, version: int, ec_level: str) -> str:
    """
    Converts a binary string sequence into blocks, applies EC codewords to each block, 
    and concatenates them together in the interleaved order required by the QR Code spec.
    """
    codewords = [int(encoded_data[i:i+8], 2) for i in range(0, len(encoded_data), 8)]

    groups = split_data(codewords, version, ec_level)
    ecc_count = EC_CODEWORDS[version - 1][ec_level]

    ecc_blocks = []
    for group in groups:
        for block in group:
            ecc = get_ecc(list(block), ecc_count)
            ecc_blocks.append(ecc)

    final_message = []
    max_len = max(len(block) for group in groups for block in group)

    for i in range(max_len):
        for group in groups:
            for block in group:
                if i < len(block):
                    final_message.append(format(block[i], '08b'))

    for i in range(ecc_count):
        for ecc in ecc_blocks:
            final_message.append(format(ecc[i], '08b'))

    remainder_bits = [0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3,
                      4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0]
    
    final_message.extend(['0'] * remainder_bits[version - 1])

    return ''.join(final_message)
