ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/g#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

Getting Started

* [Overview](https://godelterminal.com/docs.html)
* [Command reference](https://godelterminal.com/docs.html#commands)
* [Keyboard shortcuts](https://godelterminal.com/docs.html#shortcuts)
* [Pricing](https://godelterminal.com/pricing/)

Commands

Company & Security Analysis

* [DESDescription](https://godelterminal.com/docs/commands/des.html)
* [FAFinancials](https://godelterminal.com/docs/commands/fa.html)
* [ERNEarnings Estimates](https://godelterminal.com/docs/commands/ern.html)
* [EMEarnings Matrix](https://godelterminal.com/docs/commands/em.html)
* [SIShort Interest](https://godelterminal.com/docs/commands/si.html)
* [GRRatio Analysis](https://godelterminal.com/docs/commands/gr.html)
* [ANRAnalyst Ratings](https://godelterminal.com/docs/commands/anr.html)
* EVTCompany Events
* [DVDDividend Yield](https://godelterminal.com/docs/commands/dvd.html)

Market Data & Surveillance

* [QMQuote Monitor](https://godelterminal.com/docs/commands/qm.html)
* [FOCUSFocus](https://godelterminal.com/docs/commands/focus.html)
* [TASTime and Sales](https://godelterminal.com/docs/commands/tas.html)
* [HCPHistorical Change %](https://godelterminal.com/docs/commands/hcp.html)
* [WEIWorld Equity Index](https://godelterminal.com/docs/commands/wei.html)
* [WEIFWorld Equity Index Futures](https://godelterminal.com/docs/commands/weif.html)
* [IMAPIntraday Market Map](https://godelterminal.com/docs/commands/imap.html)
* [HMAPMarket Heatmap](https://godelterminal.com/docs/commands/hmap.html)
* [GLCOGlobal Commodity Futures](https://godelterminal.com/docs/commands/glco.html)
* [FXForex Pairs](https://godelterminal.com/docs/commands/fx.html)
* [MOSTMost Active](https://godelterminal.com/docs/commands/most.html)
* [HDSHolders](https://godelterminal.com/docs/commands/hds.html)
* [NNews](https://godelterminal.com/docs/commands/n.html)
* [TOPTop News](https://godelterminal.com/docs/commands/top.html)
* [TRENDTrending on Godel](https://godelterminal.com/docs/commands/trend.html)
* [HALTMarket Halts](https://godelterminal.com/docs/commands/halt.html)
* [ALLQAll Quotes](https://godelterminal.com/docs/commands/allq.html)
* [SECFSecurities Finder](https://godelterminal.com/docs/commands/secf.html)
* [WJIWojak Index](https://godelterminal.com/docs/commands/wji.html)

Portfolio & Risk

* [EQSEquity Screener](https://godelterminal.com/docs/commands/eqs.html)
* [OMONOption Chain](https://godelterminal.com/docs/commands/omon.html)
* [OVMEBlack-Scholes](https://godelterminal.com/docs/commands/ovme.html)
* [CALCCalculator](https://godelterminal.com/docs/commands/calc.html)
* [BROKBrokerage](https://godelterminal.com/docs/commands/brok.html)
* [AUMBrokerage AUM](https://godelterminal.com/docs/commands/aum.html)

Charting & Technicals

* [GChart](https://godelterminal.com/docs/commands/g.html)
* [HMSHistorical Multiple Security](https://godelterminal.com/docs/commands/hms.html)
* [HPHistorical Prices](https://godelterminal.com/docs/commands/hp.html)

Fundamentals & Filings

* [CFFilings](https://godelterminal.com/docs/commands/cf.html)
* [IPOInitial Public Offerings](https://godelterminal.com/docs/commands/ipo.html)
* [TRANEarnings Hub](https://godelterminal.com/docs/commands/tran.html)

Utilities & System

* [HELPHelp](https://godelterminal.com/docs/commands/help.html)
* [CHATChat](https://godelterminal.com/docs/commands/chat.html)
* [ACMAccount Management](https://godelterminal.com/docs/commands/acm.html)
* [PDFSettings](https://godelterminal.com/docs/commands/pdf.html)
* [ALAlerts](https://godelterminal.com/docs/commands/al.html)
* [NOTENotes](https://godelterminal.com/docs/commands/note.html)
* [ENTEntitlements](https://godelterminal.com/docs/commands/ent.html)
* [CHANGEChangelog](https://godelterminal.com/docs/commands/change.html)

Troubleshooting

* [Troubleshooting overview](https://godelterminal.com/docs/troubleshooting.html)
* [Cancel subscription](https://godelterminal.com/docs/troubleshooting.html#cancelling-subscription)
* [Error Code 5 ("Aw Snap!")](https://godelterminal.com/docs/troubleshooting.html#error-code-5-aw-snap-)

[←PreviousAUMBrokerage AUM](https://godelterminal.com/docs/commands/aum.html)[NextHMSHistorical Multiple Security→](https://godelterminal.com/docs/commands/hms.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
G

# G: Chart Command

G is the Godel Terminal command for opening the historical and real-time charting window: OHLCV candles, volume, drawing tools, and indicators powered by TradingView.

The window is alertable (you can create price alerts directly from the chart), linkable (color-link it to other windows so they follow your active ticker), and embeddable inside [CHAT](https://godelterminal.com/docs/commands/chat.html "CHAT command reference") messages using {TICKER ASSETCLASS G}.

[![](../../assets/docs/g/g-01-poster.png)](../../assets/docs/g/g-01.webm)

## Aliases

GIP and GP are both aliases for G: they open the same chart component. If you learned GIP (Intraday Chart) from Bloomberg, keep using it; Godel rewrites it to G internally. To jump directly into an intraday resolution, pass a candle argument (see below).

## How to use G

**Security Identifier/Ticker Country/Instrument Asset Class G**

Example: AAPL US EQ G: opens a daily chart for Apple.

### Resolution arguments

Add one of these tokens after G to pick the starting candle size:

| Argument | Candle size |
| --- | --- |
| 1m | 1 Minute |
| 5m | 5 Minutes |
| 15m | 15 Minutes |
| 30m | 30 Minutes |
| 1h | 1 Hour |
| 1d | 1 Day |

Example: AAPL US EQ G 1m: opens the chart in 1-minute candles.

### Default resolution by asset class

* Equities, ETFs, indices, futures, FX, crypto: **1 Day** candles.
* Options (OPT): **1 Minute** candles.

## Window Header

The top row of the window is Godel's chrome; everything below it is TradingView.

| Control | What it does |
| --- | --- |
| **Chart 🔗 AAPL US** | Window title. The 🔗 (chain) icon color-links this chart to other windows: any other window linked to the same color will track whichever ticker you switch to here. |
| **▲ / ▼ arrow + price + change + Vol** | Live quote summary. Shows the session direction arrow, last price, absolute change, percentage change, and cumulative session volume (all streaming). |
| **🔔 Bell** | Create a price alert at the crosshair or last price. Alerts created from here appear in [AL](https://godelterminal.com/docs/commands/al.html "AL command reference"). |
| **⚙ Gear** | Opens the TradingView **Chart Settings** dialog (see below). |
| **✕** | Closes the window. |

## Toolbar (left → right)

Directly under the header, TradingView's toolbar:

* D: current resolution chip. Click to open the resolution picker (1m / 5m / 15m / 30m / 1h / 1d, plus TradingView's longer intervals where data permits).
* **Candle icon**: chart style picker (Candles, Bars, Line, Area, Baseline, Heikin Ashi, Hollow Candles, Renko, Kagi, Point & Figure, Line Break).
* fₓ Indicators: opens TradingView's full indicator and strategy library. Indicators you add persist per-chart.
* **↶ / ↷**: undo / redo drawing and overlay changes.
* **⤢ Fullscreen**: expands the chart to fill the terminal's current screen.
* **📷 Camera**: snapshot the current chart as an image.

The left-edge drawing palette (pen, trend line, shapes, Fib, etc.) follows TradingView's standard layout and is hidden by default on narrow windows: drag the window wider to reveal it.

## Footer: Timeframe & Scale

Along the bottom of the chart:

| Control | What it does |
| --- | --- |
| **5y · 1y · 6m · 3m · 1m · 5d · 1d** | Range presets. These set how far back the chart displays; they are independent from candle resolution. The active preset is highlighted. |
| **📅 Calendar icon** | Opens a custom **Go To** date / date-range picker. |
| **Clock / UTC offset** | The rightmost cluster shows the current time and your browser's UTC offset (e.g. 11:57:32 UTC-4). |
| % | Toggles the y-axis between dollar prices and percent change from a reference. |
| log | Toggles logarithmic y-axis. |
| auto | Re-fits the visible price range to the data on screen. |

## Y-Axis Context Menu

Right-click the price scale on the right edge of the chart to open the scale menu. Godel exposes TradingView's full set of scale options:

**Scale modes** (choose one):

* **Regular**: linear price axis (default).
* **Percent**: ⌥P: y-axis in % change from the first visible bar.
* **Indexed to 100**: rebase the series so the first visible bar = 100.
* **Logarithmic**: ⌥L: log-scale the price axis.

**Scale controls:**

* **Lock price to bar ratio**: freezes the aspect ratio between price and time. The current ratio is shown next to the item (e.g. 0.5537).
* **Scale price chart only**: fix sub-panes (volume, indicators) while zooming the price pane.
* **Invert scale**: ⌥I: flips the y-axis (high at the bottom, low at the top).
* **Move scale to left**: render the price axis on the left edge of the chart instead of the right.

**Labels submenu:**

| Label | What it shows |
| --- | --- |
| **Symbol name label** | Ticker label anchored to the last price |
| **Symbol last price label** | Live last-price tag on the y-axis |
| **High and low price labels** | Persistent high / low markers for the visible range |
| **Indicators name labels** | Indicator names alongside their values |
| **Indicators value labels** | Live value readouts for each indicator |
| **Countdown to bar close** | Seconds remaining on the current candle |
| **No overlapping labels** | Smart-collapse labels that would overlap |

Checked items in the screenshot above are the defaults: **Symbol last price label**, **Indicators value labels**, **No overlapping labels**.

**Lines submenu**: toggle the visual rules drawn at the current price, previous close, pre/post-market session lines, and the horizontal "bid/ask" lines.

**Plus button**: toggles the TradingView + button that appears next to the last bar for quick actions (add alert, draw, trade where supported).

## Chart Settings

Click the **gear** icon in the window header to open the full **Settings** dialog. It has four tabs on the left rail:

1. **Candles / Symbol**: colors for the candle body, borders, and wicks (up and down), plus toggles for **Color bars based on previous close** and for drawing **Body**, **Borders**, and **Wick** independently. The **Data Modification** section controls extended-hours handling and session fills. 2. **Status Line**: what shows in the top-left of the chart: OHLC values, change, volume, bar time, indicator titles, last price label style. 3. **Scales & Lines**: grid, labels, and axis behavior (most of which also live in the right-click scale menu above). 4. **Trading / Drawings**: drawing-tool defaults (color, line width, text size) and alert line appearance.

Click **⋯** (bottom-left of the dialog) to access **Reset to defaults** and per-section reset options.

Settings are saved **per chart window**: different G windows can have different colors, indicators, and layouts. They persist across sessions on your account.

## Alerts from the Chart

Click the 🔔 bell to open the alert creator with the current price pre-filled. You can also right-click any price on the y-axis and pick **Add alert at …**: Godel uses that price as the threshold. Alerts created here show up in [AL](https://godelterminal.com/docs/commands/al.html "AL command reference") and notify on your desktop when triggered.

## Linking Windows

Click the 🔗 icon in the window title to open the link-color picker. Any other window set to the same color will follow whichever ticker you type into G: useful for running a G, [DES](https://godelterminal.com/docs/commands/des.html "DES command reference"), [N](https://godelterminal.com/docs/commands/n.html "N command reference"), and [OMON](https://godelterminal.com/docs/commands/omon.html "OMON command reference") side-by-side that all sync when you change symbol.

## Keyboard & mouse shortcuts

| Input | Action |
| --- | --- |
| **Scroll** | Zoom time axis |
| **Click + drag chart** | Pan |
| **Shift + drag y-axis** | Stretch price range |
| **Double-click y-axis** | Reset price range to auto |
| ⌥L | Toggle logarithmic scale |
| ⌥P | Toggle percent scale |
| ⌥I | Invert scale |

Godel's own window-management hotkeys (Tab, Shift+Arrow, Option+Arrow, double-tap Esc, etc.) also work while the chart is focused. If TradingView steals keyboard focus, re-enable "Disable Focusing into TradingView" in [PDF](https://godelterminal.com/docs/commands/pdf.html "PDF command reference") settings (it's on by default).

## Instance Limits

Up to **30 G windows per screen** for every account tier. There is no cap across screens: grid layouts of intraday charts are intentionally supported.

## Notes

* G does not popout to a native OS window: the chart lives inside the terminal only.
* Chart data is gated on the AGGREGATE\_RTH feed; if a security is missing that feed, the chart area will render empty.
* Fullscreen (⤢) fills the current Godel screen: use the browser fullscreen (F11) to take over the whole display.

## Related commands

* [HMS Historical Multiple Security](https://godelterminal.com/docs/commands/hms.html)
* [HP Historical Prices](https://godelterminal.com/docs/commands/hp.html)
* [GR Ratio Analysis](https://godelterminal.com/docs/commands/gr.html)
* [HCP Historical Change %](https://godelterminal.com/docs/commands/hcp.html)

## FAQ

What does G do?

G is the Godel Terminal chart command.

How do I open G in Godel Terminal?

Type G in the terminal, or prefix with a ticker (for example, NVDA US EQ G).

Is G available on all plans?

Yes, G is available on every Godel plan.

### Keep reading

[All commands →](https://godelterminal.com/docs.html#commands)

[Referral Program](https://godelterminal.com/referral.html)[Careers](https://godelterminal.com/careers.html)[Documentation](https://docs.godelterminal.com/)[Contact](https://godelterminal.com/contact.html)[Newsletter](https://godelterminal.com/newsletter/)

[Terms of Service](https://godelterminal.com/terms.html)|[Privacy Policy](https://godelterminal.com/privacypolicy.html)|[Cookies](https://godelterminal.com/cookies.html)

[Try It Now](https://app.godelterminal.com/?page=register)

---

Disclaimer: The information provided on this website by DL Software dba Godel Terminal is strictly for informational purposes only and should not be construed as an offer to sell, a solicitation to buy, or a recommendation for any security or strategy. DL Software dba Godel Terminal is not a broker or registered investment advisor, and we are not registered with any financial or securities regulatory authority to give financial and investment advice. While we make every effort to maintain the accuracy and timeliness of information, we cannot guarantee its absolute accuracy. We strongly recommend conducting personal research or consulting a qualified financial advisor before making any investment decisions. Trading in financial markets involves significant risk, and past performance does not guarantee future results. DL Software dba Godel Terminal, its employees, or its affiliates will not be held liable for any losses or damages arising from the use of any information on this website. Use of this website signifies your agreement to this disclaimer.

DL Software © 2026. All rights reserved.

[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)

Product

[Real-Time News](https://godelterminal.com/real-time-market-news/)[Real-Time Quotes](https://godelterminal.com/real-time-quotes/)[SEC Filings](https://godelterminal.com/sec-filings/)[Financial Terminal](https://godelterminal.com/financial-terminal/)[Asset Classes & Data Coverage](https://godelterminal.com/asset-classes-data-coverage/)

Customers

[Wealth Teams & Family Offices](https://godelterminal.com/wealth-teams-family-offices/)[Hedge Fund & Portfolio Managers](https://godelterminal.com/hedge-funds-portfolio-managers/)[Equity Research](https://godelterminal.com/equity-research/)[Corporates & Investor Relations](https://godelterminal.com/corporates-investor-relations/)[Traders & Individuals](https://godelterminal.com/traders/)

[Get a demo](https://godelterminal.com/docs/commands/g#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

×

## Reach out to our sales team

We'll respond within 24 hours.

See how the following firms get real-time coverage on their universe:

* Hedge Funds
* Family Offices
* RIAs
* Banks
* Fortune 500 companies

“I've been using Godel every day for research, market data, and option chain data. Fundamentals, options chain positioning, and market data to monitor the industries in my coverage area. Just the simple stuff that matters, all in one place.”

$350M AUMEquity-focused Hedge Fund — Feb 2026