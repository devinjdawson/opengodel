ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/allq#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousHALTMarket Halts](https://godelterminal.com/docs/commands/halt.html)[NextSECFSecurities Finder→](https://godelterminal.com/docs/commands/secf.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
ALLQ

# ALLQ: All Quotes Command

ALLQ is the Godel Terminal command for viewing every related listing of a security across venues and exchanges: live bid, ask, last, and volume on each line.

![ALLQ All Quotes window for AAPL US showing the expandable share-class / composite / venue tree with ISIN headers and live Last, Chg, Chg%, Volume, Time, and Bid/Ask columns across global venues](./ALLQ Command (All Quotes) _ Godel Terminal Docs_files/allq-hero.png)

## How to use ALLQ

**Security Identifier/Ticker Country/Instrument Asset Class ALLQ**

Example: AAPL US EQ ALLQ: lists every venue and composite listing related to Apple Inc.

![Godel Terminal command bar showing AAPL US EQ ALLQ typed with the COMMANDS autocomplete suggesting 'Find related instruments to a security and get all their quotes'](./ALLQ Command (All Quotes) _ Godel Terminal Docs_files/allq-01.png)

Results are grouped into an expandable tree:

* **Level 1**: Share class (with ISIN). Click the ▶ / ▼ arrow to collapse or expand the whole group.
* **Level 2**: Composite listing. Shows consolidated quote data for the composite row itself.
* **Level 3**: Individual venue rows nested under the composite.

## Display Columns

| Column | Description |
| --- | --- |
| **Ticker** | Security identifier on the venue |
| **Venue** | Source / venue code |
| **Exchange** | Listing exchange name |
| **Last** | Current price (prefixed with a delay indicator if the feed is delayed) |
| **Chg** | Absolute change from previous close |
| **Chg%** | Percentage change from previous close |
| **Volume** | Today's share volume |
| **Time** | Time since last trade |
| **Bid / Ask** | Live best bid and ask with sizes, formatted B <bid>x<bidSize> / <ask>x<askSize> A |

Change, change %, last, volume, and time are color-coded using your positive / negative color settings.

## Controls

* **Active quotes only** (top-right toggle): hides any row that does not have both a live bid and ask. Turned on by default so you only see venues that are actually quoting.
* **Click a ticker row**: opens the context menu to jump that instrument into other commands (e.g. [FOCUS](https://godelterminal.com/docs/commands/focus.html "FOCUS command reference"), [G](https://godelterminal.com/docs/commands/g.html "G command reference"), [OMON](https://godelterminal.com/docs/commands/omon.html "OMON command reference")).

![ALLQ window with the Active-quotes-only toggle in the top-right and an open right-click context menu on an APC row showing Q (Launch Quote in Terminal), G (Open Graph), DES (Security Description), and FOCUS (Create FOCUS Element)](./ALLQ Command (All Quotes) _ Godel Terminal Docs_files/allq-context.png)

## Notes

* ALLQ is in beta.
* Bid / ask data is gated: anonymous users see "Register to see bid / ask" in place of the quote.
* The delay indicator (D) appears next to the **Last** price for any row fed from a delayed source.

## Related commands

* [QM Quote Monitor](https://godelterminal.com/docs/commands/qm.html)
* [SECF Securities Finder](https://godelterminal.com/docs/commands/secf.html)
* [DES Description](https://godelterminal.com/docs/commands/des.html)

## FAQ

What does ALLQ do?

ALLQ is the Godel Terminal all quotes command.

How do I open ALLQ in Godel Terminal?

Type ALLQ in the terminal, or prefix with a ticker (for example, NVDA US EQ ALLQ).

Is ALLQ available on all plans?

Yes, ALLQ is available on every Godel plan.

Does ALLQ work for ETFs, indices, or non-US securities?

Yes. ALLQ works for ETFs, indices, and non-US securities, not just US stocks.

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

[Get a demo](https://godelterminal.com/docs/commands/allq#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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