from PIL import Image
import math
from random import randint
from js import document, Uint8Array, window, File
from io import BytesIO
from pyodide import ffi

darken_map = [
    [False, False, False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False, False, False],
    [False, False, False, True, True, True, True, False, False, False],
    [False, False, True, False, False, False, False, True, False, False],
    [False, False, True, False, False, False, False, True, False, False],
    [False, False, True, False, False, True, False, True, False, False],
    [False, False, True, False, False, False, True, False, False, False],
    [False, False, False, True, True, True, False, True, False, False],
    [False, False, False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False, False, False],
]


def darken(px, amount):
    r, g, b = px
    return max(0, r) - amount, max(0, g) - amount, max(0, b) - amount

def generate(e = None):
    img = Image.new("RGB", (10, 10))
    from_colour = randint(0, 255), randint(0, 255), randint(0, 255)
    to_colour = randint(0, 255), randint(0, 255), randint(0, 255)

    width, height = img.size

    # credit: https://stackoverflow.com/a/32329124
    for x in range(width):
        for y in range(height):
            dist = (math.fabs(0 - x) + math.fabs(0 - y)) / (img.size[0] + img.size[1])
            r, g, b = map(
                lambda start, end: start + end,
                map(lambda start: start * (1 - dist), from_colour),
                map(lambda end: end * dist, to_colour),
            )
            px = int(r), int(g), int(b)
            img.putpixel((x, y), darken(px, 70) if darken_map[y][x] else px)

    image_stream = BytesIO()
    img.resize((500, 500), resample=Image.Resampling.BOX).save(
        image_stream, format="PNG"
    )

    # credit: https://jeff.glass/post/pyscript-image-upload/
    image_file = File.new(
        [Uint8Array.new(image_stream.getvalue())], "quake.png", {type: "image/png"}
    )
    new_image = document.createElement("img")
    new_image.src = window.URL.createObjectURL(image_file)

    output = document.getElementById("output")
    children = output.querySelectorAll("img")

    if children.length > 0:
        children.item(0).remove()

    output.appendChild(new_image)
    document.body.style.backgroundImage = "linear-gradient(to bottom right, #{:02x}{:02x}{:02x}, #{:02x}{:02x}{:02x}".format(*from_colour, *to_colour)

generate_image = ffi.create_proxy(generate)

document.getElementById("button").addEventListener("click", generate_image)
generate()
