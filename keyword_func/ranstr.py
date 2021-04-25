import random
import string

async def main(context, length):
    if length > 1000:
        length = 100
    s = ""
    for i in range(length):
        s += random.choice(string.ascii_letters + string.digits)
    return f"`{s}`"
