from PIL import Image

NUMERIC = 0
ALPHANUMERIC = 1
BYTE = 2
KANJI = 3

ALPHANUMERIC_CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")

CHARACTER_CAPACITY_TABLE = [
    { 'L': [41, 25, 17, 10], 'M': [34, 20, 14, 8], 'Q': [27, 16, 11, 7], 'H': [17, 10, 7, 4] },
    { 'L': [77, 47, 32, 20], 'M': [63, 38, 26, 16], 'Q': [48, 29, 20, 12], 'H': [34, 20, 14, 8] },
    { 'L': [127, 77, 53, 32], 'M': [101, 61, 42, 26], 'Q': [77, 47, 32, 20], 'H': [58, 35, 24, 15] },
    { 'L': [187, 114, 78, 48], 'M': [149, 90, 62, 38], 'Q': [111, 67, 46, 28], 'H': [82, 50, 34, 21] },
    { 'L': [255, 154, 106, 65], 'M': [202, 122, 84, 52], 'Q': [144, 87, 60, 37], 'H': [106, 64, 44, 27] },
    { 'L': [322, 195, 134, 82], 'M': [255, 154, 106, 65], 'Q': [178, 108, 74, 45], 'H': [139, 84, 58, 36] },
    { 'L': [370, 224, 154, 95], 'M': [293, 178, 122, 75], 'Q': [207, 125, 86, 53], 'H': [154, 93, 64, 39] },
    { 'L': [461, 279, 192, 118], 'M': [365, 221, 152, 93], 'Q': [259, 157, 108, 66], 'H': [202, 122, 84, 52] },
    { 'L': [552, 335, 230, 141], 'M': [432, 262, 180, 111], 'Q': [312, 189, 130, 80], 'H': [235, 143, 98, 60] },
    { 'L': [652, 395, 271, 167], 'M': [513, 311, 213, 131], 'Q': [364, 221, 151, 93], 'H': [288, 174, 119, 74] },
    { 'L': [772, 468, 321, 198], 'M': [604, 366, 251, 155], 'Q': [427, 259, 177, 109], 'H': [331, 200, 137, 85] },
    { 'L': [883, 535, 367, 226], 'M': [691, 419, 287, 177], 'Q': [489, 296, 203, 125], 'H': [374, 227, 155, 96] },
    { 'L': [1022, 619, 425, 262], 'M': [796, 483, 331, 204], 'Q': [580, 352, 241, 149], 'H': [427, 259, 177, 109] },
    { 'L': [1101, 667, 458, 282], 'M': [871, 528, 362, 223], 'Q': [621, 376, 258, 159], 'H': [468, 283, 194, 120] },
    { 'L': [1250, 758, 520, 320], 'M': [991, 600, 412, 254], 'Q': [703, 426, 292, 180], 'H': [530, 321, 220, 136] },
    { 'L': [1408, 854, 586, 361], 'M': [1082, 656, 450, 277], 'Q': [775, 470, 322, 198], 'H': [602, 365, 250, 154] },
    { 'L': [1548, 938, 644, 397], 'M': [1212, 734, 504, 310], 'Q': [876, 531, 364, 224], 'H': [674, 408, 280, 173] },
    { 'L': [1725, 1046, 718, 442], 'M': [1346, 816, 560, 345], 'Q': [948, 574, 394, 243], 'H': [746, 452, 310, 191] },
    { 'L': [1903, 1153, 792, 488], 'M': [1500, 909, 624, 384], 'Q': [1063, 644, 442, 272], 'H': [813, 493, 338, 208] },
    { 'L': [2061, 1249, 858, 528], 'M': [1600, 970, 666, 410], 'Q': [1159, 702, 482, 297], 'H': [919, 557, 382, 235] },
    { 'L': [2232, 1352, 929, 572], 'M': [1708, 1035, 711, 438], 'Q': [1224, 742, 509, 314], 'H': [969, 587, 403, 248] },
    { 'L': [2409, 1460, 1003, 618], 'M': [1872, 1134, 779, 480], 'Q': [1358, 823, 565, 348], 'H': [1056, 640, 439, 270] },
    { 'L': [2620, 1588, 1091, 672], 'M': [2059, 1248, 857, 528], 'Q': [1468, 890, 611, 376], 'H': [1108, 672, 461, 284] },
    { 'L': [2812, 1704, 1171, 721], 'M': [2188, 1326, 911, 561], 'Q': [1588, 963, 661, 407], 'H': [1228, 744, 511, 315] },
    { 'L': [3057, 1853, 1273, 784], 'M': [2395, 1451, 997, 614], 'Q': [1718, 1041, 715, 440], 'H': [1286, 779, 535, 330] },
    { 'L': [3283, 1990, 1367, 842], 'M': [2544, 1542, 1059, 652], 'Q': [1804, 1094, 751, 462], 'H': [1425, 864, 593, 365] },
    { 'L': [3517, 2132, 1465, 902], 'M': [2701, 1637, 1125, 692], 'Q': [1933, 1172, 805, 496], 'H': [1501, 910, 625, 385] },
    { 'L': [3669, 2223, 1528, 940], 'M': [2857, 1732, 1190, 732], 'Q': [2085, 1263, 868, 534], 'H': [1581, 958, 658, 405] },
    { 'L': [3909, 2369, 1628, 1002], 'M': [3035, 1839, 1264, 778], 'Q': [2181, 1322, 908, 559], 'H': [1677, 1016, 698, 430] },
    { 'L': [4158, 2520, 1732, 1066], 'M': [3289, 1994, 1370, 843], 'Q': [2358, 1429, 982, 604], 'H': [1782, 1080, 742, 457] },
    { 'L': [4417, 2677, 1840, 1132], 'M': [3486, 2113, 1452, 894], 'Q': [2473, 1499, 1030, 634], 'H': [1897, 1150, 790, 486] },
    { 'L': [4686, 2840, 1952, 1201], 'M': [3693, 2238, 1538, 947], 'Q': [2670, 1618, 1112, 684], 'H': [2022, 1226, 842, 518] },
    { 'L': [4965, 3009, 2068, 1273], 'M': [3909, 2369, 1628, 1002], 'Q': [2805, 1700, 1168, 719], 'H': [2157, 1307, 898, 553] },
    { 'L': [5253, 3183, 2188, 1347], 'M': [4134, 2506, 1722, 1060], 'Q': [2949, 1787, 1228, 756], 'H': [2301, 1394, 958, 590] },
    { 'L': [5529, 3351, 2303, 1417], 'M': [4343, 2632, 1809, 1113], 'Q': [3081, 1867, 1283, 790], 'H': [2361, 1431, 983, 605] },
    { 'L': [5836, 3537, 2431, 1496], 'M': [4588, 2780, 1911, 1176], 'Q': [3244, 1966, 1351, 832], 'H': [2524, 1530, 1051, 647] },
    { 'L': [6153, 3729, 2563, 1577], 'M': [4775, 2894, 1989, 1224], 'Q': [3417, 2071, 1423, 876], 'H': [2625, 1591, 1093, 673] },
    { 'L': [6479, 3927, 2699, 1661], 'M': [5039, 3054, 2099, 1292], 'Q': [3599, 2181, 1499, 923], 'H': [2735, 1658, 1139, 701] },
    { 'L': [6743, 4087, 2809, 1729], 'M': [5313, 3220, 2213, 1362], 'Q': [3791, 2298, 1579, 972], 'H': [2927, 1774, 1219, 750] },
    { 'L': [7089, 4296, 2953, 1817], 'M': [5596, 3391, 2331, 1435], 'Q': [3993, 2420, 1663, 1024], 'H': [3057, 1852, 1273, 784] }
]

