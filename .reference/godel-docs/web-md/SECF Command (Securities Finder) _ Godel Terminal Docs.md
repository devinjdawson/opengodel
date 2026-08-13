ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/secf#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousALLQAll Quotes](https://godelterminal.com/docs/commands/allq.html)[NextWJIWojak Index→](https://godelterminal.com/docs/commands/wji.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
SECF

# SECF: Securities Finder Command

SECF is the Godel Terminal command for searching across every instrument and person indexed in Godel: tickers, funds, people, venues, and more.

**Beta.** The window title bar shows "Securities Finder Beta": some behaviors are still evolving.

[![](../../assets/docs/secf/secf-03.png)](../../assets/docs/secf/secf-03.webm)

## Aliases

SEARCH and TK both resolve to SECF: any of the three opens the same window.

## How to use SECF

**Empty window:**

SECF: opens the finder with an empty query.

![Godel Terminal command bar showing SECF typed with the COMMANDS autocomplete suggesting 'Search Godel across all instruments and people'](./SECF Command (Securities Finder) _ Godel Terminal Docs_files/secf-01.png)

**With a query pre-filled:**

&lt;QUERY&gt; SECF: the query goes into the search input as-is. Supports any text (partial tickers, names, keywords).

This window does **not** have the usual top-of-window ticker search that other commands have: all filtering happens inside the window's own toolbar.

## Asset-Class Tabs

Across the row below the toolbar, one tab per instrument type. Select one to restrict results:

| Tab | Instrument type |
| --- | --- |
| **All** | Mixed: everything that matches |
| **Equities** | Common stocks and ETFs |
| **Corporate Bonds** | TRACE-reported corporate debt |
| **Options** | Option contracts |
| **Sovereign Bonds** | Government bonds |
| **Crypto** | Cryptocurrencies |
| **Index** | Equity / bond / custom indices |
| **Futures** | Futures contracts |
| **Forex** | FX pairs |
| **People** | Analysts, executives, and other covered individuals (different column set: see below) |

