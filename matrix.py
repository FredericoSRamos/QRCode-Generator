from typing import List, Union
from constants import ALIGNMENT_PATTERN_LOCATIONS, FORMAT_INFORMATION

class QRCodeMatrix:
    """
    Handles all graphics layout and matrix manipulation logic for generating a QR Code.
    """
    def __init__(self, version: int, ec_level: str):
        self.version = version
        self.ec_level = ec_level
        self.size = version * 4 + 17
        self.matrix: List[List[Union[int, str]]] = [[-1 for _ in range(self.size)] for _ in range(self.size)]

    def place_finder_patterns(self) -> None:
        size = self.size
        # Top-left finder pattern
        for i in range(7):
            for j in range(7):
                if i == 0 or i == 6 or j == 0 or j == 6:
                    self.matrix[i][j] = 1
                elif 2 <= i <= 4 and 2 <= j <= 4:
                    self.matrix[i][j] = 1
                else:
                    self.matrix[i][j] = 0

        # Top-right and bottom-left finder patterns
        start_limit = size - 7
        for i in range(start_limit, size):
            for j in range(7):
                if i == start_limit or i == size - 1 or j == 0 or j == 6:
                    self.matrix[i][j] = 1
                    self.matrix[j][i] = 1
                elif start_limit + 2 <= i <= start_limit + 4 and 2 <= j <= 4:
                    self.matrix[i][j] = 1
                    self.matrix[j][i] = 1
                else:
                    self.matrix[i][j] = 0
                    self.matrix[j][i] = 0

    def place_separators(self) -> None:
        size = self.size
        for i in range(8):
            self.matrix[7][i] = 0
            self.matrix[i][7] = 0

        for i in range(size - 8, size):
            self.matrix[7][i] = 0
            self.matrix[i][7] = 0

        i = size - 8
        for j in range(7):
            self.matrix[i][j] = 0
            self.matrix[j][i] = 0

    def place_alignment_patterns(self) -> None:
        if self.version == 1:
            return

        locations = ALIGNMENT_PATTERN_LOCATIONS[self.version]

        for row in locations:
            for column in locations:
                if (self.matrix[row - 2][column - 2] != -1 or self.matrix[row - 2][column + 2] != -1 or
                    self.matrix[row + 2][column - 2] != -1 or self.matrix[row + 2][column + 2] != -1):
                    continue

                for i in range(row - 2, row + 3):
                    for j in range(column - 2, column + 3):
                        if i == row - 2 or i == row + 2 or j == column - 2 or j == column + 2:
                            self.matrix[i][j] = 1
                        else:
                            self.matrix[i][j] = 0
                self.matrix[row][column] = 1

    def place_timing_patterns(self) -> None:
        size = self.size
        for i in range(8, size - 8):
            self.matrix[6][i] = 1 - i % 2
            self.matrix[i][6] = 1 - i % 2

    def define_reserved_areas(self) -> None:
        size = self.size
        for j in range(9):
            self.matrix[8][j] = 0
            self.matrix[j][8] = 0

        self.matrix[8][6] = 1
        self.matrix[6][8] = 1

        for i in range(size - 8, size):
            self.matrix[i][8] = 0
            self.matrix[8][i] = 0

        self.matrix[size - 8][8] = 1

        if size >= 45:
            for i in range(size - 11, size - 8):
                for j in range(6):
                    self.matrix[i][j] = 0
                    self.matrix[j][i] = 0

    def place_matrix_modules(self, data: str) -> None:
        """
        Populate the matrix with tracking patterns and the encoded data in a zig-zag pattern.
        """
        self.place_finder_patterns()
        self.place_separators()
        self.place_alignment_patterns()
        self.place_timing_patterns()
        self.define_reserved_areas()

        size = self.size
        tracker = 0
        row = size - 1
        column = size - 1
        direction = -1

        while tracker < len(data):
            if self.matrix[row][column] == -1:
                self.matrix[row][column] = data[tracker]
                tracker += 1
            column -= 1

            if self.matrix[row][column] == -1:
                self.matrix[row][column] = data[tracker]
                tracker += 1
            row += direction
            column += 1

            if row == -1 or row == size:
                direction *= -1
                column -= 2
                row += direction

            if column == 6:
                column -= 1

    def apply_masks(self) -> List[List[List[int]]]:
        size = self.size
        masked_matrices = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(8)]

        for row in range(size):
            for column in range(size):
                if self.matrix[row][column] == '0':
                    masked_matrices[0][row][column] = 1 - (row + column) % 2
                    masked_matrices[1][row][column] = 1 - row % 2
                    masked_matrices[2][row][column] = 1 if column % 3 == 0 else 0
                    masked_matrices[3][row][column] = 1 if (row + column) % 3 == 0 else 0
                    masked_matrices[4][row][column] = 1 - (row // 2 + column // 3) % 2
                    masked_matrices[5][row][column] = 1 if row * column % 2 + row * column % 3 == 0 else 0
                    masked_matrices[6][row][column] = 1 - (row * column % 2 + row * column % 3) % 2
                    masked_matrices[7][row][column] = 1 - ((row + column) % 2 + row * column % 3) % 2
                elif self.matrix[row][column] == '1':
                    masked_matrices[0][row][column] = (row + column) % 2
                    masked_matrices[1][row][column] = row % 2
                    masked_matrices[2][row][column] = 0 if column % 3 == 0 else 1
                    masked_matrices[3][row][column] = 0 if (row + column) % 3 == 0 else 1
                    masked_matrices[4][row][column] = (row // 2 + column // 3) % 2
                    masked_matrices[5][row][column] = 0 if row * column % 2 + row * column % 3 == 0 else 1
                    masked_matrices[6][row][column] = (row * column % 2 + row * column % 3) % 2
                    masked_matrices[7][row][column] = ((row + column) % 2 + row * column % 3) % 2
                else:
                    # In case of reserved modules or padding that needs to just pass through
                    value = self.matrix[row][column]
                    if type(value) is int:
                        for m in range(8):
                            masked_matrices[m][row][column] = value

        return masked_matrices

    def get_version_string(self) -> str:
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
        return version_information_strings[self.version - 7]

    def place_format_string(self, matrix: List[List[int]], format_string: str) -> None:
        size = self.size
        tracker = 0
        for i in range(9):
            if i == 6:
                continue
            matrix[8][i] = int(format_string[tracker])
            matrix[i][8] = int(format_string[14 - tracker])
            tracker += 1

        tracker -= 1
        for i in range(size - 8, size):
            matrix[i][8] = int(format_string[14 - tracker])
            matrix[8][i] = int(format_string[tracker])
            tracker += 1

        matrix[size - 8][8] = 1

    def place_version_string(self, matrix: List[List[int]], version_string: str) -> None:
        size = self.size
        tracker = 17
        for i in range(6):
            for j in range(size - 11, size - 8):
                matrix[i][j] = int(version_string[tracker])
                matrix[j][i] = int(version_string[tracker])
                tracker -= 1

    def fill_reserved_areas(self, matrix: List[List[int]], format_string: str) -> None:
        self.place_format_string(matrix, format_string)
        if self.version > 6:
            version_string = self.get_version_string()
            self.place_version_string(matrix, version_string)

    def evaluate_first_penalty(self, matrix: List[List[int]]) -> int:
        size = self.size
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

    def evaluate_second_penalty(self, matrix: List[List[int]]) -> int:
        size = self.size
        penalty = 0
        for i in range(size - 1):
            for j in range(size - 1):
                if matrix[i][j] == matrix[i + 1][j] == matrix[i][j + 1] == matrix[i + 1][j + 1]:
                    penalty += 3
        return penalty

    def add_quiet_zone(self, matrix: List[List[int]]) -> List[List[int]]:
        size = self.size
        final_matrix = [[0] * (size + 8) for _ in range(size + 8)]
        for i in range(size):
            for j in range(size):
                final_matrix[i + 4][j + 4] = matrix[i][j]
        return final_matrix

    def evaluate_third_penalty(self, matrix: List[List[int]]) -> int:
        size = self.size + 8
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

    def evaluate_fourth_penalty(self, matrix: List[List[int]]) -> float:
        size = self.size
        total_modules = size * size
        dark_modules_count = sum(row.count(1) for row in matrix)
        dark_modules_percentage = int(dark_modules_count / total_modules * 100)
        previous_multiple_of_five = (dark_modules_percentage // 5) * 5
        next_multiple_of_five = previous_multiple_of_five + 5
        return min(abs(previous_multiple_of_five - 50) / 5, abs(next_multiple_of_five - 50) / 5) * 10

    def determine_best_mask(self, masked_matrices: List[List[List[int]]]) -> List[List[int]]:
        lowest_penalty = float('inf')
        lowest_penalty_index = 0

        for i in range(len(masked_matrices)):
            penalty = 0
            matrix = masked_matrices[i]

            penalty += self.evaluate_first_penalty(matrix)
            penalty += self.evaluate_second_penalty(matrix)
            penalty += self.evaluate_fourth_penalty(matrix)

            matrix_with_quiet_zone = self.add_quiet_zone(matrix)
            penalty += self.evaluate_third_penalty(matrix_with_quiet_zone)

            if penalty < lowest_penalty:
                lowest_penalty = penalty
                lowest_penalty_index = i

        return self.add_quiet_zone(masked_matrices[lowest_penalty_index])

    def mask_data(self) -> List[List[int]]:
        """
        Applies masking data and determining the optimal mask layout based on QR penalty rules.
        """
        masked_matrices = self.apply_masks()
        for i in range(len(masked_matrices)):
            format_string = FORMAT_INFORMATION[self.ec_level][i]
            self.fill_reserved_areas(masked_matrices[i], format_string)
        
        return self.determine_best_mask(masked_matrices)
