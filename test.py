def caesar_cipher(text, shift, mode):
    """
    Implements a Caesar cipher for encoding and decoding text.

    Args:
        text: The input string (uppercase English letters only).
        shift: The number of positions to shift each letter.
        mode: 'encode' or 'decode'.

    Returns:
        The encoded or decoded string.  Returns an error message if the input is invalid.

    """
    if not text.isupper() or not text.isalpha():
        return "Error: Input must be uppercase English letters only."

    result = ''
    for char in text:
        start = ord('A')
        shifted_char = chr((ord(char) - start + shift) % 26 + start) if mode == 'encode' else chr((ord(char) - start - shift) % 26 + start)
        result += shifted_char
    return result

#Example usage
encoded_text = caesar_cipher("HELLO", 3, "encode")
print(f"Encoded: {encoded_text}")  # Output: KHOOR

decoded_text = caesar_cipher(encoded_text, 3, "decode")
print(f"Decoded: {decoded_text}")  # Output: HELLO

invalid_input = caesar_cipher("Hello World",3,"encode")
print(f"Invalid Input Result: {invalid_input}") # Output: Error: Input must be uppercase English letters only.