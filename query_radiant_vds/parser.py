from asyncio import Queue
from json import dumps
from logging import getLogger

logger = getLogger(__name__)


async def json_out(q: Queue) -> None:
    endl = ""
    print("[")
    while True:
        result = await q.get()
        q.task_done()
        if result is None:
            break
        print(f"{endl}{dumps(result, indent=4)}", end="")
        endl = ",\n"
    print("\n]")
