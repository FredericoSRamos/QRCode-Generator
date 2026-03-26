from typing import List
from PIL import Image
from pyweb import pydom
from pyscript import display

from encoder import get_data_type, get_version_and_ec_level, encode_data
from error_correction import structure_final_message
from matrix import QRCodeMatrix

def draw_qr_code(matrix: List[List[int]], module_size: int = 10):
    """
    Renders the final QR Code matrix using PIL into an image.
    """
    size = len(matrix)
    img = Image.new('1', (size, size))
    pixels = img.load()

    for i in range(size):
        for j in range(size):
            pixels[j, i] = 0 if matrix[i][j] == 1 else 1

    return img.resize((size * module_size, size * module_size), Image.Resampling.NEAREST)

def generate_qr_code(event):
    """
    Main entry point for the PyScript application. Reads input, orchestrates building the 
    QR Code across the imported modules, and displays the result.
    """
    data = pydom["input#data"][0].value

    encode_type = get_data_type(data)

    try:
        version, ec_level = get_version_and_ec_level(
            data, 
            encode_type, 
            ec_level=pydom["input#error-correction-hidden"][0].value
        )
        pydom["div#qrcode"][0].html = ''

        encoded_data = encode_data(data, version, encode_type, ec_level)

        message = structure_final_message(encoded_data, version, ec_level)

        qr_matrix = QRCodeMatrix(version, ec_level)
        qr_matrix.place_matrix_modules(message)
        final_matrix = qr_matrix.mask_data()

        qr_code = draw_qr_code(final_matrix)
        display(qr_code, target="qrcode")
    except ValueError as e:
        # Expected fallback if data couldn't fit or input was invalid
        pydom["div#qrcode"][0].html = str(e)
    except Exception as e:
        # Prevent bare except and expose unexpected bugs
        pydom["div#qrcode"][0].html = f"An unexpected error occurred: {str(e)}"