DATA_CODEWORDS = [
    {'L': 19, 'M': 16, 'Q': 13, 'H': 9},
    {'L': 34, 'M': 28, 'Q': 22, 'H': 16},
    {'L': 55, 'M': 44, 'Q': 34, 'H': 26},
    {'L': 80, 'M': 64, 'Q': 48, 'H': 36},
    {'L': 108, 'M': 86, 'Q': 62, 'H': 46},
    {'L': 136, 'M': 108, 'Q': 76, 'H': 60},
    {'L': 156, 'M': 124, 'Q': 88, 'H': 66},
    {'L': 194, 'M': 154, 'Q': 110, 'H': 86},
    {'L': 232, 'M': 182, 'Q': 132, 'H': 100},
    {'L': 274, 'M': 216, 'Q': 154, 'H': 122},
    {'L': 324, 'M': 254, 'Q': 180, 'H': 140},
    {'L': 370, 'M': 290, 'Q': 206, 'H': 158},
    {'L': 428, 'M': 334, 'Q': 244, 'H': 180},
    {'L': 461, 'M': 365, 'Q': 261, 'H': 197},
    {'L': 523, 'M': 415, 'Q': 295, 'H': 223},
    {'L': 589, 'M': 453, 'Q': 325, 'H': 253},
    {'L': 647, 'M': 507, 'Q': 367, 'H': 283},
    {'L': 721, 'M': 563, 'Q': 397, 'H': 313},
    {'L': 795, 'M': 627, 'Q': 445, 'H': 341},
    {'L': 861, 'M': 669, 'Q': 485, 'H': 385},
    {'L': 932, 'M': 714, 'Q': 512, 'H': 406},
    {'L': 1006, 'M': 782, 'Q': 568, 'H': 442},
    {'L': 1094, 'M': 860, 'Q': 614, 'H': 464},
    {'L': 1174, 'M': 914, 'Q': 664, 'H': 514},
    {'L': 1276, 'M': 1000, 'Q': 718, 'H': 538},
    {'L': 1370, 'M': 1062, 'Q': 754, 'H': 596},
    {'L': 1468, 'M': 1128, 'Q': 808, 'H': 628},
    {'L': 1531, 'M': 1193, 'Q': 871, 'H': 661},
    {'L': 1631, 'M': 1267, 'Q': 911, 'H': 701},
    {'L': 1735, 'M': 1373, 'Q': 985, 'H': 745},
    {'L': 1843, 'M': 1455, 'Q': 1033, 'H': 793},
    {'L': 1955, 'M': 1541, 'Q': 1115, 'H': 845},
    {'L': 2071, 'M': 1631, 'Q': 1171, 'H': 901},
    {'L': 2191, 'M': 1725, 'Q': 1231, 'H': 961},
    {'L': 2306, 'M': 1812, 'Q': 1286, 'H': 986},
    {'L': 2434, 'M': 1914, 'Q': 1354, 'H': 1054},
    {'L': 2566, 'M': 1992, 'Q': 1426, 'H': 1096},
    {'L': 2702, 'M': 2102, 'Q': 1502, 'H': 1142},
    {'L': 2812, 'M': 2216, 'Q': 1582, 'H': 1222},
    {'L': 2956, 'M': 2334, 'Q': 1666, 'H': 1276}
]

