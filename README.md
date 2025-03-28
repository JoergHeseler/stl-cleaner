# STL Cleaner

## Overview

The STL Cleaner script validates and corrects STL files (ASCII and binary) by checking geometric integrity, ensuring counterclockwise vertex ordering, recalculating normals, and repositioning models to a defined minimum position. It outputs cleaned STL files ready for use in workflows like 3D printing or digital preservation.

## Background

Malformed STL files can disrupt 3D workflows and archiving. This tool ensures STL files comply with the specification and improves geometric accuracy. However, the model should be manifold before using this tool. Non-manifold models can be fixed using software like [Blender](https://www.blender.org/).

## Making Models Manifold in Blender

1. Open Blender and go to **Edit** > **Preferences** > **Get Extensions**.
2. Search for `3D Print Toolbox` and click on **Install**. **3D Print Toolbox** should be enabled now in the **Add-ons** tab.
3. Import your STL file (**File** > **Import** > **STL**).
4. Press `N` to open the right-side panel and select the **3D Print** tab.
5. In **Edit Mode**, select the model (`A`).
6. Use the **3D Print Toolbox** options:
   - Click **Check All** to identify issues.
   - Click **Make Manifold** to fix non-manifold geometry.
7. Recheck the model and export it as a cleaned STL (**File** > **Export** > **STL**).

## Usage

1. Download [**stl-cleaner.py**](./src/stl-cleaner.py).
2. In the command line run `python stl-cleaner.py <STL file> [options]`

### Options

| Option                         | Description                                            |
| ------------------------------ | ------------------------------------------------------ |
| `--o=<output file path>`       | path to the corrected output STL file output           |
| `--indent=<number of spaces>`  | indentation spaces, default=1                          |
| `--min-pos=<minimum position>` | mininum allowed model position, default=0.01,0.01,0.01 |
| `--force-repos`                | always repositions the model to the minimum position   |
| `--ignore-endsolid-name`       | only considers the solid name                          |
| `--warnings`                   | prints all warning information to standard output      |

## Dependencies

[Python 2.4](https://www.python.org/download/releases/2.4/) or higher and [Blender 4.4](https://www.blender.org/download/releases/4-4/).

## Related projects

- [3D Sample Files for Digital Preservation Testing](https://github.com/JoergHeseler/3d-sample-files-for-digital-preservation-testing)
- [DAE Validator for Archivematica](https://github.com/JoergHeseler/dae-validator-for-archivematica)
- [glTF Metadata Extractor for Archivematica](https://github.com/JoergHeseler/gltf-metadata-extractor-for-archivematica)
- [glTF Validator for Archivematica](https://github.com/JoergHeseler/gltf-validator-for-archivematica)
- [Siegfried Falls Back on Fido Identifier for Archivematica](https://github.com/JoergHeseler/siegfried-falls-back-on-fido-identifier-for-archivematica)
- [STL Metadata Extractor for Archivematica](https://github.com/JoergHeseler/stl-metadata-extractor-for-archivematica)
- [STL Validator for Archivematica](https://github.com/JoergHeseler/stl-validator-for-archivematica)
- [X3D Validator for Archivematica](https://github.com/JoergHeseler/x3d-validator-for-archivematica)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Special thanks to the colleagues from the SLUB Dresden, specifically from the Infrastructure and Long-Term Availability division, for their support and valuable feedback during the development.

## Imprint

[NFDI4Culture](https://nfdi4culture.de/) – Consortium for Research Data on Material and Immaterial Cultural Heritage.  
Funded by the German Research Foundation (DFG), Project No. [441958017](https://gepris.dfg.de/gepris/projekt/441958017).

**Author**: [Jörg Heseler](https://orcid.org/0000-0002-1497-627X)  
**License**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
