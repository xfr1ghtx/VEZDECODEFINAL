let img = document.getElementById('img')

document.getElementById('next_btn').onclick = () => {
    nextMeme()
}


async function nextMeme() {
    img.src = `/random`;
}

nextMeme()