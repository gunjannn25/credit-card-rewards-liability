**Credit Card Rewards Liability & Redemption Analytics: Quantifying $1.32K of Modeled Outstanding Rewards Liability and Its Key Drivers**

**What This Project Actually Delivered**
This project converted 19,963 raw credit-card transactions into a transaction-level rewards-liability model and then used SQL, Python, Excel, and Tableau to explain the resulting exposure.

**The most useful outputs were:**
- Quantified an estimated $1,319.10 of outstanding rewards liability from the modeled transaction population.
- Identified that Retail, Grocery, Travel, and Other collectively drive 86.90% of modeled liability, giving a clear view of where rewards exposure is concentrated.
- Identified Card 3 as the largest liability contributor, representing 55.27% of modeled liability.
- Built a 24-month redemption-development framework to estimate how outstanding rewards decline as points mature and are redeemed.
- Performed sensitivity analysis around the 92% baseline redemption assumption, showing modeled liability ranging from $1,262.13 at 88% URR to $1,376.49 at 96% URR.
- Built monthly liability and variance analysis to provide a framework for monitoring how the modeled exposure changes over time.
- Converted the analysis into an executive Tableau dashboard so a finance/rewards stakeholder can move from the overall liability estimate to its major drivers and scenario sensitivity.


****1. Business Problem****
Credit card rewards create a future financial obligation because points earned today may be redeemed later. Finance, rewards, and analytics teams need to understand how much rewards liability may remain outstanding, which spending segments are driving that liability, and how sensitive the estimate is to redemption assumptions.
This project builds a transaction-level rewards-liability model and analyzes redemption development, liability concentration, card-level segmentation, monthly trends, variance, and sensitivity to ultimate redemption assumptions.
Important: The underlying transaction dataset is synthetic/public transaction data. Rewards issuance, redemption behavior, point cost, and ultimate redemption assumptions are modeled and are not issuer-confidential or observed American Express data.

**2. Dataset**
The project uses the IBM Synthetic Credit Card Transactions dataset available through Kaggle.
The working dataset contains 19,963 transaction records across 5 cards for 1 synthetic user, covering September 2002 to February 2020.
Dataset	Rows	Columns	Key Fields
Credit Card Transactions	19,963	15	User, Card, Year, Month, Day, Amount, MCC, Merchant City, Merchant State, Fraud, Errors


**Key source fields**
- User
- Card
- Year
- Month
- Day
- Amount
- Use Chip
- Merchant Name
- Merchant City
- Merchant State
- Zip
- MCC
- Errors?
- Is Fraud?
Data classification
Observed / sourced
- Transaction date
- Transaction amount
- Card ID
- MCC
- Merchant information
- Fraud/error indicators
Derived
- Spend category
- Points issued
- Transaction age
- Monthly aggregations
- Card-level metrics
- Category-level liability
- Cohort/development outputs
Modeled
- Ultimate Redemption Rate: 92%
- Weighted Average Cost per Point: $0.01
- Redemption development period: 24 months
- Expiry flag: 36 months
The rewards model explicitly defines these assumptions as modeled rather than observed issuer data.

**3. Tools Used**
- Python: pandas, NumPy — data inspection, cleaning, feature engineering, exploratory analysis, statistical analysis, rewards-liability modeling, and cohort outputs
- SQL / MySQL Workbench: CTEs, joins, window functions, segmentation, Pareto analysis, monthly trend/variance analysis, cohort development, and sensitivity analysis
- Excel: KPI summary, monthly trend, category analysis, card segmentation, development analysis, liability analysis, and sensitivity analysis
- Tableau: interactive executive dashboard, liability trend, category analysis, card-level analysis, and redemption-rate sensitivity visualization
- GitHub: project documentation and portfolio publication
**4. Approach**
**1. Data Inspection & Cleaning**
Python was used to inspect and standardize the raw transaction data.
Key steps included:
- Constructing a standardized transaction date from Year, Month, and Day
- Converting transaction amounts into numeric USD values
- Identifying fraud and error flags
- Handling missing merchant-state and ZIP values
- Removing exact duplicate transactions
- Standardizing downstream analytical fields
The cleaned dataset was then used as the foundation for the rewards-liability model.
**2. Spend Classification & Reward Modeling**
Merchant Category Codes (MCCs) were mapped into analytical spending categories:
- Travel
- Dining
- Grocery
- Fuel
- Retail
- Other
Modeled reward earn rates were then applied by category:
Spend Category	Modeled Points / $
Travel	3
Dining	2
Grocery	2
Fuel	1
Retail	1
Other	1

Points issued were calculated from transaction spend × modeled points-per-dollar.
**3. Rewards Liability Modeling**
A transaction-level rewards model was created using:
Ultimate expected redemption
Points Issued × 92%

Modeled redemption to date
Ultimate Expected Redemption × Development Percentage

Outstanding rewards
Ultimate Expected Redemption − Modeled Redeemed Points

Estimated liability
Outstanding Expected Redemption Points × $0.01

