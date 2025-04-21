NUMERIC = 0
ALPHANUMERIC = 1
BYTE = 2
KANJI = 3

def get_data_type(data: str) -> int:
    if data.isdecimal():
        return NUMERIC
        
    if all(char in set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:") for char in data):
        return ALPHANUMERIC
        
    return BYTE
    
def get_version_and_error_correction_level(data: str, encode_type: int) -> int:
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
    
    version = 0

    for i in range(len(character_capacity_table)):
        if character_capacity_table[i][encode_type] >= len(data):
            version = i + 1
            break

    if version == 0:
        raise ValueError("Cannot fit this much data in the QR Code")
        
    return version, 'M'
    
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
    
def encode_data(data: str, version: int, encode_type: int) -> str:
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

def split_data(data_codewords: str, version: int):
    error_correction_table = {
        1:  {"group1": (1, 16), "group2": None}, 2:  {"group1": (1, 28), "group2": None}, 3:  {"group1": (1, 44), "group2": None},
        4:  {"group1": (2, 32), "group2": None}, 5:  {"group1": (2, 43), "group2": None}, 6:  {"group1": (4, 27), "group2": None},
        7:  {"group1": (4, 31), "group2": None}, 8:  {"group1": (2, 38), "group2": (2, 39)}, 9:  {"group1": (3, 36), "group2": (2, 37)},
        10: {"group1": (4, 43), "group2": (1, 44)}, 11: {"group1": (1, 50), "group2": (4, 51)}, 12: {"group1": (6, 36), "group2": (2, 37)},
        13: {"group1": (8, 37), "group2": (1, 38)}, 14: {"group1": (4, 40), "group2": (5, 41)}, 15: {"group1": (5, 41), "group2": (5, 42)},
        16: {"group1": (7, 45), "group2": (3, 46)}, 17: {"group1": (10, 46), "group2": (1, 47)}, 18: {"group1": (9, 43), "group2": (4, 44)},
        19: {"group1": (3, 44), "group2": (11, 45)}, 20: {"group1": (3, 41), "group2": (13, 42)}, 21: {"group1": (17, 42), "group2": None},
        22: {"group1": (17, 46), "group2": None}, 23: {"group1": (4, 47), "group2": (14, 48)}, 24: {"group1": (6, 45), "group2": (14, 46)},
        25: {"group1": (8, 47), "group2": (13, 48)}, 26: {"group1": (19, 46), "group2": (4, 47)}, 27: {"group1": (22, 45), "group2": (3, 46)},
        28: {"group1": (3, 45), "group2": (23, 46)}, 29: {"group1": (21, 45), "group2": (7, 46)}, 30: {"group1": (19, 47), "group2": (10, 48)},
        31: {"group1": (2, 46), "group2": (29, 47)}, 32: {"group1": (10, 46), "group2": (23, 47)}, 33: {"group1": (14, 46), "group2": (21, 47)},
        34: {"group1": (14, 46), "group2": (23, 47)}, 35: {"group1": (12, 47), "group2": (26, 48)}, 36: {"group1": (6, 47), "group2": (34, 48)},
        37: {"group1": (29, 46), "group2": (14, 47)}, 38: {"group1": (13, 46), "group2": (32, 47)}, 39: {"group1": (40, 47), "group2": (7, 48)},
        40: {"group1": (18, 47), "group2": (31, 48)},
    }

    config = error_correction_table[version]
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

def get_ecc(dividend, codewords: int):
    GALOIS_LOG = [0, 0, 1, 25, 2, 50, 26, 198, 3, 223, 51, 238, 27, 104, 199, 75, 4, 100, 224, 14, 52, 141, 239, 129, 28, 193, 105,
                  248, 200, 8, 76, 113, 5, 138, 101, 47, 225, 36, 15, 33, 53, 147, 142, 218, 240, 18, 130, 69, 29, 181, 194, 125, 106, 39, 249,
                  185, 201, 154, 9, 120, 77, 228, 114, 166, 6, 191, 139, 98, 102, 221, 48, 253, 226, 152, 37, 179, 16, 145, 34, 136, 54, 208, 148,
                  206, 143, 150, 219, 189, 241, 210, 19, 92, 131, 56, 70, 64, 30, 66, 182, 163, 195, 72, 126, 110, 107, 58, 40, 84, 250, 133, 186, 61,
                  202, 94, 155, 159, 10, 21, 121, 43, 78, 212, 229, 172, 115, 243, 167, 87, 7, 112, 192, 247, 140, 128, 99, 13, 103, 74, 222, 237, 49,
                  197, 254, 24, 227, 165, 153, 119, 38, 184, 180, 124, 17, 68, 146, 217, 35, 32, 137, 46, 55, 63, 209, 91, 149, 188, 207, 205, 144, 135,
                  151, 178, 220, 252, 190, 97, 242, 86, 211, 171, 20, 42, 93, 158, 132, 60, 57, 83, 71, 109, 65, 162, 31, 45, 67, 216, 183, 123, 164, 118,
                  196, 23, 73, 236, 127, 12, 111, 246, 108, 161, 59, 82, 41, 157, 85, 170, 251, 96, 134, 177, 187, 204, 62, 90, 203, 89, 95, 176, 156, 169,
                  160, 81, 11, 245, 22, 235, 122, 117, 44, 215, 79, 174, 213, 233, 230, 231, 173, 232, 116, 214, 244, 234, 168, 80, 88, 175]
                  
    GALOIS_ANTILOG = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96,
                      192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210,
                      185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127,
                      254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248,
                      237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77,
                      154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246,
                      241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112,
                      224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245,
                      247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1]
    
    def galois_multiplication(x, y):
        if x == 0:
            return 0
        return GALOIS_ANTILOG[(GALOIS_LOG[x] + GALOIS_LOG[y]) % 255]

    dividend.extend([0] * codewords)
    
    generator_polynomials = {
        7: [1, 127, 122, 154, 164, 11, 68, 117],
        10: [1, 216, 194, 159, 111, 199, 94, 95, 113, 157, 193],
        13: [1, 137, 73, 227, 17, 177, 17, 52, 13, 46, 43, 83, 132, 120],
        15: [1, 29, 196, 111, 163, 112, 74, 10, 105, 105, 139, 132, 151, 32, 134, 26],
        16: [1, 59, 13, 104, 189, 68, 209, 30, 8, 163, 65, 41, 229, 98, 50, 36, 59],
        17: [1, 119, 66, 83, 120, 119, 22, 197, 83, 249, 41, 143, 134, 85, 53, 125, 99, 79],
        18: [1, 239, 251, 183, 113, 149, 175, 199, 215, 240, 220, 73, 82, 173, 75, 32, 67, 217, 146],
        20: [1, 152, 185, 240, 5, 111, 99, 6, 220, 112, 150, 69, 36, 187, 22, 228, 198, 121, 121, 165, 174],
        22: [1, 89, 179, 131, 176, 182, 244, 19, 189, 69, 40, 28, 137, 29, 123, 67, 253, 86, 218, 230, 26, 145, 245],
        24: [1, 122, 118, 169, 70, 178, 237, 216, 102, 115, 150, 229, 73, 130, 72, 61, 43, 206, 1, 237, 247, 127, 217, 144, 117],
        26: [1, 246, 51, 183, 4, 136, 98, 199, 152, 77, 56, 206, 24, 145, 40, 209, 117, 233, 42, 135, 68, 70, 144, 146, 77, 43, 94],
        28: [1, 252, 9, 28, 13, 18, 251, 208, 150, 103, 174, 100, 41, 167, 12, 247, 56, 117, 119, 233, 127, 181, 100, 121, 147, 176, 74, 58, 197],
        30: [1, 212, 246, 77, 73, 195, 192, 75, 98, 5, 70, 103, 177, 22, 217, 138, 51, 181, 246, 72, 25, 18, 46, 228, 74, 216, 195, 11, 106, 130, 150]
    }
    
    divisor = generator_polynomials[codewords]

    msg_out = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = msg_out[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                msg_out[i + j] ^= galois_multiplication(divisor[j], coef)

    return msg_out[-(len(divisor) - 1):]

def structure_final_message(encoded_data: str, version: int):
    codewords = [int(encoded_data[i:i+8], 2) for i in range(0, len(encoded_data), 8)]

    groups = split_data(codewords, version)
    
    error_correction_codewords = [10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26,
                                  26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28]
    
    ecc_count = error_correction_codewords[version - 1]

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
    
def place_finder_patterns(matrix, size: int):
    # Top-left finder pattern
    for i in range(7):
        for j in range(7):
            # Outer border
            if i == 0 or i == 6 or j == 0 or j == 6:
                matrix[i][j] = 1
            # 3x3 inner area
            elif 2 <= i <= 4 and 2 <= j <= 4:
                matrix[i][j] = 1
            # Fill the remaining area
            else:
                matrix[i][j] = 0
    
    # Top-right and bottom-left finder patterns
    start_limit = size - 7
    for i in range(start_limit, size):
        for j in range(7):
            # Outer border
            if i == start_limit or i == size - 1 or j == 0 or j == 6:
                matrix[i][j] = 1
                matrix[j][i] = 1
            # 3x3 inner area
            elif start_limit + 2 <= i <= start_limit + 4 and 2 <= j <= 4:
                matrix[i][j] = 1
                matrix[j][i] = 1
            # Fill the remaining area
            else:
                matrix[i][j] = 0
                matrix[j][i] = 0
                
def place_separators(matrix, size: int):
    # Add separators for top-left finder pattern
    for i in range(8):
        matrix[7][i] = 0
        matrix[i][7] = 0
    
    # Add separators for one side of bottom-left and top-right finder patterns
    for i in range(size - 8, size):
        matrix[7][i] = 0
        matrix[i][7] = 0
    
    # Add separators for remaining side of bottom-left and top-right finder patterns
    i = size - 8
    for j in range(7):
        matrix[i][j] = 0
        matrix[j][i] = 0
                
def place_alignment_patterns(matrix, version: int):
    alignment_pattern_locations = {
        2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46],
        10: [6, 28, 50], 11: [6, 30, 54], 12: [6, 32, 58], 13: [6, 34, 62], 14: [6, 26, 46, 66], 15: [6, 26, 48, 70],
        16: [6, 26, 50, 74], 17: [6, 30, 54, 78], 18: [6, 30, 56, 82], 19: [6, 30, 58, 86], 20: [6, 34, 62, 90],
        21: [6, 28, 50, 72, 94], 22: [6, 26, 50, 74, 98], 23: [6, 30, 54, 78, 102], 24: [6, 28, 54, 80, 106],
        25: [6, 32, 58, 84, 110], 26: [6, 30, 58, 86, 114], 27: [6, 34, 62, 90, 118], 28: [6, 26, 50, 74, 98, 122],
        29: [6, 30, 54, 78, 102, 126], 30: [6, 26, 52, 78, 104, 130], 31: [6, 30, 56, 82, 108, 134], 32: [6, 34, 60, 86, 112, 138],
        33: [6, 30, 58, 86, 114, 142], 34: [6, 34, 62, 90, 118, 146], 35: [6, 30, 54, 78, 102, 126, 150], 36: [6, 24, 50, 76, 102, 128, 154],
        37: [6, 28, 54, 80, 106, 132, 158], 38: [6, 32, 58, 84, 110, 136, 162], 39: [6, 26, 54, 82, 110, 138, 166], 40: [6, 30, 58, 86, 114, 142, 170]
    }
    
    # Returns early since version 1 doesn't have alignment patterns
    if version == 1:
        return
    
    locations = alignment_pattern_locations[version]
    
    for row in locations:
        for column in locations:
            if (matrix[row - 2][column - 2] != -1 or matrix[row - 2][column + 2] != -1 or
                matrix[row + 2][column - 2] != -1 or matrix[row + 2][column + 2] != -1):
                continue
                
            for i in range(row - 2, row + 3):
                for j in range(column - 2, column + 3):
                    if i == row - 2 or i == row + 2 or j == column - 2 or j == column + 2:
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0
            matrix[row][column] = 1
            
