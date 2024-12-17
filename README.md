# STL Corrector

This repository provides a script that converts ASCII and binary Standard Tessellation Language (STL) files specified at https://www.fabbers.com/tech/STL_Format.

# Command line switches

| Option/Parameter               | Description                                          |
| ------------------------------ | ---------------------------------------------------- |
| `--o=<output file path>`       | path to the corrected output STL file output         |
| `--indent=<number of spaces>`  | indentation spaces, default=2                        |
| `--min-pos=<minimum position>` | mininum allowed model position, default=0.1,0.1,0.1  |
| `--force-repos`                | always repositions the model to the minimum position |
| `--ignore-endsolid-name`       | only considers the solid name                        |
