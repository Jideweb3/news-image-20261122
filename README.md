# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Jideweb3/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Jideweb3/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A Python program that draws a one-page broadsheet — **The Sunday Chronicle** — summing up Sunday 22 November 2026's world news in a single image, and writes it to `/output/entry.png`.

The lead story is the collapse of the COP31 climate talks in Antalya, Turkey: after 44 hours of overtime, the EU and others rejected a final draft that made no mention of fossil fuels, leaving the summit with no headline deal for the first time since Copenhagen 2009. Around it, 29 more real stories from the day — Iran's strikes on Bahrain and tankers at Hormuz, Russian strikes on Kryvyi Rih, Kyiv and Poland, the capture of cartel boss 'El Chapo Isidro' in Mexico, the World Court's genocide ruling against Myanmar, the Indonesia factory fire, the FBI database breach, the US stock correction, GTA 6's record launch, and more — each with a drawn picture and a short label. Facts as reported by Reuters, AP, AFP, CNN, WION, Rappler and Sky Sports.

## Run it

```sh
python3 main.py
```

Python 3.13 standard library only — no packages to install. The program writes `entry.png` (1024×1024, PNG) to `$MAKEFUN_OUTPUT_DIR` or `/output`, and two runs produce byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref=8wdyn50h&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
