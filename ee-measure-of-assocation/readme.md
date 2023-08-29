# Measure of Association (MOA) Analysis
It is a simple packages the uses pandas and matplotlib to calculate moa scores from sampled points and plot them.
plot the ranked predictors from the samples. 

The package is intended to be used with sampled points exported from Google Earth Engine. However it can be adapted to 
use any data source. As long as it is a csv of sampled observations

## Notes
- The package is still in development. It is not yet ready for production use.
- It **ONLY** supports csv's as input. It is not yet ready to be used with other data sources.

## Installation
### Clone the repo
```bash
git clone https://github.com/Wetlands-NWRC/earth-engine-scripts.git
```
```bash
cd ./earth-engine-scripts
```

### Setup Conda Environment
```bash
# set up the virtual environment
conda env create -n moa -c conda-forge pandas matplotlib build -y
```
```bash
# for development install
pip install -e .
```
### Build from source
```bash
# build from source
conda activate moa
```
```bash
(moa) $ python -m build
```
```bash
(moa) $ pip install dist/moa-0.0.1-py3-none-any.whl
```

## Simple Usage
```python
import pandas as pd
import moa

sampled_points = pd.read_csv('sampled_points.csv')
moa_gen = moa.MoaScoreGenerator(
    sampled_data=sampled_points, # the samples
    label_col='label', # the label column  for
)

# generates the moa scores
moa_scores = moa_gen.generate_scores()

# get predictor ranks 
moa_ranks = moa_scores.get_by_rank(1)

# generate plots -> writes plots to disk
moa.plot_predictors(
    samples=sampled_points, # the samples
    label_col='class_name',
    ranks=moa_scores, # the moa scores
    out_dir='plots' # the output directory
)



```