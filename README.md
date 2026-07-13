# DTIDistance

Tools for comparing whole-brain FA (fractional anisotropy) and MD (mean diffusivity) maps derived from diffusion tensor imaging (DTI) scans, using histogram distance metrics. The pipeline pulls candidate subjects from radiology reports, processes raw DICOMs into thresholded FA/MD maps, converts those maps into histograms, and computes a battery of distance/divergence metrics (city-block, Euclidean, Chebyshev, fidelity, Hellinger, squared-chord, intersection, Canberra, Lorentzian, cosine, squared chi-squared, Kullback-Leibler, Jeffreys) between them — for example, to see whether scans from different scanners, manufacturers, or acquisition parameters are statistically distinguishable. This also serves as a novel data quality metric for diffusion MRI data. We implemented this in an online neuoroimaging database where it automatically rated each DTI image on a scale of 1-5 based on the Hellinger histogram distance without the need for human assessment.

This code was used to produce the analysis in:

> Warner GC, Helmer KG (2018). *Characterization of Diffusion Metric Map Similarity in Data From a Clinical Data Repository Using Histogram Distances.* Front. Neurosci. 12:133. doi: [10.3389/fnins.2018.00133](https://doi.org/10.3389/fnins.2018.00133)

The version at the top level of this repo has been refactored from the original analysis code for readability and reuse. The exact code used to generate the results in the paper is preserved in [`legacy_code/`](legacy_code).

## Requirements

This is Python 2 research code (not packaged, no `requirements.txt`), so dependencies need to be installed manually:

- Python 2.7
- [`pydicom`](https://pydicom.github.io/) (imported as `dicom`, old pre-1.0 API)
- [`nibabel`](https://nipy.org/nibabel/)
- `numpy`
- `matplotlib`
- [FSL](https://fsl.fmrib.ox.ac.uk/) — `eddy_correct`, `bet`, `fslmaths` are called via `subprocess`
- [`dcm2nii`](https://www.nitrc.org/projects/dcm2nii/) — DICOM to NIfTI conversion
- [DCMTK](https://dicom.offis.de/dcmtk.php.en) — `dcmdjpeg` / `dcmdrle` for decompressing compressed DICOMs

FSL, `dcm2nii`, and DCMTK are invoked as external command-line tools and must be on your `PATH`.

## Pipeline

The scripts are meant to be run in order, editing paths/parameters in each file before running (most scripts have hardcoded input/output paths near the top rather than a command-line interface):

1. **Retrieve radiology reports** from the Research Patient Data Registry (RPDR) or an equivalent clinical data source.

2. **Filter for healthy, diffusion-relevant scans.** Use `FindHealthyDti` in [`GetData/filterHealthyDtiFromRadiologyReports.py`](GetData/filterHealthyDtiFromRadiologyReports.py) to exclude reports flagging physiological abnormalities or lacking diffusion data, and to compile the medical record numbers (MRNs) for the remaining, relevant subjects.

3. **Retrieve imaging data** for those MRNs from your data warehouse (e.g. i2b2).

4. **Convert and process DTI data.** Use `DataSet` in [`ProcessDtiData/processDtiData.py`](ProcessDtiData/processDtiData.py) to decompress raw DICOMs, filter out non-DTI series, convert to NIfTI, drop datasets with broken/invalid b-values or b-vectors, run eddy correction + b-vector rotation + skull stripping + tensor reconstruction (via [`DiffRecon_Rotate_B_Matrix.sh`](ProcessDtiData/DiffRecon_Rotate_B_Matrix.sh) and [`fdt_rotate_bvecs.sh`](ProcessDtiData/fdt_rotate_bvecs.sh)), and generate thresholded FA/MD maps.

5. **Calculate histogram distances.**
   - For comparisons across two or more independent variables (e.g. GE data, 30 gradient directions, 1.5T field strength), edit and run [`CalculateDistances/specific_hist_dist_csv.py`](CalculateDistances/specific_hist_dist_csv.py).
   - For comparisons on a single independent variable (e.g. all data with a b-value of 1000), edit and run [`CalculateDistances/hist_dist_between_csv.py`](CalculateDistances/hist_dist_between_csv.py).

6. **Generate histogram summaries.** Edit and run [`MakeHistograms/makeCsv.py`](MakeHistograms/makeCsv.py) (accepts `--siemens`, `--ge`, `--between`, `--FA`, `--MD` flags) to bin histogram values and write them out for comparison. Inspect the tails of the distributions to spot outliers.

7. **Plot results.**
   - Box-and-whisker plots: [`PlottingScripts/make_box_plots.py`](PlottingScripts/make_box_plots.py)
   - Basic FA/MD histogram plots for a single map: [`PlottingScripts/makeBasicPlot.py`](PlottingScripts/makeBasicPlot.py)
   - Cumulative-frequency plots with the Kolmogorov–Smirnov test statistic: [`PlottingScripts/make_cumulative_Kolmogrov_plot.py`](PlottingScripts/make_cumulative_Kolmogrov_plot.py)

## Repository layout

| Path | Contents |
|---|---|
| `GetData/` | Filtering radiology reports down to healthy, diffusion-relevant scans |
| `ProcessDtiData/` | DICOM → NIfTI conversion, quality filtering, FSL-based DTI processing |
| `CalculateDistances/` | Histogram distance/divergence metrics between FA/MD maps |
| `MakeHistograms/` | Utilities for building and binning histogram CSVs |
| `PlottingScripts/` | Box plots, basic histograms, cumulative KS plots |
| `legacy_code/` | Original, unmodified code used for the published analysis |

## Notes

- Several scripts (e.g. `makeCsv.py`, `hist_dist_between_csv.py`, `makeBasicPlot.py`) contain absolute, machine-specific paths (originally pointing at a Martinos Center server) — update these before running on your own data.
- The parallel-processing option in `DataSet.processDTI()` generates a script intended for the Martinos Center's `launchpad`/PBS cluster and is unlikely to work on other systems without modification.
- No license file is currently included in this repository.
