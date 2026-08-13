ProductCustomers[Pricing](https://godelterminal.com/pricing/)[Documentation](https://godelterminal.com/docs.html)[Careers](https://godelterminal.com/careers.html)[News](https://godelterminal.com/news.html)[Get a demo](https://godelterminal.com/docs/commands/gr#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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

[←PreviousSIShort Interest](https://godelterminal.com/docs/commands/si.html)[NextANRAnalyst Ratings→](https://godelterminal.com/docs/commands/anr.html)

[Docs](https://godelterminal.com/docs.html)/
[Commands](https://godelterminal.com/docs.html#commands)/
GR

# GR: Ratio Analysis Command

GR is the Godel Terminal command for graphing the relationship between two securities over time: ratios, spreads, or correlations.

![GR Ratio Analysis window for NVDA vs SPY showing the price comparison chart, NVDA/SPY ratio mountain chart, rolling correlation panel, and a regression scatter plot with Beta, Alpha, R², and standard error statistics](./GR Command (Ratio Analysis) _ Godel Terminal Docs_files/gr-hero.png)

## How to use GR

**Global (default):**

GR: opens with AAPL vs. SPY as the default pair.

![Godel Terminal command bar showing GR typed with the COMMANDS autocomplete suggesting 'Graph Relationship between two securities over time'](./GR Command (Ratio Analysis) _ Godel Terminal Docs_files/gr-01.png)

**Scoped:**

**Security Identifier/Ticker Country/Instrument Asset Class GR**

Opens with the scoped ticker as the "buy" leg.

![Godel Terminal command bar showing NVDA US EQ GR typed with the COMMANDS autocomplete suggesting 'Graph Relationship between two securities over time'](./GR Command (Ratio Analysis) _ Godel Terminal Docs_files/gr-02.png)

## Tickers

At the top of the window:

* **Buy**: the primary / numerator ticker.
* **Sell**: the comparison / denominator ticker.

Use the inline ticker search next to each to swap either leg. Any pair of the same asset class (equity, ETF, FX, index, futures, crypto) can be compared.

## Time Period

Dropdown with presets: **1D, 1W, 1M, 3M, 6M, 1Y**, and longer windows where data is available.

## Panels

### Price Comparison Chart

A dual-axis time series with both tickers plotted on their own y-scale. Legend shows the most recent price for each side; highs and lows for the selected period are marked on the chart.

### Ratio Chart

A mountain chart of Buy / Sell. Useful for spotting mean-reversion and persistent drifts in the relationship.

### Correlation (optional)

Toggle **Correlation** on to add a rolling-correlation chart below the ratio. Configure the window length (default 120 observations, min 2, max 730) using the inline input + **Set** button.

### Regression (optional)

Toggle **Regression** on to add a scatter plot of Buy returns vs. Sell returns with an OLS fit. The regression panel provides:

| Stat | Meaning |
| --- | --- |
| **Beta** | Slope of Buy returns regressed on Sell returns |
| **Adjusted Beta** | Shrinkage-adjusted beta |
| **Alpha** | Regression intercept |
| **R²** | Explained variance |
| **r** | Pearson correlation |
| **Std Error (α, β)** | Standard errors of the intercept and slope |
| **T-test / p-value** | Most recent significance test |

When the dataset is very large, the scatter plot is sampled using an inverse-normal-weighted scheme to preserve tails. A **Show Full Data** / **Show Filtered Data** toggle switches between the downsampled view and the full set.

## Notes

* Missing data points on either side are aligned and filled forward where sensible.
* Correlation and regression windows share the same underlying time series; changing either toggles refreshes both panels.

## Related commands

* [G Chart](https://godelterminal.com/docs/commands/g.html)
* [HMS Historical Multiple Security](https://godelterminal.com/docs/commands/hms.html)
* [HP Historical Prices](https://godelterminal.com/docs/commands/hp.html)

## FAQ

What does GR do?

GR is the Godel Terminal ratio analysis command.

How do I open GR in Godel Terminal?

Type GR in the terminal, or prefix with a ticker (for example, NVDA US EQ GR).

Is GR available on all plans?

Yes, GR is available on every Godel plan.

Does GR work for ETFs, indices, or non-US securities?

Yes. GR works for ETFs, indices, and non-US securities, not just US stocks.

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

[Get a demo](https://godelterminal.com/docs/commands/gr#demo)[Login](https://app.godelterminal.com/?page=login)[Sign Up](https://app.godelterminal.com/?page=register)

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