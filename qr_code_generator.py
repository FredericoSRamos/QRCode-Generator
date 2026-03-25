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
    img_size = size * module_size
    img = Image.new('L', (img_size, img_size), color=255)

    for i in range(size):
        for j in range(size):
            color = 0 if matrix[i][j] == 1 else 255
            for x in range(module_size):
                for y in range(module_size):
                    img.putpixel((j * module_size + x, i * module_size + y), color)

    return img

def generate_qr_code(event):
    """
    Main entry point for the PyScript application. Reads input, orchestrates building the 
    QR Code across the imported modules, and displays the result.
    """
    data = pydom["input#data"][0].value

    encode_type = get_data_type(data)
    version, ec_level = get_version_and_ec_level(
        data, 
        encode_type, 
        ec_level=pydom["input#error-correction-hidden"][0].value
    )

    try:
        # If version is an error string, this will raise a ValueError
        int(version)
        pydom["div#qrcode"][0].html = ''

        encoded_data = encode_data(data, int(version), encode_type, ec_level)

        message = structure_final_message(encoded_data, int(version), ec_level)

        qr_matrix = QRCodeMatrix(int(version), ec_level)
        qr_matrix.place_matrix_modules(message)
        final_matrix = qr_matrix.mask_data()

        qr_code = draw_qr_code(final_matrix)
        display(qr_code, target="qrcode")
    except ValueError:
        # Expected fallback if data couldn't fit or input was invalid
        pydom["div#qrcode"][0].html = str(version)
    except Exception as e:
        # Prevent bare except and expose unexpected bugs
        pydom["div#qrcode"][0].html = f"An unexpected error occurred: {str(e)}"