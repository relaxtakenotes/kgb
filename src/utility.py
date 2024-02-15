from difflib import Differ
from functools import wraps, partial
import asyncio
import json
import os

def get_text_difference(text1, text2):
    differ = Differ()
    return differ.compare(text1.split("\n"), text2.split("\n"))

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run

def textwrap(text):
    return ["```" + (text[i:i + 1990]) + "```" for i in range(0, len(text), 1990)]

def write_internal(data):
    with open("internal.json", "w+") as f:
        json.dump(data, f, indent=4)

def get_internal():
    if not os.path.isfile("internal.json"):
        return {}

    with open("internal.json") as f:
        return json.load(f)

def log(problem):
    with open("problems.log", "a+") as f:
        f.write(problem + "\n")