import random

def generate_random_mobile_number(prefixChoise = ['7','8','9']):
    # Generate a random number in the range of valid mobile numbers
    # Assuming valid mobile numbers in India start with 7, 8, or 9 and are 10 digits long
    first_digit = random.choice(prefixChoise)
    remaining_digits = ''.join(random.choices('0123456789', k=9))
    print(first_digit + remaining_digits)
    return first_digit + remaining_digits
