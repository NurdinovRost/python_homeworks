def encrypt_caesar(plaintext):
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("")
    ''
    """
    # PUT YOUR CODE HERE
    ciphertext = ""
    for i in plaintext:
        if  (65 <= ord(i) <= 90) or (97 <= ord(i) <= 122):
            if ord(i) < 91:
                if ord(i) < 88:
                    ciphertext += chr(ord(i) + 3)
                else:
                    ciphertext += chr(((ord(i) + 3) % 91) + 65)
            else:
                if ord(i) < 120:
                    ciphertext += chr(ord(i) + 3)
                else:
                    ciphertext += chr(((ord(i) + 3) % 123) + 97)
        else:
            ciphertext += i
    return ciphertext


def decrypt_caesar(ciphertext):
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("")
    ''
    """
    # PUT YOUR CODE HERE
    plaintext = ""
    for i in ciphertext:
        if  (65 <= ord(i) <= 90) or (97 <= ord(i) <= 122):
            if ord(i) < 91:
                if ord(i) > 67:
                    plaintext += chr(ord(i) - 3)
                else:
                    plaintext += chr(90 - (67 - ord(i)))
            else:
                if ord(i) > 99:
                    plaintext += chr(ord(i) - 3)
                else:
                    plaintext += chr(122 - (99 - ord(i)))
        else:
            plaintext += i
    return plaintext
