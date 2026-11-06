# D-2stepD

Directed-network measures D, 2-step D and CD, node visualizations, overlap matrices and intentional-attack curves.

## Install

Use Python 3.11. From the repository root:

```bash
python -m venv .venv
# Activate .venv using the command for your operating system.
python -m pip install -r requirements.txt
cp config.example.json config.json
jupyter lab
```

## Configure and run

Set `data_dir`, `output_dir` and `seed` in `config.json`, then open a notebook and run its cells in order with a fresh kernel. Relative directories resolve against the configuration file location. The repository root is the Jupyter working directory.

`RESEARCH_CONFIG` selects a configuration file; `RESEARCH_DATA_DIR`, `RESEARCH_OUTPUT_DIR` and `RESEARCH_SEED` provide environment overrides. The default seed is 2026. Tables use CSV, single-CSV ZIP archives or Excel. File naming is defined in `project_utils.DATA_FILES`; `input_schema.json` specifies the table field contracts.

Figures render in Jupyter. Explicit file exports use the configured output directory. Notebooks are stored with clear execution state.

For APS figures, run `calculate measures in APS Network.ipynb` first. It writes `aps_disruption_metrics.csv` to `output_dir`. Then run `fig 3 by networkx.ipynb` or the APS section of `fig5 intentional attack.ipynb` with the same configuration. These notebooks join the calculated `D`, `2stepD`, `CD` and `degree` columns to the node properties by DOI `id`; `h`, `pagerank` and `meta` come from the node property table. DOI ids must be unique and match between the two tables.

## Notebooks

- `calculate measures in APS Network.ipynb`
- `fig 3 by networkx.ipynb`
- `fig 4 bubble-R-10.ipynb`
- `fig5 intentional attack.ipynb`

## Methods

APS edges point from citing to cited DOI. Vertex IDs follow node-table row order, including isolated vertices. Duplicate edges and self-loops are removed. D and CD exclude the focal vertex from reference-citer counts. 2-step D is a scalar, with value 1 when there are no first- or second-step references and 0 when its nontrivial denominator is empty. The main notebook writes `aps_disruption_metrics.csv` with the DOI key `id`. Node property tables join on this key.

`netdata.zip` contains the supplied network material. The overlap notebook uses R and `plot_overlap.R`; install `ggplot2`, `reshape2`, `jsonlite` and `IRkernel`, then select the R kernel. The overlap CSV values are proportions in [0, 1].

Bootstrap intervals use full-size resamples of finite observations and deterministic random generators.

## Source checks

```bash
python scripts/validate_sources.py
```

This command parses Python and notebook source, validates JSON and checks notebook execution state. GitHub Actions runs the same source checks without executing research analyses.

## Citation and license

`CITATION.cff` provides software citation metadata. Cite the associated publication using its bibliographic record. Project code and documentation use the MIT license. Third-party data retain their providers' licenses and access terms.
