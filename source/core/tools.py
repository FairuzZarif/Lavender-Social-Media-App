import random
import string


# Generate Strong Password Python, ChatGPT, OpenAI, 2024-11-29.
def generate_password():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits)
    ]
    all_chars = lowercase + uppercase + digits
    password += random.choices(all_chars, k = 16 - len(password))
    random.shuffle(password)
    return ''.join(password)
