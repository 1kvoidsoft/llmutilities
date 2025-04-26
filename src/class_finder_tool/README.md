# Class Finder Tool

A utility for finding and extracting C# and JavaScript class definitions from large codebases.

## Overview

This tool searches through directories to find files containing specific class definitions and copies them to a designated output directory. It's particularly useful for:

- Extracting specific components from large projects
- Analyzing class implementations across a codebase
- Creating subsets of code for review or refactoring
- Tracking down where specific classes are defined

## Features

- Searches recursively through directory structures
- Supports both C# (.cs) and JavaScript (.js) files
- Handles multiple encodings (UTF-8, GB2312, GBK, ISO-8859-1)
- Generates a detailed report of found classes
- Optional filename suffix support for output files
- Handles naming conflicts automatically
- Command-line interface for easy integration into workflows


## Usage

### Command Line

```bash
python search_classes.py <search_directory> <destination_directory> "<class_list>" [dest_suffix]
```

Parameters:
- `<search_directory>`: Root directory to search for class files
- `<destination_directory>`: Directory to copy found files to
- `<class_list>`: Comma-separated list of class names to search for
- `[dest_suffix]`: (Optional) Suffix to add to destination filenames

Example:
```bash
python search_classes.py ./src ./output "class1,class2,class3..." Old
```

### PowerShell Script

A sample PowerShell script (`search_events.ps1`) is included to demonstrate how to use the tool for specific use cases.

```powershell
# Set source and output directories
$PROJECT_ROOT = "YOUR_PROJECT_ROOT"
$OUTPUT_DIR = "OUTPUT_DIR"
$SUFFIX = ""  # Set the desired suffix here

# Run the class finder script with the event-related classes and suffix
python search_classes.py $PROJECT_ROOT $OUTPUT_DIR "class1,class2,class3..." $SUFFIX
```

### As a Module

You can also import and use the tool in your own Python scripts:

```python
from search_classes import search_and_copy_classes

results = search_and_copy_classes(
    search_directory="./src",
    destination_directory="./output",
    class_list_str="class1,class2,class3...",
    dest_suffix="Old"
)

print(f"Found {results['total_classes_found']} classes in {results['total_files']} files")
```

## Output

The tool creates:

1. Copies of files containing the specified classes in the destination directory
2. A `search_report.txt` file with detailed information about:
   - Which classes were found and where
   - How many instances of each class were found
   - Classes that weren't found
   - Total number of files processed

## Error Handling

The tool attempts to handle various file encoding issues and will try multiple encodings before giving up on a file. Warnings will be printed for files that couldn't be processed.

