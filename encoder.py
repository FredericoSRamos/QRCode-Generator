from typing import Tuple, Union
from constants import (
    NUMERIC, ALPHANUMERIC, BYTE, KANJI, ALPHANUMERIC_CHARS,
    CHARACTER_CAPACITY_TABLE, DATA_CODEWORDS, PAD_BYTES
)

def get_data_type(data: str) -> int:
    """
    Determines the appropriate QR Code data encoding type (NUMERIC, ALPHANUMERIC, BYTE, or KANJI).
    """
    if data.isdecimal():
        return NUMERIC

    if all(char in ALPHANUMERIC_CHARS for char in data):
        return ALPHANUMERIC

    try:
        encoded_data = data.encode("shift_jis")

        if len(encoded_data) % 2 != 0:
            return BYTE

        for i in range(0, len(encoded_data), 2):
            byte1, byte2 = encoded_data[i], encoded_data[i + 1]
            val = (byte1 << 8) | byte2

            if not (0x8140 <= val <= 0x9FFC or 0xE040 <= val <= 0xEBBF):
                return BYTE

        return KANJI
    except UnicodeEncodeError:
        return BYTE

def get_version_and_ec_level(data: str, encode_type: int, ec_level: str = '') -> Tuple[int, str]:
    """
    Determine the appropriate QR version and error correction level for the data.
    Raises ValueError if no valid combination is found or provided EC level is invalid.
    """
    VALID_EC_LEVELS = "HQML"

    if ec_level and ec_level not in VALID_EC_LEVELS:
        raise ValueError("Invalid error correction level provided")

    if encode_type == BYTE:
        data_length = len(encode_byte(data)) // 8
    else:
        data_length = len(data)

    if ec_level:
        for version, capacities in enumerate(CHARACTER_CAPACITY_TABLE):
            if capacities[ec_level][encode_type] >= data_length:
                return version + 1, ec_level
        raise ValueError("Cannot fit data with the specified error correction level")

    for ec_level_iter in VALID_EC_LEVELS:
        for version, capacities in enumerate(CHARACTER_CAPACITY_TABLE):
            if capacities[ec_level_iter][encode_type] >= data_length:
                return version + 1, ec_level_iter

    raise ValueError("Cannot fit data into a QR Code")

def encode_numeric(data: str) -> str:
    """
    Encodes numeric string data into binary representation.
    """
    number_groups = []
    
    while len(data) > 3:
        number_groups.append(data[:3])
        data = data[3:]
    if data:
        number_groups.append(data)

    encoded_data = []

    for group in number_groups:
        num = int(group)
        if len(group) == 3:
            encoded_data.append(f"{num:010b}")
        elif len(group) == 2:
            encoded_data.append(f"{num:07b}")
        elif len(group) == 1:
            encoded_data.append(f"{num:04b}")

    return ''.join(encoded_data)

def encode_alphanumeric(data: str) -> str:
    """
    Encodes alphanumeric string data into binary representation.
    """
    string_pairs = []

    while len(data) > 1:
        string_pairs.append(data[:2])
        data = data[2:]
    if data:
        string_pairs.append(data)

    encoded_data = []
    alphanumeric_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

    for pair in string_pairs:
        if len(pair) == 2:
            value = alphanumeric_chars.index(pair[0]) * 45 + alphanumeric_chars.index(pair[1])
            encoded_data.append(f"{value:011b}")
        else:
            value = alphanumeric_chars.index(pair[0])
            encoded_data.append(f"{value:06b}")

    return ''.join(encoded_data)

def encode_byte(data: str) -> str:
    """
    Encodes raw byte data into binary string representation.
    Uses ISO-8859-1 encoding if possible, falls back to UTF-8.
    """
    try:
        encoded_data = data.encode('ISO-8859-1')
    except UnicodeEncodeError:
        encoded_data = data.encode('UTF-8')

    return "".join(f"{byte:08b}" for byte in encoded_data)

def encode_kanji(data: str) -> str:
    """
    Encodes Kanji characters using Shift-JIS encoding into binary format.
    """
    encoded_shift_jis = data.encode('shift-jis')
    encoded_data = []
    i = 0
    
    while i < len(encoded_shift_jis):
        byte1 = encoded_shift_jis[i]
        byte2 = encoded_shift_jis[i + 1]
        shift_jis_value = (byte1 << 8) | byte2

        if 0x8140 <= shift_jis_value <= 0x9FFC:
            adjusted = shift_jis_value - 0x8140
        else:
            adjusted = shift_jis_value - 0xC140

        most_significant_byte = (adjusted >> 8) & 0xFF
        least_significant_byte = adjusted & 0xFF
        final_value = most_significant_byte * 0xC0 + least_significant_byte

        encoded_data.append(f"{final_value:013b}")
        i += 2

    return ''.join(encoded_data)

def encode_data(data: str, version: int, encode_type: int, ec_level: str) -> str:
    """
    Wrapper function that formats the length of the data and handles mode indicators,
    padding, and joining the final binary string based on encoding specifications.
    """
    mode_indicator = f"{1 << encode_type:04b}"

    if version < 10:
        character_count_size = ['010b', '09b', '08b', '08b']
    elif version < 27:
        character_count_size = ['012b', '011b', '016b', '010b']
    else:
        character_count_size = ['014b', '013b', '016b', '012b']

    character_count_bits = character_count_size[encode_type]

    if encode_type == NUMERIC:
        encoded_data = encode_numeric(data)
        character_count = f"{len(data):{character_count_bits}}"
    elif encode_type == ALPHANUMERIC:
        encoded_data = encode_alphanumeric(data)
        character_count = f"{len(data):{character_count_bits}}"
    elif encode_type == BYTE:
        encoded_data = encode_byte(data)
        character_count = f"{len(encoded_data) // 8:{character_count_bits}}"
    else:
        encoded_data = encode_kanji(data)
        character_count = f"{len(data):{character_count_bits}}"

    binary_parts = [mode_indicator, character_count, encoded_data]
    current_len = sum(len(p) for p in binary_parts)

    required_bits = DATA_CODEWORDS[version - 1][ec_level] * 8
    bits_left = required_bits - current_len

    if bits_left >= 4:
        binary_parts.append('0000')
        current_len += 4
    elif bits_left > 0:
        binary_parts.append('0' * bits_left)
        current_len += bits_left

    padding_needed = (8 - current_len % 8) % 8
    if padding_needed > 0:
        binary_parts.append('0' * padding_needed)
        current_len += padding_needed

    bytes_left = (required_bits - current_len) // 8
    for i in range(bytes_left):
        binary_parts.append(PAD_BYTES[i % 2])

    return "".join(binary_parts)