def place_timing_patterns(matrix, size: int):
    for i in range(8, size - 8):
        matrix[6][i] = 1 - i % 2
        matrix[i][6] = 1 - i % 2
        
def define_reserverd_areas(matrix, size: int):
    i = size - 8
    
    # Add dark module
    matrix[i][8] = 1
    
    # Add bottom-left reserved area
    while i < size - 1:
        i += 1
        matrix[i][8] = 0
    
    # Add top-left reserved area
    for j in range(9):
        matrix[8][j] = 0
        matrix[j][8] = 0
    
    # Place back the black modules that got overwritten by the top-left reserved area
    matrix[8][6] = 1
    matrix[6][8] = 1
    
    # Add top-right reserved area
    for j in range(size - 8, size):
        matrix[8][j] = 0
    
    # Add reserved version information area (for version 7 and above)
    if size >= 45:
        for i in range(size - 11, size - 8):
            for j in range(6):
                matrix[i][j] = 0
                matrix[j][i] = 0

def place_matrix_modules(data: str, version: int):
    size = version * 4 + 17

    matrix = [[-1 for _ in range(size)] for _ in range(size)]
    
    place_finder_patterns(matrix, size)
    place_separators(matrix, size)
    place_alignment_patterns(matrix, version)
    place_timing_patterns(matrix, size)
    define_reserverd_areas(matrix, size)
    
    tracker = 0
    row = size - 1
    column = size - 1
    
    direction = -1
    
    # Populate the matrix with the data and error correction bits in the specified pattern
    while tracker < len(data):
        if matrix[row][column] == -1:
            matrix[row][column] = data[tracker]
            tracker += 1
        column -= 1
        
        if matrix[row][column] == -1:
            matrix[row][column] = data[tracker]
            tracker += 1
        row += direction
        column += 1
            
        # Handle direction change
        if row == -1 or row == size:
            direction *= -1
            column -= 2
            row += direction
            
        # Ignore column with the vertical timing pattern
        if column == 6:
            column -= 1
            
    return matrix
    
