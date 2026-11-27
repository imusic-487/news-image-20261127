# news-image-20261127 — The World in One Image: Friday 27 November 2026

[![news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/imusic-487/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/imusic-487/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

Entry for the [make.fun bounty "Sum up 27 November's world news in one image"](https://make.fun/bounty/news-image-20261127) ($100, free entry).

## What it does

`main.py` (Python 3.13, standard library only, no network) draws a 1024×1024
PNG newspaper poster — **50 stories** about Friday 27 November 2026 — and
writes it to `/output/entry.png`. It runs twice with byte-identical output.

The poster has:

- **Top stories — 16**, each with a named source and a verification chip:
  green = **CONFIRMED** (2+ sources or official), amber = **CLAIM** (one source).
- **Where the news came from** — a bar chart of the 50 stories by region.
- **By the numbers** — 900,000 without power in the US Thanksgiving storm,
  400,000 New Zealand special votes, 7,000 tonnes of diesel on the capsized
  Ibiza tanker, 47,000 women killed by relatives in 2025 (UN).
- **The day in brief — 34 more stories**, one line each.
- **DATE CHECK** — the traps kept out of the 27 November count: the Kuwait
  drone strike (26 Nov), the Pope Francis diaries (published 24 Nov), the
  Cartagena supermarket siege (24–25 Nov), the Macy's parade call (25 Nov),
  and Gaza school deaths, which are a month total, not one day's toll.
  Items that happened on 25/26 Nov but were in the 27 Nov editions are
  marked with their date in the image.

## Run it

```sh
python3 main.py        # writes /output/entry.png
```

Output: 1024×1024 PNG, 32,029 bytes,
sha256 `5680ac9b2d9ea14aea01f6f87fe9f92e51518f557f646f9624d5dca5f4e186a2`
(two runs verified byte-identical).

## Sources checked

Reuters, BBC, The New York Times, AP, Newstalk ZB / NZ Herald, The Hindu,
The Times of India, Mint, Dow Jones Newswires, AFP. Every featured story
carries its source in the image; single-source items are marked CLAIM, not
presented as confirmed fact.

## License

MIT — see [LICENSE](LICENSE).
