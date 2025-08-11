# Bird Conservation Resource Allocation – Final Project Part 3 (INST414)

## Project Overview

This project uses bird population data from 2010 to 2023 in Maryland to support better conservation planning through predictive analytics. By modeling abundance trends for three bird species—osprey, American woodcock, and northern cardinal—I aimed to forecast where each species is most likely to be found in high numbers. These predictions help conservation organizations prioritize areas for habitat protection and resource allocation. The analysis combines observational data with modeled estimates to identify meaningful patterns in abundance and reveal where efforts may have the greatest impact now and in the future.

### Business Problem

Current conservation resource allocation can be inefficient due to a lack of actionable population and distribution data. This project uses eBird datasets to develop a **predictive model** that estimates whether a specific region contains a significant portion of a bird species’ population, based on environmental and temporal variables. These predictions help target areas that may warrant conservation attention.

### Data Sets Used

1. **eBird Basic Dataset (EBD)**  
   - Source: Cornell Lab of Ornithology  
   - Contains raw bird observation data including species, date, location, and observer metadata  
   - Accessed by submitting a data request and downloading as `.txt`

2. **Status and Trends Data Products**  
   - Structured CSV files generated from the EBD using statistical models  
   - Includes spatial and seasonal population summaries like `abundance_mean`, `total_pop_percent`, and `season`  
   - Downloaded for the three selected bird species across Maryland


These datasets are placed in a folder named after the source (`cornell_bird_data`) and are included in the project package. Here is the link to the website: https://science.ebird.org/en/use-ebird-data/download-ebird-data-products. Note that these were a one-time download after submitting access requests and are tracked via Git Large File Storage (Git LFS). Data were subset to Maryland from 2010–2023 and include Northern Cardinal, American Woodcock, and Osprey.

---

## Setup Instructions

Follow these steps to set up the environment and prepare the project for use.

### 1. Clone this repository

```bash
git clone https://github.com/jbconway/inst414-final-project-Jillian-Conway.git
cd inst414-final-project-Jillian-Conway
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
On Windows: 

```bash
venv\Scripts\activate
```

On Mac/Linux

```bash
source venv/bin/activate
```

### 4. Install required packages
```bash
pip install -r requirements.txt
```

### 5. Set up Git LFS (Large File Storage)
This project includes large CSV and TXT files (>100MB) that cannot be stored directly on GitHub without LFS.

```bash
git lfs install
git lfs pull
```
This ensures that large data files referenced in the repo are correctly downloaded.

### 6. Git Config (this step only applies if you would be commiting new datasets to this project)
.gitignore excludes files and folders that should not be tracked by Git, such as the virtual environment folder:

```bash
venv/
```

.gitattributes configures Git LFS to track large data files, including:
```bash
*.csv filter=lfs diff=lfs merge=lfs -text
*.txt filter=lfs diff=lfs merge=lfs -text
cornel_bird_data/ebd_ds/*.txt filter=lfs diff=lfs merge=lfs -text
data/extracted/*.csv filter=lfs diff=lfs merge=lfs -text
data/processed/*.csv filter=lfs diff=lfs merge=lfs -text
```

## Running the Project

### Run the full pipeline

Simply run:

```bash
python main.py
```

This command will execute the entire workflow, including:

- Extracting, transforming, and loading the raw bird data

- Training a Random Forest regression/classification model to predict bird abundance or abundance category (high/low) in regions
    - Handling limited variability in target variables by binarizing abundance (high/low)
    - Model evaluation using metrics like R², MSE, accuracy, and confusion matrix heatmaps

- Saving visualizations and evaluation metrics to the data/analyzed/ directory 


## Code Package Structure
```bash
inst414-final-project-Jillian-Conway/
│
├── data/
│   ├── analyzed/               # Model evaluation outputs (e.g., confusion matrix)
│   ├── extracted/              # Cleaned data from EBD
│   ├── processed/              # Joined and transformed final data
│   ├── outputs/                # Final visualizations (maps, plots)
│   ├── shapefiles/             # Shapefile for Maryland boundaries
│   └── reference-tables/       # Data dictionaries and lookup tables
│
├── cornel_bird_data/           # Raw data from Cornell (EBD + Status & Trends)
│   ├── ebd_ds/
│   └── trends_and_status_ds/
│
├── etl/
│   ├── extract.py              # Read and subset raw datasets
│   ├── transform.py            # Clean and merge datasets
│   └── load.py                 # Save processed data
│
├── vis/
│   └── visualizations.py       # Geospatial maps of sightings
│
├── analysis/
│   ├── model.py                # Predictive model (logistic regression)
│   └── evaluate.py             # Evaluation metrics and output saving
│
├── main.py                     # Project entry point
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md

```


## Techniques Employed

- Predictive analytics using logistic regression

- Feature engineering based on seasonal and abundance trends

- Model evaluation based on calculated accuracy values

- Data cleaning and transformation using pandas

- Mapping and geospatial visualization using GeoPandas and matplotlib

- Pipeline-based structure: ETL → Modeling → Evaluation → Visualization

## Expected Outputs

- Processed Data Files
    - Cleaned, merged, and transformed datasets stored in data/processed/ ready for analysis.

- Model Artifacts and Evaluation
    - Trained regression models and evaluation metrics (MSE, MAE, R²) saved in data/analyzed/, including CSV summaries of model performance.

- Visualizations

    - Spatial maps of bird sightings by species in data/outputs/

    - Confusion matrix heatmaps and evaluation plots reflecting binary abundance classification

- Logs and Reports (coming soon)
    - Console output showing progress and key results during pipeline runs.


## Additional Notes and Contact
Notes:

- Some .csv and .txt files exceed GitHub’s 100MB file limit, so Git LFS is required.

- Due to eBird’s data access policy requiring a formal request and the large size of the full datasets, only a limited subset of the data was downloaded (primarily from 2023). This constraint may affect the breadth and variability of the analysis results.

- Be sure to run git lfs pull after cloning to retrieve the large data files.

Contact: 

Jillian Conway

INST414 – Final Project Part 2

University of Maryland