The **People** tab is special: it switches the results table to a name / company / position / email / phone layout and disables the venue, country, and "Hide results with no trades" filters (they aren't applicable to person records).

## Toolbar Controls

Left to right along the top of the window:

| Control | Behavior |
| --- | --- |
| **Search term** | Free-text input. The finder re-runs automatically as you type: in-flight requests are aborted whenever a filter changes so the visible list always reflects your current criteria. |
| **Max dropdown** | Maximum number of rows to return. Options: **50**, **100**, **250**, **500**. Default: **50**. Larger caps take longer to fetch and render. |
| **Venues** | Multi-select dropdown listing every venue Godel covers, sorted by number of instruments. Each entry shows the venue's short code, full name, and total ticker count (e.g. NYSE (3.2M tickers)). Search inside the dropdown to jump to a specific venue. Default: **All Venues**. |
| **Countries** | Multi-select dropdown of listing countries. Each entry shows the country's **ISO-2 code** (AD, AE, AM, AR, AT, …) and **full country name** (with a flag indicator). Searchable. Default: **All Countries**. |
| **Hide results with no trades** *(toggle)* | When on, filters out instruments that don't have a live aggregated trading feed (AGGREGATE\_RTH). Useful for cutting out delisted / untraded listings. |

## Display Columns

### Instrument tabs (everything except People)

| Column | Description |
| --- | --- |
| **Ticker** | Security identifier. For bonds this is a full bond identifier (e.g. BACR V6.278 PERP); for equities it's the symbol. |
| **Venue** | Source / venue code the row is sourced from (e.g. TRACE for bond trades). |
| **Name** | Full instrument / issuer name. |
| **Last** | Current live price. Prefixed with a delay indicator if the feed is delayed. |
| **Chg** | Absolute change vs. previous close. Color-coded (green up / red down / gray no change). |
| **Time** | Time since last trade. |

**FIGI** and **ISIN** columns are implemented but currently hidden on every tab. They can be enabled server-side in the future without a client change.

### People tab

| Column | Description |
| --- | --- |
| **Name** | First + last name of the person |
| **Company** | Where they currently work |
| **Position** | Their title / role |
| **Email** | Contact email |
| **Phone** | Contact phone number |

**Paid users** see the actual values. **Anonymous and free (piker) users** see the Name, but the Company / Position / Email / Phone columns are **rendered blurred** with placeholder text: the real contact information is subscription-gated.

## Row Behavior

### Clicking an instrument row

Opens the context menu anchored at the click position. From there you can launch that instrument into any company-scoped command:

* [FOCUS](https://godelterminal.com/docs/commands/focus.html "FOCUS command reference"): concise live price
* [G](https://godelterminal.com/docs/commands/g.html "G command reference"): chart
* [DES](https://godelterminal.com/docs/commands/des.html "DES command reference"): company description
* [OMON](https://godelterminal.com/docs/commands/omon.html "OMON command reference"): options chain (for equities / ETFs)
* [N](https://godelterminal.com/docs/commands/n.html "N command reference"): news
* [CF](https://godelterminal.com/docs/commands/cf.html "CF command reference"): filings
* …and every other command that accepts a ticker.

### Clicking a person row

Triggers the people deeplink handler: opens that person's profile page. (Distinct from the instrument context menu.)

## Live Updates

Every visible instrument row subscribes to live price updates via websocket. Last / Chg / Time update continuously while the window is open: no need to refresh.

When you change filters (tab, query, venues, countries, max, toggle), the current subscriptions are torn down and a new search is issued. Any in-flight request from the old filter set is aborted, so you never see stale results bleed through.

## Practical Use Cases

### 1. "I need to find a specific corporate bond"

Bonds are hard to type directly into the terminal: use SECF with the **Corporate Bonds** tab, then search by issuer (e.g. Citigroup, Goldman) or by CUSIP fragment. Filter by Venue = TRACE to guarantee quotable results. Today this surfaces live quotes and TRACE prints; a full bond description with yield to maturity, call schedule, and more is coming soon.

### 2. "Every option chain available for a company"

Switch to the **Options** tab, query the underlying ticker, and scroll through the returned contracts. Click any row → context menu → [G](https://godelterminal.com/docs/commands/g.html "G command reference") to chart that specific contract.

### 3. "Looking up an analyst by name"

Switch to the **People** tab and type the name. Subscribers can see their current firm, title, and contact info; non-subscribers see the name only.

### 4. "What venues list this ticker?"

Search for the ticker on the **All** tab: the results surface one row per venue listing. For a deeper per-venue breakdown on a single known ticker, use [ALLQ](https://godelterminal.com/docs/commands/allq.html "ALLQ command reference") instead (it's designed specifically for that use case).

### 5. "What's tradable in a specific country?"

Filter **Countries** to the country of interest (e.g. JP for Japan), keep the query empty, and raise the **Max** to 500. Gives you a scrollable list of 500 instruments with live quotes to browse.

## Notes

* SECF is in **beta**: minor behaviors may change, and new tabs / columns may appear.
* The search input's ticker-search bar (visible on most other commands) is intentionally hidden on SECF: all filtering happens inside the window.
* Non-subscriber gating is specific to the **People** tab only. Instrument searches work fully for all account tiers.
* The **FIGI** and **ISIN** columns are code-present but UI-hidden. If you specifically need ISIN / CUSIP lookup today, the Corporate Bonds tab's free-text search matches against issuer name and ticker identifier.

## Related commands

* [QM Quote Monitor](https://godelterminal.com/docs/commands/qm.html)
* [DES Description](https://godelterminal.com/docs/commands/des.html)
* [ALLQ All Quotes](https://godelterminal.com/docs/commands/allq.html)

## FAQ

What does SECF do?

SECF is the Godel Terminal securities finder command.

How do I open SECF in Godel Terminal?

Type SECF in the terminal.

Is SECF available on all plans?

SECF is available to paid subscribers.

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

[Get a demo](https://godelterminal.com/docs/commands/secf#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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