EC_TABLE = {
    'L': {
        1: {"group1": (1, 19), "group2": None},
        2: {"group1": (1, 34), "group2": None},
        3: {"group1": (1, 55), "group2": None},
        4: {"group1": (1, 80), "group2": None},
        5: {"group1": (1, 108), "group2": None},
        6: {"group1": (2, 68), "group2": None},
        7: {"group1": (2, 78), "group2": None},
        8: {"group1": (2, 97), "group2": None},
        9: {"group1": (2, 116), "group2": None},
        10: {"group1": (2, 68), "group2": (2, 69)},
        11: {"group1": (4, 81), "group2": None},
        12: {"group1": (2, 92), "group2": (2, 93)},
        13: {"group1": (4, 107), "group2": None},
        14: {"group1": (3, 115), "group2": (1, 116)},
        15: {"group1": (5, 87), "group2": (1, 88)},
        16: {"group1": (5, 98), "group2": (1, 99)},
        17: {"group1": (1, 107), "group2": (5, 108)},
        18: {"group1": (5, 120), "group2": (1, 121)},
        19: {"group1": (3, 113), "group2": (4, 114)},
        20: {"group1": (3, 107), "group2": (5, 108)},
        21: {"group1": (4, 116), "group2": (4, 117)},
        22: {"group1": (2, 111), "group2": (7, 112)},
        23: {"group1": (4, 121), "group2": (5, 122)},
        24: {"group1": (6, 117), "group2": (4, 118)},
        25: {"group1": (8, 106), "group2": (4, 107)},
        26: {"group1": (10, 114), "group2": (2, 115)},
        27: {"group1": (8, 122), "group2": (4, 123)},
        28: {"group1": (3, 117), "group2": (10, 118)},
        29: {"group1": (7, 116), "group2": (7, 117)},
        30: {"group1": (5, 115), "group2": (10, 116)},
        31: {"group1": (13, 115), "group2": (3, 116)},
        32: {"group1": (17, 115), "group2": None},
        33: {"group1": (17, 115), "group2": (1, 116)},
        34: {"group1": (16, 115), "group2": (28, 116)},
        35: {"group1": (12, 121), "group2": (7, 122)},
        36: {"group1": (6, 121), "group2": (14, 122)},
        37: {"group1": (17, 122), "group2": (4, 123)},
        38: {"group1": (4, 122), "group2": (18, 123)},
        39: {"group1": (20, 117), "group2": (4, 118)},
        40: {"group1": (19, 118), "group2": (6, 119)}
    },
    'M': {
        1: {"group1": (1, 16), "group2": None},
        2: {"group1": (1, 28), "group2": None},
        3: {"group1": (1, 44), "group2": None},
        4: {"group1": (2, 32), "group2": None},
        5:  {"group1": (2, 43), "group2": None},
        6:  {"group1": (4, 27), "group2": None},
        7: {"group1": (4, 31), "group2": None},
        8:  {"group1": (2, 38), "group2": (2, 39)},
        9:  {"group1": (3, 36), "group2": (2, 37)},
        10: {"group1": (4, 43), "group2": (1, 44)},
        11: {"group1": (1, 50), "group2": (4, 51)},
        12: {"group1": (6, 36), "group2": (2, 37)},
        13: {"group1": (8, 37), "group2": (1, 38)},
        14: {"group1": (4, 40), "group2": (5, 41)},
        15: {"group1": (5, 41), "group2": (5, 42)},
        16: {"group1": (7, 45), "group2": (3, 46)},
        17: {"group1": (10, 46), "group2": (1, 47)},
        18: {"group1": (9, 43), "group2": (4, 44)},
        19: {"group1": (3, 44), "group2": (11, 45)},
        20: {"group1": (3, 41), "group2": (13, 42)},
        21: {"group1": (17, 42), "group2": None},
        22: {"group1": (17, 46), "group2": None},
        23: {"group1": (4, 47), "group2": (14, 48)},
        24: {"group1": (6, 45), "group2": (14, 46)},
        25: {"group1": (8, 47), "group2": (13, 48)},
        26: {"group1": (19, 46), "group2": (4, 47)},
        27: {"group1": (22, 45), "group2": (3, 46)},
        28: {"group1": (3, 45), "group2": (23, 46)},
        29: {"group1": (21, 45), "group2": (7, 46)},
        30: {"group1": (19, 47), "group2": (10, 48)},
        31: {"group1": (2, 46), "group2": (29, 47)},
        32: {"group1": (10, 46), "group2": (23, 47)},
        33: {"group1": (14, 46), "group2": (21, 47)},
        34: {"group1": (14, 46), "group2": (23, 47)},
        35: {"group1": (12, 47), "group2": (26, 48)},
        36: {"group1": (6, 47), "group2": (34, 48)},
        37: {"group1": (29, 46), "group2": (14, 47)},
        38: {"group1": (13, 46), "group2": (32, 47)},
        39: {"group1": (40, 47), "group2": (7, 48)},
        40: {"group1": (18, 47), "group2": (31, 48)}
    },
    'Q': {
        1: {"group1": (1, 13), "group2": None},
        2: {"group1": (1, 22), "group2": None},
        3: {"group1": (2, 17), "group2": None},
        4: {"group1": (2, 24), "group2": None},
        5: {"group1": (2, 15), "group2": (2, 16)},
        6: {"group1": (4, 19), "group2": None},
        7: {"group1": (2, 14), "group2": (4, 15)},
        8: {"group1": (4, 18), "group2": (2, 19)},
        9: {"group1": (4, 16), "group2": (4, 17)},
        10: {"group1": (6, 19), "group2": (2, 20)},
        11: {"group1": (4, 22), "group2": (4, 23)},
        12: {"group1": (4, 20), "group2": (6, 21)},
        13: {"group1": (8, 20), "group2": (4, 21)},
        14: {"group1": (11, 16), "group2": (5, 17)},
        15: {"group1": (5, 24), "group2": (7, 25)},
        16: {"group1": (15, 19), "group2": (2, 20)},
        17: {"group1": (1, 22), "group2": (15, 23)},
        18: {"group1": (17, 22), "group2": (1, 23)},
        19: {"group1": (17, 21), "group2": (4, 22)},
        20: {"group1": (15, 24), "group2": (5, 25)},
        21: {"group1": (17, 22), "group2": (6, 23)},
        22: {"group1": (7, 24), "group2": (16, 25)},
        23: {"group1": (11, 24), "group2": (14, 25)},
        24: {"group1": (11, 24), "group2": (16, 25)},
        25: {"group1": (7, 24), "group2": (22, 25)},
        26: {"group1": (28, 22), "group2": (6, 23)},
        27: {"group1": (8, 23), "group2": (26, 24)},
        28: {"group1": (4, 24), "group2": (31, 25)},
        29: {"group1": (1, 23), "group2": (37, 24)},
        30: {"group1": (15, 24), "group2": (25, 25)},
        31: {"group1": (42, 24), "group2": (1, 25)},
        32: {"group1": (10, 24), "group2": (35, 25)},
        33: {"group1": (29, 24), "group2": (19, 25)},
        34: {"group1": (44, 24), "group2": (7, 25)},
        35: {"group1": (39, 24), "group2": (14, 25)},
        36: {"group1": (46, 24), "group2": (10, 25)},
        37: {"group1": (49, 24), "group2": (10, 25)},
        38: {"group1": (48, 24), "group2": (14, 25)},
        39: {"group1": (43, 24), "group2": (22, 25)},
        40: {"group1": (34, 24), "group2": (34, 25)}
    },
    'H': {
        1: {"group1": (1, 9), "group2": None},
        2: {"group1": (1, 16), "group2": None},
        3: {"group1": (2, 13), "group2": None},
        4: {"group1": (4, 9), "group2": None},
        5: {"group1": (2, 11), "group2": (2, 12)},
        6: {"group1": (4, 15), "group2": None},
        7: {"group1": (4, 13), "group2": (1, 14)},
        8: {"group1": (4, 14), "group2": (2, 15)},
        9: {"group1": (4, 12), "group2": (4, 13)},
        10: {"group1": (6, 15), "group2": (2, 16)},
        11: {"group1": (3, 12), "group2": (8, 13)},
        12: {"group1": (7, 14), "group2": (4, 15)},
        13: {"group1": (12, 11), "group2": (4, 12)},
        14: {"group1": (11, 12), "group2": (5, 13)},
        15: {"group1": (11, 12), "group2": (7, 13)},
        16: {"group1": (3, 15), "group2": (13, 16)},
        17: {"group1": (2, 14), "group2": (17, 15)},
        18: {"group1": (2, 14), "group2": (19, 15)},
        19: {"group1": (9, 13), "group2": (16, 14)},
        20: {"group1": (15, 15), "group2": (10, 16)},
        21: {"group1": (19, 16), "group2": (6, 17)},
        22: {"group1": (34, 13), "group2": None},
        23: {"group1": (16, 15), "group2": (14, 16)},
        24: {"group1": (30, 16), "group2": (2, 17)},
        25: {"group1": (22, 15), "group2": (13, 16)},
        26: {"group1": (33, 16), "group2": (4, 17)},
        27: {"group1": (12, 15), "group2": (28, 16)},
        28: {"group1": (11, 15), "group2": (31, 16)},
        29: {"group1": (19, 15), "group2": (26, 16)},
        30: {"group1": (23, 15), "group2": (25, 16)},
        31: {"group1": (23, 15), "group2": (28, 16)},
        32: {"group1": (19, 15), "group2": (35, 16)},
        33: {"group1": (11, 15), "group2": (46, 16)},
        34: {"group1": (59, 16), "group2": (1, 17)},
        35: {"group1": (22, 15), "group2": (41, 16)},
        36: {"group1": (2, 15), "group2": (64, 16)},
        37: {"group1": (24, 15), "group2": (46, 16)},
        38: {"group1": (42, 15), "group2": (32, 16)},
        39: {"group1": (10, 15), "group2": (67, 16)},
        40: {"group1": (20, 15), "group2": (61, 16)}
    }
}

