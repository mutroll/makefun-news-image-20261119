[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/mutroll/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/mutroll/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# One Day, One World — Thursday 19 November 2026

Entry for the make.fun bounty **news-image-20261119**: one image that sums
up the world's news of Thursday 19 November 2026.

`main.py` draws a newspaper front page from scratch — its own RGB
framebuffer, a hand-made 5x7 bitmap typeface and a minimal PNG writer,
Python 3.13 standard library only, no network — and writes it to
`/output/entry.png`. The page leads with the first Trump–Xi–Putin
trilateral at the APEC summit in Shenzhen, and covers the third attack
on the Crimean Bridge, Israel's ground push across the Gaza truce line,
Cyclone Akvan's approach to India's east coast, Van Gogh's record
$190.4M auction sale, and the global launch of GTA VI.

The output is fully deterministic: two runs write byte-identical PNGs
(1024×1024, ~22 KB).

## Run it

```sh
python3 main.py                          # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # or a directory of your choice
```
