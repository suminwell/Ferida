#!/usr/bin/env python3
"""
Frida Gadget JS Encryption Tool
Uses AES-256-GCM symmetric encryption

Requirements:
    pip install cryptography

Usage:
    python3 encrypt_tool.py genkey
    python3 encrypt_tool.py encrypt <input.js> <output.json> <key_hex>
    python3 encrypt_tool.py decrypt <input.json> <output.js> <key_hex>
"""
import sys
import os
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_aes_key():
    key = os.urandom(32)
    return key.hex()

def encrypt_js_file(input_file, output_file, key_hex):
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    if len(key_hex) != 64:
        print('Error: Key must be 64 hex characters')
        sys.exit(1)
    key = bytes.fromhex(key_hex)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
    encrypted_data = iv + ciphertext_with_tag
    encrypted_base64 = b64encode(encrypted_data).decode('utf-8')
    print(f'Encrypted: {len(plaintext)} -> {len(encrypted_data)} bytes')
    json_data = {'data': encrypted_base64}
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f'Output: {output_file}')

def decrypt_js_file(input_file, output_file, key_hex):
    with open(input_file, 'r') as f:
        json_data = json.load(f)
    if 'data' not in json_data:
        print('Error: Invalid JSON format')
        sys.exit(1)
    if len(key_hex) != 64:
        print('Error: Key must be 64 hex characters')
        sys.exit(1)
    key = bytes.fromhex(key_hex)
    encrypted_data = b64decode(json_data['data'])
    if len(encrypted_data) < 28:
        print('Error: Encrypted data too short')
        sys.exit(1)
    iv = encrypted_data[:12]
    ciphertext_with_tag = encrypted_data[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)
    with open(output_file, 'wb') as f:
        f.write(plaintext)
    print(f'Decrypted: {len(plaintext)} bytes')

def print_usage():
    print('Usage:')
    print('  python3 encrypt_tool.py genkey')
    print('  python3 encrypt_tool.py encrypt <input.js> <output.json> <key_hex>')
    print('  python3 encrypt_tool.py decrypt <input.json> <output.js> <key_hex>')

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    command = sys.argv[1].lower()
    if command == 'genkey':
        key_hex = generate_aes_key()
        print('Generated AES-256 key:')
        print(key_hex)
    elif command == 'encrypt':
        if len(sys.argv) != 5:
            print('Error: Wrong arguments')
            print_usage()
            sys.exit(1)
        encrypt_js_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == 'decrypt':
        if len(sys.argv) != 5:
            print('Error: Wrong arguments')
            print_usage()
            sys.exit(1)
        decrypt_js_file(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(f'Error: Unknown command: {command}')
        print_usage()
        sys.exit(1)

if __name__ == '__main__':
    main()

