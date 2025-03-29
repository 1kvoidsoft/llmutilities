# C# Project Analyzer

A Python tool for analyzing C# projects, identifying class relationships, and extracting the most interconnected classes.

## Overview

This tool recursively analyzes C# files in a directory, identifies references between classes (both instance and static), and copies the most frequently referenced classes to a separate directory. It's particularly useful for:

- Understanding the core architecture of large C# projects
- Creating a focused "project knowledge" bundle for AI tools like Claude
- Identifying key dependencies in Unity game projects
- Documenting class relationships for knowledge transfer

## Features

- 📊 Analyzes both instance and static references between classes
- 🔍 Detects public methods, properties, Unity serialized fields, and static members
- 🔄 Identifies dependencies using regex patterns for various C# and Unity constructs
- 📝 Generates detailed analysis reports with reference counts and class relationships
- 📂 Extracts frequently referenced classes to a separate directory
- 🛡️ Handles multiple file encodings for international projects

## How It Works

The tool performs a multi-pass analysis:

1. **Structure Analysis**: Extracts class declarations, methods, properties, and fields
2. **Reference Analysis**: Identifies instance references between classes
3. **Static Reference Analysis**: Identifies static references between classes
4. **Output Generation**: Creates reports and extracts frequently referenced files

## Usage

```python
# Basic usage
python member_search.py

# To customize directories in code:
# 1. Update the main() function with your directories:
search_directory = "path/to/your/csharp/project"
analysis_output = "path/to/output/analysis.txt"
frequent_classes_directory = "path/to/output/frequent_classes"
```

## Reference Detection

The analyzer looks for various reference patterns, including:

### Instance References
- Class member declarations: `private ClassName instance;`
- Method parameters: `void Method(ClassName param)`
- Local variables: `ClassName variable = new ClassName();`

### Unity-Specific References
- Serialized fields: `[SerializeField] private ClassName field;`
- Component access: `GetComponent<ClassName>()`, `AddComponent<ClassName>()`
- Object management: `FindObjectOfType<ClassName>()`, `Instantiate<ClassName>()`

### Static References
- Method calls: `ClassName.Method()`
- Property access: `ClassName.Property`
- Singleton patterns: `ClassName.Instance`, `ClassName.GetInstance()`
- Event systems: `ClassName.AddListener()`, `ClassName.Publish()`

## Output

The tool produces two main outputs:

1. **Analysis Report**: A detailed text file containing:
   - Class listing sorted by reference count
   - Instance and static reference counts
   - Methods, properties, and serialized fields for each class
   - Lists of referencing classes

2. **Extracted Files**: Copies of all C# files containing frequently referenced classes

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## Ideal for Unity Projects

While designed for any C# project, this tool has special handling for Unity-specific patterns like:
- SerializeField attributes
- GetComponent/AddComponent calls
- FindObjectOfType/Instantiate methods
- RequireComponent attributes

## License

[MIT License](LICENSE)
