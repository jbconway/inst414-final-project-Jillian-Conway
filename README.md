# Bird Conservation Resource Allocation – Final Project Part 2 (INST414)

## Project Overview

This project analyzes bird population data in Maryland from 2010 to 2023 to inform conservation resource allocation. The goal is to identify where bird species are most abundant and how their habitats overlap to help optimize conservation efforts.

### Business Problem

Current conservation resource allocation can be inefficient due to a lack of actionable population and distribution data. This project uses eBird datasets to understand abundance trends and spatial overlap among three species of interest in Maryland.

### Data Sets Used

1. **eBird Basic Dataset (EBD)**  
   - Source: Cornell Lab of Ornithology  
   - Contains raw bird observation data including species, date, location, and observer metadata  
   - Accessed by submitting a data request and downloading as `.txt`

2. **Status and Trends Data Products**  
   - Structured CSV files generated from the EBD using statistical models  
   - Includes spatial and seasonal population summaries like `abundance_mean`, `total_pop_percent`, and `season`  
   - Downloaded for the three selected bird species across Maryland

These datasets are placed in a folder named after the source (`cornell_bird_data`) and are included in the project package. Note that these were downloaded once after submitting access requests and are tracked via Git Large File Storage (Git LFS). Both datasets are used to explore where species are abundant and how their habitats overlap spatially. Data were subset to Maryland from 2010–2023 and include Northern Cardinal, American Woodcock, and Osprey.

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

### 6. Git Config
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

 - Performing descriptive analysis and generating summary statistics

 - Creating visualizations such as abundance histograms and bird location maps

 - All outputs (processed data, analysis results, and visualizations) will be saved in the appropriate data/ subfolders.


## Code Package Structure
```bash
inst414-final-project-Jillian-Conway/
│
├── data/
│   ├── analyzed/                # Descriptive output files (e.g., plots)
│   ├── extracted/               # Cleaned data from EBD
│   ├── processed/               # Joined and transformed final data
│   ├── outputs/                 # Final visualizations
│   ├── shapefiles/              # Shapefile for Maryland boundaries
│   └── reference-tables/        # Additional reference tables used in analysis
│
├── cornel_bird_data/            # Raw data from Cornell (EBD + Status & Trends)
│   ├── ebd_ds/
│   └── trends_and_status_ds/
│
├── etl/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── vis/
│   └── visualizations.py        # Mapping and abundance plots
│
├── analysis/                    # Analysis and modeling scripts
│   ├── evaluate.py             # Descriptive analytics
│   └── model.py                # Modeling code 
│
├── main.py                     # Project entry point
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```


## Techniques Employed
- Descriptive statistics (counts, means, distributions)

- Geospatial visualization (using GeoPandas and matplotlib)

- Data transformation and cleaning using pandas

- Reproducible pipeline-based structure (ETL → Evaluation → Visualization)

## Additional Notes and Contact
Notes:

Some .csv and .txt files exceed GitHub’s 100MB file limit, so Git LFS is required.

Be sure to run git lfs pull after cloning to retrieve the large data files.

Contact: 

Jillian Conway

INST414 – Final Project Part 2

University of Maryland
