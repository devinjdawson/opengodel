ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/hmap#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousIMAPIntraday Market Map](https://godelterminal.com/docs/commands/imap.html)[NextGLCOGlobal Commodity Futures→](https://godelterminal.com/docs/commands/glco.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
HMAP

# HMAP: Market Heatmap Command

HMAP is the Godel Terminal command for viewing the intraday movement of an index, or any of your watchlists, as a market-cap-weighted heatmap. Tiles are grouped by sector, sized by your chosen metric, and update live. Currently in Beta.

[![](../../assets/docs/hmap/hmap-poster.png)](../../assets/docs/hmap/hmap.webm)

## How to use HMAP

**Command:**

HMAP

![HMAP command showing the S&P 500 as a market-cap-weighted heatmap grouped by sector, green and red tiles sized and labeled by percent change](./HMAP Command (Market Heatmap) _ Godel Terminal Docs_files/hmap-01.png)

## Map an index or a watchlist

The toolbar starts you on the **S&P 500** and **DJIA** presets. The watchlist selector next to them maps any of your own watchlists instead, so the same heatmap works for your coverage universe, a sector list, or anything else you track in [QM](https://godelterminal.com/docs/commands/qm.html "QM command reference").

![HMAP watchlist selector open on the DJIA heatmap, listing user watchlists such as Pharma, Crypto, Banks, Semis, and Chemicals](./HMAP Command (Market Heatmap) _ Godel Terminal Docs_files/hmap-02.png)

Pick a watchlist and the map redraws with just those names, still sector-grouped and market-cap-weighted:

![HMAP displaying a Chemicals watchlist as a heatmap with large green and red tiles for each member](./HMAP Command (Market Heatmap) _ Godel Terminal Docs_files/hmap-03.png)

## Toolbar controls

| Control | Description |
| --- | --- |
| **S&P 500 / DJIA** | Index presets |
| **Watchlist** | Map one of your watchlists instead of an index |
| **Size By** | Metric that sets tile size (e.g. absolute % change) |
| **Label** | Value printed on each tile (e.g. % change) |
| **Sectors** | Show or hide the sector grouping |
| **Animate / Update** | Live refresh on or off, with the update interval in milliseconds |
| **Color** | Automatic or manual color scaling |
| **Map / Table** | Switch between the heatmap and a sortable table of the same members |

## Table view

The **Table** toggle flattens the map into a sortable list with last price, change, % change, and volume for every member. Sort by any column to rank the whole index or watchlist.

![HMAP table view listing all S&P 500 members with last price, change, percent change, and volume, sorted by percent change](./HMAP Command (Market Heatmap) _ Godel Terminal Docs_files/hmap-04.png)

## Tile interactions

* Hover a tile for the full name and current change.
* Right-click a tile for quick actions on that security, like opening the quote or its [DES](https://godelterminal.com/docs/commands/des.html "DES command reference") description, without leaving the map.
* The **Movers** panel on the right edge expands to a ranked list of the day's biggest movers in the current view.

## Related commands

* [IMAP Intraday Market Map](https://godelterminal.com/docs/commands/imap.html)
* [MOST Most Active](https://godelterminal.com/docs/commands/most.html)
* [QM Quote Monitor](https://godelterminal.com/docs/commands/qm.html)
* [WEI World Equity Index](https://godelterminal.com/docs/commands/wei.html)

## FAQ

What does HMAP do?

HMAP shows the intraday movement of an index as a market-cap-weighted heatmap, grouped by sector and updating live.

How do I open HMAP in Godel Terminal?

Type HMAP in the terminal.

Can HMAP show a watchlist instead of an index?

Yes. Use the watchlist selector in the toolbar to map any of your watchlists instead of an index preset.

What is the difference between HMAP and IMAP?

IMAP is the sector-wheel intraday market map for an index. HMAP is a market-cap-weighted tile heatmap that can also map your own watchlists, with a sortable table view and live update controls.

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

[Get a demo](https://godelterminal.com/docs/commands/hmap#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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