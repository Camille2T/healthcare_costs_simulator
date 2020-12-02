# Healthcare costs simulator

This repository contains all the underlying data and code needed to build this Heroku app: <https://healthcare-costs-simulator.herokuapp.com/>  


## Why a healthcare costs simulator?

As a sector, healthcare represents 17% of US GDP, that's twice the average of other developed countries. This has very tangible consequences for American people especially for the 25 millions of them who are uninsured.

My app provides recommendations on where to receive medical care for a specific medical condition based on a declared place of living: it predicts the hospitals that bill the lowed while being rated at least 4 out of 5 by Medicare ([overall rating](https://www.medicare.gov/hospitalcompare/about/hospital-overall-ratings.html)). It uses data issued by the Center for Medicare and Medicaid Services to predict prices for more than 400 medical conditions in the 3100 Acute Care Hospitals in the United States.


## Data wrangling and preparation

### Data sources

**Centers for Medicare and Medicaid Services:**   

  - Medicare Provider Utilization and Payment Data: [Inpatient dataset 2017](https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Inpatient) (most recent available): provides information on inpatient discharges for Medicare fee-for-service beneficiaries. It includes information on utilization, payment (total payment and Medicare payment), and hospital-specific charges for the more than 3,000 U.S. hospitals
  - The [Hospital General Information](https://data.medicare.gov/Hospital-Compare/Hospital-General-Information/xubh-q36u) dataset is a list of all hospitals that have been registered with Medicare. It includes addresses, hospital ownership, and overall hospital rating.
- The [Hospital spending per beneficiary](https://data.medicare.gov/Hospital-Compare/Medicare-Spending-Per-Beneficiary-Hospital/rrqw-56er) index, built by Medicare Services shows whether Medicare spends more, less, or about the same for an episode of care at a specific hospital compared to all hospitals nationally.



**Local data (at county level):**

    - IRS: [statistics of income county data 2017](https://www.irs.gov/statistics/soi-tax-stats-county-data-2017)
    - United States Census Bureau: [County Population by Characteristics 2017](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html)
    - OpenDataSoft [US Zip Code Latitude and Longitude](https://public.opendatasoft.com/explore/dataset/us-zip-code-latitude-and-longitude/table/?flg=fr)
    - The Darthmouth institute for Health Policy & clinical practice: [ZIP code to HRR crosswalk file](https://atlasdata.dartmouth.edu/downloads/supplemental) captures the hospital referral regions (HRR).

### Data wrangling   

The ```Data Wrangling``` notebook presents all the performed operations to prepare the data.

The prepared data is stored in the ```Prepared_data``` file, it consists in three datasets:
- the inpatient dataset which stores all the price information and is organized by DRG (see definition here) and hospitals.
- the hospital dataset, which gathers all information at the hospital level
- the local dataset, which gathers all the relevant demographic and economic data at the county level by zipcode.

Some useful lists and dictionnaries are also stored in the ```Prepared_data``` file

## Models

I built four different models (see the ```Models``` notebook) on data availability. The most performant one achieves a prediction with an average error rate of 21% or  $ 12,700. All models use a custom made estimator made of a Linear Regression estimator with a Random Forest Estimator applied on the residuals.

## Visualizations

The ```Visualizations```  notebook displays 4 visualizations.


## Construction of the app

I started with this [github repository](https://github.com/thedataincubator/flask-framework/tree/docker) which contains a basic template for a Flask configuration that
works on Heroku.

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [Docker](https://docs.docker.com/)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [The Data Incubator](https://github.com/thedataincubator)
