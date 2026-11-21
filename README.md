# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/dftaufiq/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/dftaufiq/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image summing up the world's news of Saturday 21 November 2026: a newspaper front page with 35 stories across 7 regions — 3 illustrated lead stories, 10 illustrated features, a numbered world map and 22 more briefs — every one of them dated to Saturday 21 November 2026.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## About the image

`main.py` (Python 3.13, standard library only) copies `entry.png` to the output directory. The image itself is drawn from scratch by `generate_image.py` (build-time only, needs Pillow) — no photographs or copied artwork: every panel, chart and the dotted world map are drawn in code. Every story on the page was checked against reporting of 21 November 2026, with sources named beside each story:

- Antalya: COP31 slips into overtime with no deal — the third draft is due Saturday morning, fossil fuels and the $120bn adaptation target dropped from the text
- Riyadh: the Saudi-led coalition intercepts three Houthi ballistic missiles fired towards the capital on Saturday
- Warsaw: NATO chief Mark Rutte flies in on Saturday after Friday's airspace breach — a Kh-101 cruise missile and a drone crossed into Poland
- New York: Wall Street ends its worst week since 2020 — Nasdaq −5.28% at Friday's close, S&P 500 in correction, VIX at 35.89
- Kyiv: Zelenskyy warns Russia is stepping up double-tap and triple-tap strikes "to kill as many people as possible"
- Turin: the ATP Finals semi-finals — Alcaraz v Shelton and Zverev v Medvedev, the top four seeds
- Plus Brent at $92.57, gold at $3,517, Akvan weakening over Odisha, Cyclone Xavier's gale warnings, the Vatican tree, EU aid for Kyiv, Ebola in eastern Congo — and 22 more briefs

The DATE CHECK box at the foot of the page names the big stories deliberately left out because they happened on earlier days (the Denmark "assassination plot", Gupta's sentencing, the 900,000 AI chips cleared for China, Mongolia's president resigning, India's H5N1 vaccine, the Kryvyi Rih strike, the Kyiv barrage, Akvan's landfall) — so the page shows Saturday's news and nothing else.

To redraw the image from its source data: `python3 generate_image.py`

---

<sub>Entered on [make.fun](https://make.fun/?ref=bqc0tvks&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
