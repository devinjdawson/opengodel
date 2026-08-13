ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/hp#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousHMSHistorical Multiple Security](https://godelterminal.com/docs/commands/hms.html)[NextCFFilings→](https://godelterminal.com/docs/commands/cf.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
HP

# HP: Historical Prices Command

HP is the Godel Terminal command for viewing a security's historical prices as a daily or intraday table: OHLCV exportable to Excel or JSON.

![HP window for AAPL US cycling through paged daily OHLCV history with summary bar and per-row high/low highlighting](./HP Command (Historical Prices) _ Godel Terminal Docs_files/hp-1d-loop.gif)

## How to use HP

**Security Identifier/Ticker Country/Instrument Asset Class HP**

Example: AAPL US EQ HP: daily prices for Apple (default = one year back to today).

![Godel Terminal command bar showing AAPL US EQ HP typed with the COMMANDS autocomplete suggesting 'Historical prices for a security'](./HP Command (Historical Prices) _ Godel Terminal Docs_files/hp-01.png)

## Toolbar

At the top of the window:

* **Date pickers**: start and end of the history window.
* **Excel download** (icon): exports every loaded row to a spreadsheet.
* **Resolution dropdown**: 1D, 1H, 1M. See [Resolutions](https://godelterminal.com/docs/commands/hp#resolutions) below.
* **QuickQuote** chip: current live price.

## Resolutions

HP renders three resolutions out of the same window: daily, hourly, and minute-level. The toolbar dropdown switches between them; switching to 1D or 1H resets the range to the last year, while 1M resets to yesterday only because minute data is dense.

### 1H: hourly intraday

Each row is one trading hour, labelled with the hour range (e.g. *07 PM to 08 PM*). The summary bar reports total **Hours** in the loaded range; volume is the hour's tape.

![HP at 1H resolution for AAPL US cycling through paged hourly OHLCV history](./HP Command (Historical Prices) _ Godel Terminal Docs_files/hp-1h-loop.gif)

### 1M: minute-level intraday

Each row is one minute, labelled with the minute range (e.g. *07:59 PM to 08:00 PM*). The summary bar reports total **Minutes** in the loaded range. Use the date picker to widen the window beyond yesterday.

![HP at 1M resolution for AAPL US cycling through paged minute-level OHLCV history](./HP Command (Historical Prices) _ Godel Terminal Docs_files/hp-1m-loop.gif)

## Summary Bar

Underneath the toolbar, HP displays a one-line analysis of the loaded range:

* **Units**: how many rows are shown (Days / Hours / Minutes)
* **Hi**: period high, in green
* **Lo**: period low, in red
* **Chg**: cumulative change from the first to last close, color-coded
* **Avg**: mean close across the range, in primary theme color

## Display Columns

| Column | Description |
| --- | --- |
| **Date** | Date (and time range for intraday resolutions): weekdays are labeled; highest / lowest rows are called out by color |
| **Open** | Session open |
| **Close** | Session close |
| **High** | Session high: highlighted green if it is the period high |
| **Low** | Session low: highlighted red if it is the period low |
| **Volume** | Session volume, K / M / B formatted |

On daily view, weekends are elided and closed-market weekdays render a grayed-out placeholder row so the calendar is continuous.

## Paging

HP shows 100 rows per page. Use the previous / next arrows in the footer to move through the range; the center chip shows the current page number.

## Multi-asset history

HP is not just for equities. Open historical prices on forex pairs, corporate and sovereign bonds, crypto, futures, and indices: find the instrument with [SECF](https://godelterminal.com/docs/commands/secf.html), then open HP on it. Below: a year of daily history on CHFUSD forex, the SRPT 4.875 corporate bond, and BTCUSD, side by side in one workspace.

![Three HP windows side by side showing a year of daily OHLCV history for CHFUSD forex, the SRPT 4.875 corporate bond, and BTCUSD crypto, each with its own summary bar and export button](./HP Command (Historical Prices) _ Godel Terminal Docs_files/hp-02.png)

## Entitlements

* **Daily (1D) data** is available to all accounts.
* **Intraday (1H and 1M) data** requires an entitlement: see the [ENT](https://godelterminal.com/docs/commands/ent.html) command to get access.

## Related commands

* [G Chart](https://godelterminal.com/docs/commands/g.html)
* [HMS Historical Multiple Security](https://godelterminal.com/docs/commands/hms.html)
* [HCP Historical Change %](https://godelterminal.com/docs/commands/hcp.html)

## FAQ

What does HP do?

HP is the Godel Terminal historical prices command.

How do I open HP in Godel Terminal?

Type HP in the terminal, or prefix with a ticker (for example, NVDA US EQ HP).

Is HP available on all plans?

Yes, HP is available on every Godel plan.

Does HP work for ETFs, indices, or non-US securities?

Yes. HP works for ETFs, indices, and non-US securities, not just US stocks.

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

[Get a demo](https://godelterminal.com/docs/commands/hp#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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