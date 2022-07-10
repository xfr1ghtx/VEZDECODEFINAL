import io
import random
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import db
import image_processing
from models import CreateMeme

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup():
    await db.start()


@app.on_event("shutdown")
async def shutdown():
    await db.stop()


@app.post("/set")
async def set_req(meme: CreateMeme) -> Dict[str, int]:
    if meme.image_url is None:
        meme.top_text = meme.top_text or ""
        meme.bottom_text = meme.bottom_text or ""
        meme_id = await db.search_meme(meme.top_text, meme.bottom_text)
        if meme_id is None:
            raise HTTPException(status_code=404, detail="Such meme not found")

    elif meme.top_text is None and meme.bottom_text is None and meme.image_url is not None:
        images = await db.get_all_src_images()
        similar_images = image_processing.search_similar(meme.image_url, images)
        if len(similar_images) == 0:
            raise HTTPException(status_code=404, detail="No images")

        top_text = (await db.select_meme(random.choice(similar_images))).top_text
        bottom_text = (await db.select_meme(random.choice(similar_images))).bottom_text

        meme_id = await db.insert_meme(top_text, bottom_text)
        src_path, path = image_processing.generate_meme(meme.image_url, top_text, bottom_text, meme_id)
        await db.update_meme(meme_id, path, src_path)

    elif meme.top_text is not None and meme.bottom_text is not None:
        meme_id = await db.insert_meme(meme.top_text, meme.bottom_text)
        src_path, path = image_processing.generate_meme(meme.image_url, meme.top_text, meme.bottom_text, meme_id)
        await db.update_meme(meme_id, path, src_path)

    else:
        raise HTTPException(status_code=400, detail="No data")

    return {"meme_id": meme_id}


@app.get("/get")
async def get_req(meme_id: int):
    meme = await db.select_meme(meme_id)
    if meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")
    return FileResponse(meme.image_url)


@app.get("/")
async def get_index():
    return FileResponse('static/index.html')


@app.get("/random")
async def get_random():
    images = await db.get_all_src_images()
    src_image = random.choice(images)[1]
    top_text = (await db.select_meme(random.choice(images)[0])).top_text
    bottom_text = (await db.select_meme(random.choice(images)[0])).bottom_text

    img = image_processing.draw_meme_from_path(src_image, top_text, bottom_text)
    img = image_processing.img2buf(img)

    return StreamingResponse(img, media_type='image/jpeg', headers={
        'Cache-Control': 'no-store'
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
