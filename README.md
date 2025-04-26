# LLMUtilities

A collection of Python utilities for code analysis, file management, and structure visualization designed to work well with Large Language Models (LLMs) like Claude or ChatGPT.

## Overview

This repository contains a set of specialized tools that help developers extract, organize, and visualize code for analysis with AI-powered tools. Whether you're analyzing large codebases, tracking down specific classes, or preparing code for LLM-based analysis, these utilities make the process more efficient.

## Tools Included

### 1. Class Finder Tool

Extract specific classes from large codebases.

- **Path:** `src/class_finder_tool/`
- **Features:**
  - Find class definitions across large directories
  - Copy relevant files to a specified output directory
  - Support for C# and JavaScript files
  - Handle multiple file encodings
  - Generate detailed search reports
  - Optional filename suffix support

```bash
python src/class_finder_tool/search_classes.py <search_directory> <destination_directory> "<class_list>" [dest_suffix]
```

### 2. File Structure Generator

Generate visual tree representations of project directory structures.

- **Path:** `src/filestructure_gen/`
- **Features:**
  - Create text-based tree visualizations of file structures
  - Support for excluding specific directories
  - Unicode formatting for attractive output
  - Save results to text files

```bash
# Modify directory paths in the script before running
python src/filestructure_gen/filestructure_gen.py
```

### 3. C# Project Analyzer

Analyze relationships between classes in C# projects, particularly useful for Unity projects.

- **Path:** `src/member_search/`
- **Features:**
  - Analyze both instance and static references between classes
  - Detect public methods, properties, Unity serialized fields, and static members
  - Identify dependencies using regex patterns for C# and Unity constructs
  - Generate detailed analysis reports with reference counts
  - Extract frequently referenced classes to a separate directory

```bash
# Customize directories in the script before running
python src/member_search/member_search.py
```

## Use Cases

### For AI-Assisted Development
- Extract relevant code sections to share with LLMs for analysis or modification
- Focus on high-value classes by identifying the most referenced components
- Generate context-rich documentation for AI tools to better understand your codebase

### For Project Management
- Visualize project structure for documentation
- Find dependencies between components
- Track down specific implementations
- Create focused subsets of code for review or refactoring

### For Unity Developers
- Identify key interconnected classes in Unity projects
- Extract game architecture patterns
- Analyze serialized field usage

## Getting Started

1. Each tool can be run independently from its directory:
```bash
python src/class_finder_tool/search_classes.py ./src ./output "ClassA,ClassB,ClassC"
```

2. See individual tool READMEs for detailed usage instructions.

## Requirements

- Python 3.7 or higher
- No external dependencies (uses standard library only)
