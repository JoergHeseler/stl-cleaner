# STL Cleaner

This repository provides a script that converts ASCII and binary Standard Tessellation Language (STL) files specified at https://www.fabbers.com/tech/STL_Format.

## What It Does

This script validates and corrects STL files (both ASCII and binary formats) by checking the geometric integrity of facets, ensuring counterclockwise vertex ordering, and repositioning the model to a defined minimum position if needed. It also verifies consistency between solid and endsolid names in ASCII files and outputs a cleaned, corrected version of the STL file.

## Usage

1. Download [**stl-cleaner.py**](./src/stl-cleaner.py).

2. In the command line run `python stl-cleaner.py <STL file> [options]`

### Command line switches

| Option                         | Description                                            |
| ------------------------------ | ------------------------------------------------------ |
| `--o=<output file path>`       | path to the corrected output STL file output           |
| `--indent=<number of spaces>`  | indentation spaces, default=1                          |
| `--min-pos=<minimum position>` | mininum allowed model position, default=0.01,0.01,0.01 |
| `--force-repos`                | always repositions the model to the minimum position   |
| `--ignore-endsolid-name`       | only considers the solid name                          |

## Dependencies

[Python 2.4](https://www.python.org/download/releases/2.4/) or higher.

## Imprint

[NFDI4Culture](https://nfdi4culture.de/) – Consortium for Research Data on Material and Immaterial Cultural Heritage

NFDI4Culture is a consortium within the German [National Research Data Infrastructure (NFDI)](https://www.nfdi.de/).

Contact: [Jörg Heseler](https://orcid.org/0000-0002-1497-627X)

This repository is licensed under a [Creative Commons Attribution 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

NFDI4Culture is funded by the German Research Foundation (DFG) – Project number – [441958017](https://gepris.dfg.de/gepris/projekt/441958017).
