# Data

The school-load scripts in `analysis/` use the **Building Data Genome 2** dataset (Miller et al. 2020, *Scientific Data* 7, 368; CC BY 4.0): hourly meter readings for 1,636 non-residential buildings, 2016–2017.

Download two files from the [BDG2 repository](https://github.com/buds-lab/building-data-genome-project-2) into `data/bdg2/`:

- `metadata.csv` (from `data/metadata/`)
- `electricity_cleaned.csv` (from `data/meters/cleaned/`, about 175 MB)

Or point `BDG2_DIR` at a folder that already has them. The 194 buildings tagged as K-12 or primary/secondary schools are mostly in Washington DC (site "Rat") and Cardiff, UK (site "Lamb").