GALOIS_LOG = [
    0, 0, 1, 25, 2, 50, 26, 198, 3, 223, 51, 238, 27, 104, 199, 75, 4, 100, 224, 14, 52, 141, 239, 129, 28, 193, 105,
    248, 200, 8, 76, 113, 5, 138, 101, 47, 225, 36, 15, 33, 53, 147, 142, 218, 240, 18, 130, 69, 29, 181, 194, 125, 106, 39, 249,
    185, 201, 154, 9, 120, 77, 228, 114, 166, 6, 191, 139, 98, 102, 221, 48, 253, 226, 152, 37, 179, 16, 145, 34, 136, 54, 208, 148,
    206, 143, 150, 219, 189, 241, 210, 19, 92, 131, 56, 70, 64, 30, 66, 182, 163, 195, 72, 126, 110, 107, 58, 40, 84, 250, 133, 186, 61,
    202, 94, 155, 159, 10, 21, 121, 43, 78, 212, 229, 172, 115, 243, 167, 87, 7, 112, 192, 247, 140, 128, 99, 13, 103, 74, 222, 237, 49,
    197, 254, 24, 227, 165, 153, 119, 38, 184, 180, 124, 17, 68, 146, 217, 35, 32, 137, 46, 55, 63, 209, 91, 149, 188, 207, 205, 144, 135,
    151, 178, 220, 252, 190, 97, 242, 86, 211, 171, 20, 42, 93, 158, 132, 60, 57, 83, 71, 109, 65, 162, 31, 45, 67, 216, 183, 123, 164, 118,
    196, 23, 73, 236, 127, 12, 111, 246, 108, 161, 59, 82, 41, 157, 85, 170, 251, 96, 134, 177, 187, 204, 62, 90, 203, 89, 95, 176, 156, 169,
    160, 81, 11, 245, 22, 235, 122, 117, 44, 215, 79, 174, 213, 233, 230, 231, 173, 232, 116, 214, 244, 234, 168, 80, 88, 175
]

