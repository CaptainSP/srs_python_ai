def caesar_encrypt(text, shift):
    """Encrypts a string using the Caesar cipher.

    Args:
        text: The uppercase English alphabet string to encrypt.
        shift: The integer shift value.

    Returns:
        The encrypted string.
    """
    result = ''
    for char in text:
        if 'A' <= char <= 'Z':
            shifted_char = chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
            result += shifted_char
        else:
            result += char  # Handle non-alphabetic characters (optional)

    return result

def caesar_decrypt(text, shift):
    """Decrypts a string encrypted using the Caesar cipher.

    Args:
        text: The encrypted string.
        shift: The integer shift value.

    Returns:
        The decrypted string.
    """
    result = ''
    for char in text:
        if 'A' <= char <= 'Z':
            shifted_char = chr(((ord(char) - ord('A') - shift) % 26) + ord('A'))
            result += shifted_char
        else:
            result += char #Handle non-alphabetic characters (optional)

    return result


# Example usage
text = "HELLO"
shift = 3
encrypted_text = caesar_encrypt(text, shift)
decrypted_text = caesar_decrypt(encrypted_text, shift)

print(f"Original text: {text}")
print(f"Encrypted text: {encrypted_text}")
print(f"Decrypted text: {decrypted_text}")

text2 = "HELLO, WORLD!"
shift2 = 5
encrypted_text2 = caesar_encrypt(text2, shift2)
decrypted_text2 = caesar_decrypt(encrypted_text2, shift2)

print(f"\nOriginal text: {text2}")
print(f"Encrypted text: {encrypted_text2}")
print(f"Decrypted text: {decrypted_text2}")