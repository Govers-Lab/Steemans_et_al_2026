# Source data and figure reproduction

These notebooks utilize the supplementary datasets associated with the paper. `requirements.txt` records the versions used for the final calculations and validation. Open notebooks from the package root or this folder and run their cells in order.

Scripts display figures and retain the scientific calculations. Default plotting reads only the supplied Excel datasets.

| Script | Dataset and principal sheets | | 
| --- | --- | --- |
| 01 DnaN M9-glucose | S1: `M9glu_plotted_means`, `M9glu_plotted_fractions`, `M9glu_PHATE_plotted`; supporting cells and PHATE inputs | 
| 02 DnaN LB | S1: `LB_plotted_means`, `LB_plotted_fractions`, supporting cells | 
| 03 WT single-cell PHATE | S2: `PHATE_plotted`, `PHATE_input_cells` | 
| 04 Genome-wide preprocessing | Optional on-request single-cell file and annotation workbook; downstream output supplied in S3 |
| 05 Interpretable features | S3: `Raw_well_profiles` |
| 06 Feature/profile correlations | S3 `Raw_well_profiles`; S4 `Feature_correlations`; S5 `Gene_correlations`, `UMAP_plotted`|
| 07 Stationary-phase regulators | S6: `UMAP_plotted`, `Pie_plotted`, `Gene_classification`, `Gene_metadata`; optional reconstruction from S3 |
| 08 Fluorescence phase response | S7: `Plotted_results`, `Replicate_means`, `Single_cells` | 
| 09 Y-gene omics | S8: `Heatmap data`, `Heatmap columns`, `Measurements`, `Source samples` | 
| 10 Y-gene conservation | S9: `Protein_status`, `Tree`, `Taxa`, `Proteins`; display settings in script 10 |

The full genome-wide single-cell table is available on request and is not bundled. Its correct basename is `single-cell_profiles_keio_stat.parquet`, for both preprocessing and WT analysis. Notebook 04 accepts generic configurable paths to that file and its annotation workbook.
