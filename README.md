# Meme generator using Tarantool

Run:

- `docker  compose up -d`
- `python3 main.py`

Endpoints:

- Page with random generation: `/`
- Get request: `/get?meme_id=<id>`
- Set request: `/set`
    - Body examples:
        - `{
          "image_url": "https://example/image.jpg",
          "top_text": "super",
          "bottom_text": "meme"
          }`
        - `{
          "top_text": "super",
          "bottom_text": "meme"
          }`
        - `{
          "image_url": "https://example/image.jpg"
          }`
