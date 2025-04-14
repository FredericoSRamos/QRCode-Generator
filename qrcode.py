NUMERIC = 0
ALPHANUMERIC = 1
BYTE = 2
KANJI = 3

def data_type(data: str) -> int:
    if data.isdecimal():
        return NUMERIC
        
    if all(char in set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:") for char in data):
        return ALPHANUMERIC
        
    return BYTE
    
def encode_numeric(data: str) -> str:
    number_groups = []

    while len(data) > 3:
        number_groups.append(data[:3])
        data = data[3:]
        
    if data:
        number_groups.append(data)

    encoded_data = ""

    for group in number_groups:
        num = int(group)
        
        if len(group) == 3:
            encoded_data += format(num, '010b')
        elif len(group) == 2:
            encoded_data += format(num, '07b')
        elif len(group) == 1:
            encoded_data += format(num, '04b')

    return encoded_data
    
def encode_alphanumeric(data: str) -> str:
    string_pairs = []

    while len(data) > 1:
        string_pairs.append(data[:2])
        data = data[2:]
    
    if data:
        string_pairs.append(data)

    encoded_data = ""
    alphanumeric_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

    for pair in string_pairs:
        if len(pair) == 2:
            value = alphanumeric_chars.index(pair[0]) * 45 + alphanumeric_chars.index(pair[1])
            encoded_data += format(value, '011b')
        else:
            value = alphanumeric_chars.index(pair[0])
            encoded_data += format(value, '06b')

    return encoded_data
    
def encode_byte(data: str) -> str:
    return ''.join(format(byte, '08b') for byte in data.encode('utf-8'))
    
def encode_data(data: str) -> str:
    encode_type = data_type(data)
    
    character_capacity_table = [
        [34, 20, 14], [63, 38, 26], [101, 61, 42], [149, 90, 62], [202, 122, 84],
        [255, 154, 106], [293, 178, 122], [365, 221, 152], [432, 262, 180], [513, 311, 213],
        [604, 366, 251], [691, 419, 287], [796, 483, 331], [871, 528, 362], [991, 600, 412],
        [1082, 656, 450], [1212, 734, 504], [1346, 816, 560], [1500, 909, 624], [1600, 970, 666],
        [1708, 1035, 711], [1872, 1134, 779], [2059, 1248, 857], [2188, 1326, 911], [2395, 1451, 997],
        [2544, 1542, 1059], [2701, 1637, 1125], [2857, 1732, 1190], [3035, 1839, 1264], [3289, 1994, 1370],
        [3486, 2113, 1452], [3693, 2238, 1538], [3909, 2369, 1628], [4134, 2506, 1722], [4343, 2632, 1809],
        [4588, 2780, 1911], [4775, 2894, 1989], [5039, 3054, 2099], [5313, 3220, 2213], [5596, 3391, 2331]
    ]
    
    # size = version * 4 + 17
    version = 0

    for i in range(len(character_capacity_table)):
        if character_capacity_table[i][encode_type] >= len(data):
            version = i + 1
            break

    if version == 0:
        raise ValueError("Cannot fit this much data in the QR Code")
    
    mode_indicator = format(2 ** encode_type, '04b')
        
    if version < 10:
        character_count_size = ['010b', '09b', '08b', '08b']
    elif version < 27:
        character_count_size = ['012b', '011b', '016b', '010b']
    else:
        character_count_size = ['014b', '013b', '016b', '012b']

    character_count = format(len(data), character_count_size[encode_type])
    
    data_codewords_number = [16, 28, 44, 64, 86, 108, 124, 154, 182, 216, 254, 290, 334, 365, 415, 453, 507, 563, 627, 669,
                            714, 782, 860, 914, 1000, 1062, 1128, 1193, 1267, 1373, 1455, 1541, 1631, 1725, 1812, 1914, 1992, 2102, 2216, 2334]
    
    required_bits = data_codewords_number[version - 1] * 8
    
    if encode_type == NUMERIC:
        encoded_data = encode_numeric(data)
    elif encode_type == ALPHANUMERIC:
        encoded_data = encode_alphanumeric(data)
    else:
        encoded_data = encode_byte(data)
        
    concatenated_string = mode_indicator + character_count + encoded_data
    
    bits_left = required_bits - len(concatenated_string)
    
    if bits_left >= 4:
        concatenated_string += '0000'
    else:
        concatenated_string += '0' * bits_left
        
    concatenated_string += '0' * ((8 - len(concatenated_string) % 8) % 8)
    
    bits_left = (required_bits - len(concatenated_string)) // 8
    
    pad_bytes = ['11101100', '00010001']
    for i in range(bits_left):
        concatenated_string += pad_bytes[i % 2]
        
    return concatenated_string
