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
| `--warnings`                   | prints all warning information to standard output      |

## Background

As part of the [NFDI4Culture](https://nfdi4culture.de/) initiative, efforts are underway to enhance the capabilities of open-source digital preservation software like Archivematica to identify, validate and preserve 3D file formats. This repository provides a script to enable Graphics Language Transmission Format (glTF) file validation in Archivematica, which is not supported by default in version 1.13.2, enhancing its 3D content preservation capabilities.

## Dependencies

[Python 2.4](https://www.python.org/download/releases/2.4/) or higher.

## Related projects

- [3D Sample Files for Digital Preservation Testing](https://github.com/JoergHeseler/3d-sample-files-for-digital-preservation-testing)
- [DAE Validator for Archivematica](https://github.com/JoergHeseler/dae-validator-for-archivematica)
- [glTF Metadata Extractor for Archivematica](https://github.com/JoergHeseler/gltf-metadata-extractor-for-archivematica)
- [glTF Validator for Archivematica](https://github.com/JoergHeseler/gltf-validator-for-archivematica)
  <!-- - [STL Cleaner](https://github.com/JoergHeseler/stl-cleaner) -->
- [STL Metadata Extractor for Archivematica](https://github.com/JoergHeseler/stl-metadata-extractor-for-archivematica)
- [STL Validator for Archivematica](https://github.com/JoergHeseler/stl-validator-for-archivematica)
- [X3D Validator for Archivematica](https://github.com/JoergHeseler/x3d-validator-for-archivematica)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Special thanks to the IT colleagues at the SLUB Dresden for their support and valuable feedback during development.

## Imprint

[NFDI4Culture](https://nfdi4culture.de/) – Consortium for Research Data on Material and Immaterial Cultural Heritage

NFDI4Culture is a consortium within the German [National Research Data Infrastructure (NFDI)](https://www.nfdi.de/).

Contact: [Jörg Heseler](https://orcid.org/0000-0002-1497-627X)

This repository is licensed under a [Creative Commons Attribution 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

NFDI4Culture is funded by the German Research Foundation (DFG) – Project number – [441958017](https://gepris.dfg.de/gepris/projekt/441958017).
