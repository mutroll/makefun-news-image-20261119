[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/mutroll/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/mutroll/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# Thursday 19 November 2026 — The World in One Day

A bold poster that sums up the world's news of **Thursday 19 November 2026**
in a single 1024×1024 image, drawn programmatically by `main.py`
(Python 3.13, standard library only, deterministic, no network).

The design puts the date first — a giant masthead naming the day — then six
large panels with simple scenes and short, heavy headlines that stay legible
even when the poster is shrunk to thumbnail size.

## The six stories

1. **Trump · Xi · Putin — Shenzhen summit.** The three leaders held their
   first trilateral meeting on the sidelines of the APEC summit in Shenzhen,
   with nuclear arms control and Ukraine on the table.
2. **Crimean Bridge hit a third time.** Ukraine struck the Kerch bridge
   again early on Thursday; traffic was suspended while damage was assessed.
3. **Tanks enter central Gaza.** Israeli forces advanced west of the Yellow
   Line into central Gaza — the first major ground push since the October
   2025 ceasefire — as floods destroyed shelters and Australia, Canada,
   Italy and the UK jointly demanded immediate humanitarian access.
4. **Cyclone Akvan nears India.** The Bay of Bengal storm headed for the
   Andhra Pradesh–Odisha coast with ~50,000 people evacuated in Odisha.
5. **Van Gogh sells for $190.4M.** *Blossoming Chestnut Trees* (1890) set a
   new record for the artist at Sotheby's New York.
6. **GTA VI launches worldwide.** The first new mainline Grand Theft Auto
   in 13 years rolled out globally, back in Vice City / Leonida.

Footer: Anthropic's record $81.3bn IPO, the EU's proposed €45bn Ukraine
loan, and the EU–Indonesia trade pact.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024×1024 PNG, same bytes on every run)
```

Without `MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`, as in the
competition sandbox.
