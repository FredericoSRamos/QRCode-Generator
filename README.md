# QR Code Encoder

A simple QR Code encoder written in Python, designed to convert input text into a binary string suitable for QR code generation. This project supports **Numeric**, **Alphanumeric**, and **Byte** encoding modes in accordance with the QR code specification.

---

## 🚀 Features

- Automatic detection of encoding mode (Numeric, Alphanumeric, Byte)
- Support for QR code versions 1 to 40 (Medium error correction)
- Data segmentation and encoding as per QR standard
- Padding and final bitstream construction

---

## 🧠 Encoding Modes

The encoder supports the following QR modes:

| Mode         | Detected When                              |
|--------------|---------------------------------------------|
| Numeric      | String contains only digits (`0-9`)         |
| Alphanumeric | Characters from `0-9A-Z $%*+-./:`           |
| Byte         | Any other character (UTF-8 is assumed)      |

It is currently a work in progress
