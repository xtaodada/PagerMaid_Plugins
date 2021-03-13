import random
import string

async def main(context):
    try:
        length = int(context.text.split()[1])
    except:
        length = 8
    if length > 1000:
        length = 100
    s = ""
    for i in range(length):
        s += random.choice(string.ascii_letters + string.digits)
    return f"`{s}`"