def apply_masks(matrix, size: int):
    masked_matrices = [[row[:] for row in matrix] for _ in range(8)]
        
    # Apply mask patterns (Toggle modules)
    # 0 - (row + column) mod 2 == 0
    # 1 - row mod 2 == 0
    # 2 - column mod 3 == 0
    # 3 - (row + column) mod 3 == 0
    # 4 - (floor(row / 2) + floor(column / 3)) mod 2 == 0
    # 5 - ((row * column) mod 2) + ((row * column) mod 3) == 0
    # 6 - (((row * column) mod 2) + ((row * column) mod 3)) mod 2 == 0
    # 7 - (((row + column) mod 2) + ((row * column) mod 3) ) mod 2 == 0
    
    for row in range(size):
        for column in range(size):
            if matrix[row][column] == '0':
                masked_matrices[0][row][column] = 1 - (row + column) % 2
                masked_matrices[1][row][column] = 1 - row % 2
                masked_matrices[2][row][column] = 1 if column % 3 == 0 else 0
                masked_matrices[3][row][column] = 1 if (row + column) % 3 == 0 else 0
                masked_matrices[4][row][column] = 1 - (row // 2 + column // 3) % 2
                masked_matrices[5][row][column] = 1 if row * column % 2 + row * column % 3 == 0 else 0
                masked_matrices[6][row][column] = 1 - (row * column % 2 + row * column % 3) % 2
                masked_matrices[7][row][column] = 1 - ((row + column) % 2 + row * column % 3) % 2
            elif matrix[row][column] == '1':
                masked_matrices[0][row][column] = (row + column) % 2
                masked_matrices[1][row][column] = row % 2
                masked_matrices[2][row][column] = 0 if column % 3 == 0 else 1
                masked_matrices[3][row][column] = 0 if (row + column) % 3 == 0 else 1
                masked_matrices[4][row][column] = (row // 2 + column // 3) % 2
                masked_matrices[5][row][column] = 0 if row * column % 2 + row * column % 3 == 0 else 1
                masked_matrices[6][row][column] = (row * column % 2 + row * column % 3) % 2
                masked_matrices[7][row][column] = ((row + column) % 2 + row * column % 3) % 2
                
    return masked_matrices
    
def evaluate_first_penalty(matrix, size: int):
    penalty = 0
    
    for i in range(size):
        currentRow = -1
        currentColumn = -1
        sequenceRow = 0
        sequenceColumn = 0
        
        for j in range(size):
            if matrix[i][j] == currentRow:
                sequenceRow += 1
            else:
                if sequenceRow > 4:
                    penalty += sequenceRow - 2
                    
                currentRow = matrix[i][j]
                sequenceRow = 1
                
            if matrix[j][i] == currentColumn:
                sequenceColumn += 1
            else:
                if sequenceColumn > 4:
                    penalty += sequenceColumn - 2
                    
                currentColumn = matrix[j][i]
                sequenceColumn = 1
            
        if sequenceRow > 4:
            penalty += sequenceRow - 2
        if sequenceColumn > 4:
            penalty += sequenceColumn - 2
                
    return penalty
    
def evaluate_second_penalty(matrix, size: int):
    penalty = 0
    
    for i in range(size - 1):
        for j in range(size - 1):
            if matrix[i][j] == matrix[i + 1][j] == matrix[i][j + 1] == matrix[i + 1][j + 1]:
                penalty += 3
    
    return penalty
    
def evaluate_third_penalty(matrix, size: int):
    penalty = 0
    
    bad_patterns = ['10111010000', '00001011101']
    
    for i in range(size):
        for j in range(size - 10):
            horizontal_segment = ''.join(map(str, matrix[i][j:j + 11]))
            if horizontal_segment in bad_patterns:
                penalty += 40
            
            vertical_segment = ''.join(str(matrix[j + k][i]) for k in range(11))
            if vertical_segment in bad_patterns:
                penalty += 40
    
    return penalty
    
def evaluate_fourth_penalty(matrix, size: int):
    total_modules = size * size
    dark_modules_count = sum(row.count(1) for row in matrix)
            
    dark_modules_percentage = int(dark_modules_count / total_modules * 100)
    
    previous_multiple_of_five = (dark_modules_percentage // 5) * 5
    next_multiple_of_five = previous_multiple_of_five + 5
    
    return min(abs(previous_multiple_of_five - 50) / 5, abs(next_multiple_of_five - 50) / 5) * 10
    
def determine_best_mask(masked_matrices, size: int):
    lowest_penalty = float('inf')
    lowest_penalty_index = 0
    
    # Checks the 4 penalty rules for every mask
    for i in range(len(masked_matrices)):
        penalty = 0
        
        # The first rule gives the QR code a penalty for each group of five or more same-colored modules in a row (or column).
        penalty += evaluate_first_penalty(masked_matrices[i], size)
        
        # The second rule gives the QR code a penalty for each 2x2 area of same-colored modules in the matrix.
        penalty += evaluate_second_penalty(masked_matrices[i], size)
        
        # The third rule gives the QR code a large penalty if there are patterns that look similar to the finder patterns.
        penalty += evaluate_third_penalty(masked_matrices[i], size)
        
        # The fourth rule gives the QR code a penalty if more than half of the modules are dark or light, with a larger penalty for a larger difference.
        penalty += evaluate_fourth_penalty(masked_matrices[i], size)
        
        if penalty < lowest_penalty:
            lowest_penalty = penalty
            lowest_penalty_index = i
    
    # Chooses the one with the lowest penalty score
    return lowest_penalty_index

def mask_data(matrix, version: int):
    size = version * 4 + 17
    
    masked_matrices = apply_masks(matrix, size)
    lowest_penalty_index = determine_best_mask(masked_matrices, size)
    best_matrix = masked_matrices[lowest_penalty_index]
    
    return best_matrix
        
if __name__ == "__main__":
        
    data = 'HELLO WORLD'
    encode_type = get_data_type(data)
    version, error_correction_level = get_version_and_error_correction_level(data, encode_type)
    encoded_data = encode_data(data, version, encode_type)
    message = structure_final_message(encoded_data, version)
    matrix = place_matrix_modules(message, version)
    masked_matrix = mask_data(matrix, version)
    for a in masked_matrix:
        for b in a:
            print(f" {b} ", end="")
        print("")
