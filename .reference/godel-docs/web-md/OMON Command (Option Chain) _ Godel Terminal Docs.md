ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/omon#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousEQSEquity Screener](https://godelterminal.com/docs/commands/eqs.html)[NextOVMEBlack-Scholes→](https://godelterminal.com/docs/commands/ovme.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
OMON

# OMON: Option Chain Command

OMON is the Godel Terminal command for viewing the real-time options chain of a security: every strike and expiration with live bid, ask, last, volume, IV, and the full set of Greeks.

[![](../../assets/docs/omon/omon-01.png)](../../assets/docs/omon/omon-01.webm)

## Aliases

OPT, CALL, and PUT are all aliases for OMON: they open the same options chain. OPT was the legacy mnemonic (pre-2025); OMON is now the canonical shortcut. Any of the four will work in the terminal.

## How to use OMON

**Security Identifier/Ticker Country/Instrument Asset Class OMON**

Example: AAPL US EQ OMON: opens the Apple options chain.

**Aliases:** OPT, CALL, and PUT all map to OMON.

## Modes

The mode selector in the quick-settings bar switches what the table shows:

* **Both**: Calls on the left, Puts on the right, with the strike column in the center.
* **Calls**: calls-only view with full column depth.
* **Puts**: puts-only view with full column depth.

Each mode remembers its own column order and greeks selection.

## Navigation Menu

Controls at the top of the window:

* **Expiration** dropdown: pick the expiration cycle to view. Left and right arrows step through cycles.
* **Months out**: how many months forward to request.
* **Strikes above** / **Strikes below**: how many strikes above / below the current spot to render (each defaults to 10).
* **QuickQuote** chip: live price of the underlying.

Changes to the navigation menu are debounced into the window props (≈300 ms) so rapid adjustments don't fire a flurry of API calls.

## Display Columns

The default column set (per side):

| Column | Description |
| --- | --- |
| **Last** | Last trade price for the contract (seriesValue.value) |
| **Bid** | Best bid |
| **Ask** | Best ask |
| **Volume** | Today's contract volume |
| **IV** | Implied volatility |
| **Delta** | Price sensitivity to underlying ($1 move) |
| **Gamma** | Rate of change of delta |
| **Vega** | Sensitivity to volatility |
| **Theta** | Time decay |
| **Rho** | Sensitivity to interest rate |
| **Lambda** | Price elasticity |
| **Epsilon** | Dividend sensitivity |

### Column management

* **Greeks selector** (quick-settings bar): toggle which greeks you want visible. Your selection is packed into a compact bitmask and stored per mode.
* **Drag column headers** to reorder them. On the Both mode, calls and puts have their own ordered sets so the layout is symmetric around the strike.
* **Resize** columns by dragging their right edge.

## Live Price Row

Between the ITM and OTM sides of the chain, a highlighted band in your primary theme color shows Last Price: x.xx so the underlying spot is always visible in context.

## Click a Contract

Click any strike / contract cell to open the context menu. From there you can launch the contract into [FOCUS](https://godelterminal.com/docs/commands/focus.html "FOCUS command reference"), [G](https://godelterminal.com/docs/commands/g.html "G command reference") (as an option chart), or [OVME](https://godelterminal.com/docs/commands/ovme.html "OVME command reference") (to pull the pricing + Greeks into the Black-Scholes calculator).

## Empty State

If no options data is available for the security (e.g. the ticker has no listed options), the table shows "No options data found for [ticker]".

## Notes

* OMON replaces the legacy OPT command: they are now the same component.
* Options data is streamed via websocket, so rows update live as quotes change.

## Related commands

* [G Chart](https://godelterminal.com/docs/commands/g.html)
* [DES Description](https://godelterminal.com/docs/commands/des.html)
* [TAS Time and Sales](https://godelterminal.com/docs/commands/tas.html)
* [OVME Black-Scholes](https://godelterminal.com/docs/commands/ovme.html)

## FAQ

What does OMON do?

OMON is the Godel Terminal option chain command.

How do I open OMON in Godel Terminal?

Type OMON in the terminal, or prefix with a ticker (for example, NVDA US EQ OMON).

Is OMON available on all plans?

Yes, OMON is available on every Godel plan.

Does OMON work for ETFs, indices, or non-US securities?

Yes. OMON loads the options chain for any optionable security, including ETFs and index options.

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

[Get a demo](https://godelterminal.com/docs/commands/omon#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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