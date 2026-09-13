# Adventure Works 2025 BI Solutions - Sponsor Usage Guide by McReg Analytics
- **Prepared By:** Group 3 3DSA1: CARLOS, Mikaela Angela, DAYAG, Drei Cerise, HABALUYAS, Althea Marie, and OLIVA, Maria Camela
- **Last Updated:** 09/2026

---
## WHAT?
- The dashboard provides an interactive view of how Adventure Works Cycle is performing across its two sales channels: Internet and Reseller. It is built to showcase high- and underperformance areas, analyze channels and the effectiveness of promotions, and enable faster, evidence-based decisions regarding pricing, production, and marketing focus.
- Full business case, findings, and recommendations are documented in the report files below.
---
## Repository Contents
 
| File | Description |
|---|---|
| `[dashboard-file-name].pbix` | The Power BI dashboard — covering Executive Overview, Channel Performance, Product Performance, Marketing Performance, Customer Insights, and Employee Evaluation. |
| `AdventureWorksDW2025_DataDictionary.csv` | Field-level data dictionary covering every column used in the model: source table, data type, business definition, and derivation logic. |
| `AdventureWorksDW2025_DataDictionaryCode.py` | Script used to help generate/populate the data dictionary. |
| `AdventureWorksDW2025_DataInventory.xlsx` | Source data profiling, such as row counts, data types, null rates, and other data quality observations gathered before modeling began. |
| `AdventureWorksDW2025_DataInventoryCode.py` | Script used to help generate the data inventory. |
| `McRegAnalytics_BusinessCase.pdf` | The approved business case: sponsor, problem statement, key business questions, and success measures. |
| `McRegAnalytics_DataDocumentation.pdf` | Full write-up of business context, methodology, key findings, action plan, and limitations/assumptions. |
| `McRegAnalytics_TechnicalDocumentation.pdf` | Technical detail on the data model: tables, relationships, measures (DAX), and calculated columns. |
| `README.md` | This file. |

---
## HOW?
- Download the `[dashboard-file-name].pbix` file from this repository and open it in **Power BI Desktop**; free and no sign-in is required to view a local file.

---
## Navigation

| Page | What it's for |
|---|---|
| **Home** | Starts here by default. An introduction of the team. |
| **Executive Overview** | The summary. Showcase company-wide revenue, profit, and the key Internet vs. Reseller channel comparison. |
| **Channel Performance** | A look at how Internet and Reseller channels compare on revenue, margin, and units sold. |
| **Product Performance** | Which products and categories drive revenue and profit, by quarter and region. |
| **Marketing Performance** | How discounts and promotions are used, and whether they're actually working. |
| **Customer Insights** | Overview of insights regarding discounts, demographics, income, occupation, and bundling potential. |
| **Employee Evaluation** | Sales team performance by tenure and revenue generated. |
 
**Interacting with charts:** click any slicer to filter the whole page; click a bar, bubble, or map point to highlight related data; hover over any chart for exact figures in a tooltip. 

## Interpretation
- **Executive Overview:** The headline, findings shows while Reseller Sales generates larger share of revenue, Internet Sales is more profitable.
- **Channel Performance:** confirms the revenue-vs-profit split seen on the Executive page and adds trend and unit-volume detail.
- **Product Performance:** the Revenue vs. Margin view shows that bikes drive the most revenue but carry the lowest margin, while accessories are the opposite.
- **Marketing Performance:** the majority of orders occur at full price; discounted orders don't show meaningfully different purchase behavior, and discounting is concentrated on the lowest-margin category.
- **Customer Insights:** identifies which customer segments are most valuable and which are the strongest candidates for accessory bundling.
- **Employee Evaluation:** tenure alone does not predict top sales performance.

---

## SCOPE AND LIMITATIONS
- Data covers **December 2010 through early 2014**
- Reseller Sales data ends approximately two months before Internet Sales data; charts comparing both channels are filtered to periods where both have complete data, to avoid misleading partial-period comparisons.
- This dashboard uses Microsoft's AdventureWorksDW2025 sample dataset as required coursework; all figures reflect that dataset and not live company data.
---

## CONTACT
| Contact |
|---|
| Project Lead - DAYAG, Drei Cerise  dreicerise.dayag.sci@ust.edu.ph |
| Data Engineering Owner - CARLOS, Mikaela Angela  mikaelaangela.carlos.sci@ust.edu.ph |
| Data Modeling Owner - OLIVA, Maria Camela  mariacamela.oliva.sci@ust.edu.ph |
| Visualization and Reporting Owner - HABALUYAS, Althea Marie  altheamarie.habaluyas.sci@ust.edu.ph |

---
*This guide accompanies the Adventure Works BI dashboard submitted for DS4157, Activity #1. AI assistance was used in the development of this project as disclosed in the accompanying written report.*


