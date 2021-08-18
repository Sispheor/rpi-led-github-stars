import asyncio
import os
import sys
import requests
from time import sleep
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, LCD_FONT, CP437_FONT
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message

INTERVAL_CHECK = 60
REPO_URL = "https://api.github.com/repos/HewlettPackard/squest"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)

if GITHUB_TOKEN is None:
    print("GITHUB_TOKEN required")
    exit(1)


async def get_github_stars():
    print("Call Github API to get number of stars")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    r = requests.get(REPO_URL, headers=headers)
    try:
        stargazers_count = r.json()["stargazers_count"]
    except KeyError:
        return None
    return str(stargazers_count)


async def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    number_of_star_before = 0
    print("Start main")
    while True:
        number_of_star_now = await get_github_stars()
        if number_of_star_now is not None:
            if number_of_star_before != number_of_star_now:
                print(f"Stars now: {number_of_star_now}")
                await draw_new_star(device, number_of_star_now)
                number_of_star_before = number_of_star_now
                await draw_current_stars(device, number_of_star_now)

        print(f"Sleep {INTERVAL_CHECK} seconds before next check")
        await asyncio.sleep(INTERVAL_CHECK)


async def draw_new_star(device, stars):
    text_to_print = f"New star on Squest --> {stars}"
    show_message(device, text_to_print, fill="white", font=proportional(CP437_FONT), scroll_delay=0.05)


async def draw_current_stars(device, stars):
    with canvas(device) as draw:
        for i in range(1, 7):
            draw.point((i, 0), fill="white")
            draw.point((i, 1), fill="white")
            draw.point((i, 2), fill="white")
            draw.point((i, 3), fill="white")
            draw.point((i, 4), fill="white")
            draw.point((i, 5), fill="white")
        for i in range(1, 5):
            draw.point((0, i), fill="white")
            draw.point((7, i), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((4, 7), fill="white")
        # V inside
        draw.point((2, 3), fill="black")
        draw.point((3, 4), fill="black")
        draw.point((4, 3), fill="black")
        draw.point((5, 2), fill="black")

        text(draw, (10, 1), stars, fill="white", font=proportional(LCD_FONT))

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
