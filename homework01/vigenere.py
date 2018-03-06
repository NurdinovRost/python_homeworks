def encrypt_vigenere(plaintext, keyword):
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    # PUT YOUR CODE HERE
    while len(plaintext) > len(keyword):
        keyword += keyword
    ciphertext = ""
    for i in range(len(plaintext)):
        if  (65 <= ord(plaintext[i]) <= 90) or (97 <= ord(plaintext[i]) <= 122):
            if ord(plaintext[i]) < 91:
                code = ord(plaintext[i]) + ord(keyword[i]) - 65
                if code > 90:
                    ciphertext += chr(65 + (code - 91))
                else:
                    ciphertext += chr(code)
            else:
                code = ord(plaintext[i]) + ord(keyword[i]) - 97
                if code > 122:
                    ciphertext += chr(97 + (code - 123))
                else:
                    ciphertext += chr(code)
        else:
            ciphertext += plaintext[i]
    return ciphertext

encrypt_vigenere("ATTACKATDAWN", "LEMON")


def decrypt_vigenere(ciphertext, keyword):
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    # PUT YOUR CODE HERE
    while len(ciphertext) > len(keyword):
        keyword += keyword
    plaintext = ""
    for i in range(len(ciphertext)):
        if  (65 <= ord(ciphertext[i]) <= 90) or (97 <= ord(ciphertext[i]) <= 122):
            if ord(ciphertext[i]) < 91:
                code = ord(ciphertext[i]) - ord(keyword[i]) + 65
                if code < 65:
                    plaintext += chr(90 - (64 - code))
                else:
                    plaintext += chr(code)
            else:
                code = ord(ciphertext[i]) - ord(keyword[i]) + 97
                if code < 97:
                    plaintext += chr(122 - (96 - code))
                else:
                    plaintext += chr(code)
        else:            
            plaintext += ciphertext[i]            
    return plaintext