GALOIS_ANTILOG = [
    1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96,
    192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210,
    185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127,
    254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248,
    237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77,
    154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246,
    241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112,
    224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245,
    247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1
]

GENERATOR_POLYNOMIALS = {
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

EC_CODEWORDS = [
    {'L': 7, 'M': 10, 'Q': 13, 'H': 17},
    {'L': 10, 'M': 16, 'Q': 22, 'H': 28},
    {'L': 15, 'M': 26, 'Q': 18, 'H': 22},
    {'L': 20, 'M': 18, 'Q': 26, 'H': 16},
    {'L': 26, 'M': 24, 'Q': 18, 'H': 22},
    {'L': 18, 'M': 16, 'Q': 24, 'H': 28},
    {'L': 20, 'M': 18, 'Q': 18, 'H': 26},
    {'L': 24, 'M': 22, 'Q': 22, 'H': 26},
    {'L': 30, 'M': 22, 'Q': 20, 'H': 24},
    {'L': 18, 'M': 26, 'Q': 24, 'H': 28},
    {'L': 20, 'M': 30, 'Q': 28, 'H': 24},
    {'L': 24, 'M': 22, 'Q': 26, 'H': 28},
    {'L': 26, 'M': 22, 'Q': 24, 'H': 22},
    {'L': 30, 'M': 24, 'Q': 20, 'H': 24},
    {'L': 22, 'M': 24, 'Q': 30, 'H': 24},
    {'L': 24, 'M': 28, 'Q': 24, 'H': 30},
    {'L': 28, 'M': 28, 'Q': 28, 'H': 28},
    {'L': 30, 'M': 26, 'Q': 28, 'H': 28},
    {'L': 28, 'M': 26, 'Q': 26, 'H': 26},
    {'L': 28, 'M': 26, 'Q': 30, 'H': 28},
    {'L': 28, 'M': 26, 'Q': 28, 'H': 30},
    {'L': 28, 'M': 28, 'Q': 30, 'H': 24},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 26, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 28, 'M': 28, 'Q': 28, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30},
    {'L': 30, 'M': 28, 'Q': 30, 'H': 30}
]

ALIGNMENT_PATTERN_LOCATIONS = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
}

FORMAT_INFORMATION = {
    'L': [
        '111011111000100', '111001011110011', '111110110101010', '111100010011101',
        '110011000101111', '110001100011000', '110110001000001', '110100101110110'
    ],
    'M': [
        '101010000010010', '101000100100101', '101111001111100', '101101101001011',
        '100010111111001', '100000011001110', '100111110010111', '100101010100000'
    ],
    'Q': [
        '011010101011111', '011000001101000', '011111100110001', '011101000000110',
        '010010010110100', '010000110000011', '010111011011010', '010101111101101'
    ],
    'H': [
        '001011010001001', '001001110111110', '001110011100111', '001100111010000',
        '000011101100010', '000001001010101', '000110100001100', '000100000111011'
    ]
}

def get_data_type(data):
    if data.isdecimal():  # If the data is numeric (only digits)
        return NUMERIC

    # If the data contains only alphanumeric characters (found in alphanumeric set)
    if all(char in ALPHANUMERIC_CHARS for char in data):
        return ALPHANUMERIC

    try:
        encoded_data = data.encode("shift_jis")

        # If the encoded data length is not even, it's not valid Kanji encoding
        if len(encoded_data) % 2 != 0:
            return BYTE

        # Loop through the encoded data, checking for valid Kanji byte pairs
        for i in range(0, len(encoded_data), 2):
            byte1, byte2 = encoded_data[i], encoded_data[i + 1]
            val = (byte1 << 8) | byte2  # Combine two bytes into a single value

            # Check if the value is within the valid Kanji ranges
            if not (0x8140 <= val <= 0x9FFC or 0xE040 <= val <= 0xEBBF):
                return BYTE  # If not, treat it as raw byte data

        return KANJI  # If all values are valid Kanji, return KANJI type
    except:
        return BYTE  # In case of an error, treat it as raw byte data

