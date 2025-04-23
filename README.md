# QR Code Generator

## Overview
This project is a QR Code generator implemented in Python. It encodes various types of data into QR Codes, including numeric, alphanumeric, byte, and Kanji characters. The generator also incorporates error correction capabilities and applies different mask patterns to optimize the QR Code for scanning.

## Features
- **Data Type Detection**: Automatically detects the type of data (numeric, alphanumeric, byte, or Kanji).
- **Encoding**: Supports encoding of numeric, alphanumeric, byte, and Kanji data into QR Code format.
- **Error Correction**: Implements Reed-Solomon error correction to recover data in case of damage.
- **Masking**: Applies various mask patterns to minimize scanning errors and optimize readability.
- **Dynamic Versioning**: Adjusts the QR Code version based on the amount of data and error correction level.
- **Image Generation**: Generates a visual representation of the QR Code.

## How to use
Thanks to the PyScript framework and the GitHub Pages, this application is available for free at https://fredericosramos.github.io/QRCode-Generator/