The redemption curve develops linearly over 24 months, with the model capped at the 92% ultimate redemption assumption.
These assumptions are explicitly labeled as MODELED in the project.

**4. SQL Analysis**
The modeled transaction data was loaded into MySQL for business analysis.
SQL analysis included:
- Executive KPI aggregation
- Card-level segmentation
- Spend-category liability analysis
- Pareto analysis
- Monthly liability trend
- Month-over-month liability variance
- Redemption development analysis
- Ultimate redemption-rate sensitivity analysis
- Window functions and CTE-based analytical queries
- 
**5. Business Analysis**
The project applies several business-analysis techniques:
- Segmentation: card-level liability concentration
- Pareto analysis: spend categories driving liability
- Trend analysis: monthly liability movement
- Variance analysis: month-over-month liability changes
- Cohort/development analysis: modeled redemption development
- Sensitivity analysis: impact of different ultimate redemption assumptions
- KPI analysis: spend, points issued, outstanding points, and modeled liability
  
**6. Visualization**
The Tableau dashboard focuses on four core views:
- Monthly Modeled Rewards Liability
- Modeled Rewards Liability by Spend Category
- Modeled Rewards Liability by Card
- Estimated Liability Sensitivity to Ultimate Redemption Rate
The dashboard is designed as an executive view of the modeled rewards-liability exposure and its primary drivers.
**5. Key Insights**
1. $1.32K of modeled rewards liability
The model produces:
- 19,963 transaction records
- $1,622,991.69 total transaction spend
- 2,204,320 modeled points issued
- $1,319.10 estimated outstanding rewards liability
The liability is a modeled estimate, based on the 92% ultimate redemption assumption and $0.01 modeled point cost.
2. Liability is concentrated in a small number of spend categories
The four largest categories — Retail, Grocery, Travel, and Other — account for approximately 86.90% of modeled liability.
Spend Category	Modeled Liability	Liability Share
Retail	$392.27	29.74%
Grocery	$365.17	27.68%
Travel	$228.21	17.30%
Other	$160.59	12.17%
Dining	$102.91	7.80%
Fuel	$69.95	5.30%
This concentration makes spend-category monitoring useful for understanding the modeled liability base.
3. Card-level exposure is concentrated
Card 3 accounts for approximately 55.27% of modeled liability.
The remaining modeled liability is distributed across the other four cards, indicating that card-level segmentation can identify concentrated rewards exposure even within the same transaction portfolio.
4. The liability estimate is sensitive to ultimate redemption assumptions
Using the same transaction population and modeled point cost:
Ultimate Redemption Rate	Estimated Liability
88%	$1,262.13
90%	$1,290.66
92%	$1,319.10
94%	$1,347.96
96%	$1,376.49
The modeled liability increases as the assumed ultimate redemption rate increases.
The 92% scenario is the project's baseline, rather than an observed issuer redemption rate.
5. Redemption development drives the timing of outstanding liability
The model assumes redemption develops over a 24-month period, meaning younger rewards cohorts retain more outstanding expected redemptions while older cohorts approach the modeled ultimate redemption level.
This provides a framework for analyzing how the timing of redemption affects outstanding rewards exposure.
**6. Recommendations**
1. Monitor rewards liability by spending category to identify categories contributing disproportionately to modeled exposure.
2. Track card-level concentration to identify accounts/cards contributing materially to outstanding rewards.
3. Perform scenario analysis on redemption assumptions rather than relying on a single point estimate.
4. Refresh the liability model periodically as new transaction and redemption information becomes available.
5. Separate observed data from modeled assumptions when communicating liability estimates to finance or business stakeholders.
6. Use monthly variance monitoring to identify material changes in modeled liability and investigate the underlying transaction or redemption drivers.
7. Where actual issuer redemption and cost data become available, replace modeled assumptions with observed experience and recalibrate the liability model.
**7. Dashboard**
The Tableau dashboard contains:
Executive views
- Monthly Modeled Rewards Liability
- Modeled Rewards Liability by Spend Category
- Modeled Rewards Liability by Card
- Ultimate Redemption Rate Sensitivity
Key dashboard questions
- How is modeled liability changing over time?
- Which spending categories contribute most to liability?
- Which cards have the highest modeled exposure?
- How much does the liability estimate change under different redemption assumptions?

**Important Modeling Limitations**
- The transaction dataset is synthetic/public data, not proprietary issuer data.
- The dataset contains one synthetic user and five cards; therefore, segmentation in this project is primarily card-level, not customer-level.
- Rewards issuance and redemption histories are not present in the source transaction data.
- The 92% ultimate redemption rate is modeled, not an observed issuer-specific rate.
- The $0.01 cost per point is modeled, not an issuer-reported value.
- The 24-month redemption development curve is a modeling assumption.
- The 36-month expiry flag is a modeled program assumption and should not be interpreted as a statement about any specific card issuer's rewards-expiration policy.
- The liability estimate should therefore be interpreted as a scenario-based analytical model, not a financial statement liability.

Name: Gunjan Aggarwal gmail: gunjan250103@gmail.com