# Function to determine the appropriate QR version and error correction level for the data
def get_version_and_ec_level(data, encode_type, ec_level=''):
    # List of valid error correction levels:
    # L - Low: 7% of data can be restored
    # M - Medium: 15% of data can be restored
    # Q - Quarter: 25% of data can be restored
    # H - High: 30% of data can be restored
    VALID_EC_LEVELS = "HQML"

    # If an invalid error correction level is provided, return an error message
    if ec_level and ec_level not in VALID_EC_LEVELS:
        return "Invalid error correction level provided"

    # Calculate the length of the data
    if encode_type == BYTE:
        data_length = len(encode_byte(data)) // 8
    else:
        data_length = len(data)

    # If an error correction level is specified, check if the data fits within that level's capacity
    if ec_level:
        for version, capacities in enumerate(CHARACTER_CAPACITY_TABLE):
            if capacities[ec_level][encode_type] >= data_length:
                return version + 1, ec_level
        return "Cannot fit data with the specified error correction level"

    # If no error correction level is provided, try all valid levels, from highest to lowest
    for ec_level in VALID_EC_LEVELS:
        for version, capacities in enumerate(CHARACTER_CAPACITY_TABLE):
            if capacities[ec_level][encode_type] >= data_length:
                return version + 1, ec_level

    return "Cannot fit data into a QR Code"  # If no valid combination is found

# Function to encode numeric data (groups of 3 digits)
def encode_numeric(data):
    number_groups = []

    # Split data into groups of 3 digits
    while len(data) > 3:
        number_groups.append(data[:3])
        data = data[3:]

    if data:
        number_groups.append(data)  # Append remaining digits if any

    encoded_data = []

    # Encode each group of digits
    for group in number_groups:
        num = int(group)

        # Format the number as binary, with different bit lengths based on group size
        if len(group) == 3:
            encoded_data.append(format(num, '010b'))
        elif len(group) == 2:
            encoded_data.append(format(num, '07b'))
        elif len(group) == 1:
            encoded_data.append(format(num, '04b'))

    return ''.join(encoded_data)

def encode_alphanumeric(data):
    string_pairs = []

    # Split data into pairs of characters
    while len(data) > 1:
        string_pairs.append(data[:2])
        data = data[2:]

    if data:
        string_pairs.append(data)  # Append remaining character if any

    encoded_data = []
    alphanumeric_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

    # Encode each pair of characters
    for pair in string_pairs:
        if len(pair) == 2:
            value = alphanumeric_chars.index(pair[0]) * 45 + alphanumeric_chars.index(pair[1])
            encoded_data.append(format(value, '011b'))
        else:
            value = alphanumeric_chars.index(pair[0])
            encoded_data.append(format(value, '06b'))

    return ''.join(encoded_data)

def encode_byte(data):
    try:
        # Try to encode using ISO-8859-1 encoding
        encoded_data = data.encode('ISO-8859-1')
    except:
        # If it fails, fall back to UTF-8 encoding (some QR code readers may not support it)
        encoded_data = data.encode('UTF-8')

    return ''.join(format(byte, '08b') for byte in encoded_data)

# Function to encode Kanji characters (shift-JIS encoding)
def encode_kanji(data):
    encoded_shift_jis = data.encode('shift-jis')

    encoded_data = []

    i = 0
    while i < len(encoded_shift_jis):
        byte1 = encoded_shift_jis[i]
        byte2 = encoded_shift_jis[i + 1]
        shift_jis_value = (byte1 << 8) | byte2  # Combine two bytes into a single value

        # Adjust the value based on Kanji ranges
        if 0x8140 <= shift_jis_value <= 0x9FFC:
            adjusted = shift_jis_value - 0x8140
        else:
            adjusted = shift_jis_value - 0xC140

        # Convert the value to 13-bit binary and append it
        most_significant_byte = (adjusted >> 8) & 0xFF
        least_significant_byte = adjusted & 0xFF
        final_value = most_significant_byte * 0xC0 + least_significant_byte

        encoded_data.append(format(final_value, '013b'))

        i += 2

    return ''.join(encoded_data)

