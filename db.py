import asyncio
from typing import Optional, Any, List, Tuple

import asynctnt

from models import Meme

conn = asynctnt.Connection(host='localhost', port=3301, username='admin', password='super_tarantool_password')


async def insert_meme(top_text: str, bottom_text: str) -> int:
    resp = await conn.insert('memes', [None, top_text, bottom_text, '', ''])
    return resp.body[0][0]


async def update_meme(meme_id: int, image_path: str, src_path: str):
    await conn.update('memes', [meme_id], [('=', 'image_path', image_path), ('=', 'src_path', src_path)])


async def select_meme(meme_id: int) -> Optional[Meme]:
    data = await conn.select('memes', [meme_id])
    if len(data) > 0:
        meme = data[0]
    else:
        return None
    return Meme(meme_id=meme[0], image_url=meme[3], top_text=meme[1], bottom_text=meme[2], src_url=meme[4])


async def get_all_src_images() -> List[Tuple[int, str]]:
    data = await conn.select('memes')
    return [(row[0], row[4]) for row in data]


async def search_meme(top_text: str, bottom_text: str) -> Optional[int]:
    resp = await conn.call('search_meme', [top_text, bottom_text])
    rows = resp.body[0]['rows']
    if len(rows) > 0:
        return rows[0][0]
    else:
        return None
    # print(rows)


async def start():
    await conn.connect()


async def stop():
    await conn.disconnect()


async def test():
    await start()
    print(await get_all_src_images())
    await stop()


if __name__ == "__main__":
    asyncio.run(test())