def encode_data(data, version, encode_type, ec_level):
    mode_indicator = format(1 << encode_type, '04b')  # Mode indicator

    # Set character count size based on QR Code version and encoding type
    if version < 10:
        character_count_size = ['010b', '09b', '08b', '08b']
    elif version < 27:
        character_count_size = ['012b', '011b', '016b', '010b']
    else:
        character_count_size = ['014b', '013b', '016b', '012b']

    # Format the length of the data according to the encoding type
    character_count = format(len(data), character_count_size[encode_type])

    required_bits = DATA_CODEWORDS[version - 1][ec_level] * 8  # Total available bits for data

    # Encode the data based on its type
    if encode_type == NUMERIC:
        encoded_data = encode_numeric(data)
    elif encode_type == ALPHANUMERIC:
        encoded_data = encode_alphanumeric(data)
    elif encode_type == BYTE:
        encoded_data = encode_byte(data)
        character_count = format(len(encoded_data) // 8, character_count_size[encode_type])
    else:
        encoded_data = encode_kanji(data)

    # Concatenate all parts to form the QR Code data
    concatenated_string = mode_indicator + character_count + encoded_data

    # Add padding bits
    bits_left = required_bits - len(concatenated_string)

    if bits_left >= 4:
        concatenated_string += '0000'
    else:
        concatenated_string += '0' * bits_left

    concatenated_string += '0' * ((8 - len(concatenated_string) % 8) % 8)  # Ensure byte alignment

    # Add pad bytes to meet the size requirement
    bytes_left = (required_bits - len(concatenated_string)) // 8
    pad_bytes = ['11101100', '00010001']
    for i in range(bytes_left):
        concatenated_string += pad_bytes[i % 2]

    return concatenated_string

def split_data(data_codewords, version, ec_level):
    config = EC_TABLE[ec_level][version]  # Look up the error correction configuration for this version and level
    group1 = config["group1"]
    group2 = config["group2"]

    groups = []
    blocks = []
    index = 0

    # Split data into blocks for group 1
    for _ in range(group1[0]):
        block_size = group1[1]
        blocks.append(data_codewords[index:index + block_size])
        index += block_size

    groups.append(blocks)

    # If group 2 exists, process its data blocks
    if group2:
        blocks = []
        for _ in range(group2[0]):
            block_size = group2[1]
            blocks.append(data_codewords[index:index + block_size])
            index += block_size
        groups.append(blocks)

    return groups

def get_ecc(dividend, codewords):
    # Perform multiplication in Galois field
    def galois_multiplication(x, y):
        if x == 0:
            return 0
        return GALOIS_ANTILOG[(GALOIS_LOG[x] + GALOIS_LOG[y]) % 255]  # Use logarithmic table for multiplication

    dividend.extend([0] * codewords)

    divisor = GENERATOR_POLYNOMIALS[codewords]

    # Perform polynomial division
    msg_out = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = msg_out[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                msg_out[i + j] ^= galois_multiplication(divisor[j], coef)

    return msg_out[-(len(divisor) - 1):]  # Return the remainder, wich is the error correction code (ECC)

def structure_final_message(encoded_data, version, ec_level):
    codewords = [int(encoded_data[i:i+8], 2) for i in range(0, len(encoded_data), 8)]  # Convert binary string to codewords

    groups = split_data(codewords, version, ec_level)  # Split the data into blocks

    ecc_count = EC_CODEWORDS[version - 1][ec_level]  # Get the number of ECC codewords for this version and level

    ecc_blocks = []
    for group in groups:
        for block in group:
            ecc = get_ecc(list(block), ecc_count)  # Generate ECC for this block
            ecc_blocks.append(ecc)  # Add the ECC to the list

    final_message = []  # Final message after combining data and ECC
    max_len = max(len(block) for group in groups for block in group)  # Find the maximum block length

    # Add the data codewords in a specific pattern
    for i in range(max_len):
        for group in groups:
            for block in group:
                if i < len(block):
                    final_message.append(format(block[i], '08b'))  # Add each codeword in binary format

    # Add ECC codewords to the final message
    for i in range(ecc_count):
        for ecc in ecc_blocks:
            final_message.append(format(ecc[i], '08b'))

    # Add remainder bits (used for padding)
    remainder_bits = [0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3,
                      4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0]
    
    final_message.extend(['0'] * remainder_bits[version - 1])

    return ''.join(final_message)

def place_finder_patterns(matrix, size):
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

def place_separators(matrix, size):
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

def place_alignment_patterns(matrix, version):
    # Returns early since version 1 doesn't have alignment patterns
    if version == 1:
        return

    # Get alignment pattern locations for the given QR code version
    locations = ALIGNMENT_PATTERN_LOCATIONS[version]

    for row in locations:
        for column in locations:
            # Check if it is a valid place for an alignment pattern
            if (matrix[row - 2][column - 2] != -1 or matrix[row - 2][column + 2] != -1 or
                matrix[row + 2][column - 2] != -1 or matrix[row + 2][column + 2] != -1):
                continue

            # Add the alignment pattern
            for i in range(row - 2, row + 3):
                for j in range(column - 2, column + 3):
                    if i == row - 2 or i == row + 2 or j == column - 2 or j == column + 2:
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0
            matrix[row][column] = 1

def place_timing_patterns(matrix, size):
    # Place timing patterns along row 6 and column 6
    for i in range(8, size - 8):
        matrix[6][i] = 1 - i % 2
        matrix[i][6] = 1 - i % 2

def define_reserverd_areas(matrix, size):
    # Add top-left reserved area
    for j in range(9):
        matrix[8][j] = 0
        matrix[j][8] = 0

    # Place back the black modules that got overwritten by the top-left reserved area
    matrix[8][6] = 1
    matrix[6][8] = 1

    # Add bottom-left and top-right reserved areas
    for i in range(size - 8, size):
        matrix[i][8] = 0
        matrix[8][i] = 0

    # Add dark module
    matrix[size - 8][8] = 1

    # Add reserved version information area (for version 7 and above)
    if size >= 45:
        for i in range(size - 11, size - 8):
            for j in range(6):
                matrix[i][j] = 0
                matrix[j][i] = 0

def place_matrix_modules(data, version):
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

    # Populate the matrix with the data and error correction bits in the specified zig-zag pattern
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

def apply_masks(matrix, size):
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

def evaluate_first_penalty(matrix, size):
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

def evaluate_second_penalty(matrix, size):
    penalty = 0

    for i in range(size - 1):
        for j in range(size - 1):
            if matrix[i][j] == matrix[i + 1][j] == matrix[i][j + 1] == matrix[i + 1][j + 1]:
                penalty += 3

    return penalty

# Add a 4-module border around the QR Code
def add_quiet_zone(matrix):
    size = len(matrix)

    final_matrix = [[0] * (size + 8) for _ in range(size + 8)]

    for i in range(size):
        for j in range(size):
            final_matrix[i + 4][j + 4] = matrix[i][j]

    return final_matrix

def evaluate_third_penalty(matrix):
    penalty = 0

    bad_patterns = ['10111010000', '00001011101']
    full_matrix = add_quiet_zone(matrix)
    size = len(full_matrix)

    for i in range(size):
        for j in range(size - 10):
            horizontal_segment = ''.join(map(str, full_matrix[i][j:j + 11]))
            if horizontal_segment in bad_patterns:
                penalty += 40

            vertical_segment = ''.join(str(full_matrix[j + k][i]) for k in range(11))
            if vertical_segment in bad_patterns:
                penalty += 40

    return penalty

def evaluate_fourth_penalty(matrix, size):
    total_modules = size * size
    dark_modules_count = sum(row.count(1) for row in matrix)

    dark_modules_percentage = int(dark_modules_count / total_modules * 100)

    previous_multiple_of_five = (dark_modules_percentage // 5) * 5
    next_multiple_of_five = previous_multiple_of_five + 5

    return min(abs(previous_multiple_of_five - 50) / 5, abs(next_multiple_of_five - 50) / 5) * 10

def determine_best_mask(masked_matrices, size):
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
        penalty += evaluate_third_penalty(masked_matrices[i])

        # The fourth rule gives the QR code a penalty if more than half of the modules are dark or light, with a larger penalty for a larger difference.
        penalty += evaluate_fourth_penalty(masked_matrices[i], size)

        if penalty < lowest_penalty:
            lowest_penalty = penalty
            lowest_penalty_index = i

    # Chooses the one with the lowest penalty score
    return lowest_penalty_index

def get_version_string(version):
    version_information_strings = [
        '000111110010010100', '001000010110111100', '001001101010011001', '001010010011010011',
        '001011101111110110', '001100011101100010', '001101100001000111', '001110011000001101',
        '001111100100101000', '010000101101111000', '010001010001011101', '010010101000010111',
        '010011010100110010', '010100100110100110', '010101011010000011', '010110100011001001',
        '010111011111101100', '011000111011000100', '011001000111100001', '011010111110101011',
        '011011000010001110', '011100110000011010', '011101001100111111', '011110110101110101',
        '011111001001010000', '100000100111010101', '100001011011110000', '100010100010111010',
        '100011011110011111', '100100101100001011', '100101010000101110', '100110101001100100',
        '100111010101000001','101000110001101001'
    ]

    return version_information_strings[version - 7]

def place_format_string(matrix, format_string, size):
    tracker = 0

    # Fill top-left reserved area
    for i in range(9):
        if i == 6:
            continue

        matrix[8][i] = int(format_string[tracker])
        matrix[i][8] = int(format_string[14 - tracker])
        tracker += 1

    tracker -= 1

    # Fill bottom-left and top-right reserved areas
    for i in range(size - 8, size):
        matrix[i][8] = int(format_string[14 - tracker])
        matrix[8][i] = int(format_string[tracker])
        tracker += 1

    # Place back dark module
    matrix[size - 8][8] = 1

def place_version_string(matrix, version_string, size):
    tracker = 17

    # Fill reserved version information areas
    for i in range(6):
        for j in range(size - 11, size - 8):
            matrix[i][j] = int(version_string[tracker])
            matrix[j][i] = int(version_string[tracker])
            tracker -= 1

def fill_reserved_areas(matrix, version, format_string):
    size = version * 4 + 17

    place_format_string(matrix, format_string, size)

    # Add version string for QR Codes version 7 and above
    if version > 6:
        version_string = get_version_string(version)
        place_version_string(matrix, version_string, size)

def mask_data(matrix, version, ec_level):
    size = version * 4 + 17

    masked_matrices = apply_masks(matrix, size)

    for i in range(len(masked_matrices)):
        format_string = FORMAT_INFORMATION[ec_level][i]

        fill_reserved_areas(masked_matrices[i], version, format_string)

    lowest_penalty_index = determine_best_mask(masked_matrices, size)
    best_matrix = masked_matrices[lowest_penalty_index]

    return best_matrix, lowest_penalty_index

def draw_qr_code(matrix, module_size=10):
    size = len(matrix)

    img_size = size * module_size
    img = Image.new('L', (img_size, img_size), color=255)

    for i in range(size):
        for j in range(size):
            color = 0 if matrix[i][j] == 1 else 255
            for x in range(module_size):
                for y in range(module_size):
                    img.putpixel((j * module_size + x, i * module_size + y), color)

    return img

if __name__ == "__main__":

    data = 'Hello, world!'
    encode_type = get_data_type(data)
    version, ec_level = get_version_and_ec_level(data, encode_type)

    encoded_data = encode_data(data, version, encode_type, ec_level)

    message = structure_final_message(encoded_data, version, ec_level)

    matrix = place_matrix_modules(message, version)
    masked_matrix, mask = mask_data(matrix, version, ec_level)

    final_matrix = add_quiet_zone(masked_matrix)

    qr_code = draw_qr_code(final_matrix)
    qr_code.save('qr_code.png')
