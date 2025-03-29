import os
import re
import shutil  # Added this import
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class ClassStructure:
    """Data structure to store class members and methods"""
    public_methods: List[str] = field(default_factory=list)
    public_properties: List[str] = field(default_factory=list)
    unity_serialized_fields: List[str] = field(default_factory=list)

    static_methods: List[str] = field(default_factory=list)  # New field for static methods
    static_properties: List[str] = field(default_factory=list)  # New field for static properties
    
    reference_count: int = 0
    static_reference_count: int = 0  # New field for static reference counting
    
    referenced_by: Set[str] = field(default_factory=set)  # Store which classes reference this class

    static_referenced_by: Set[str] = field(default_factory=set)  # New field for static references

class CSharpAnalyzer:
    def __init__(self):
        self.class_dict: Dict[str, ClassStructure] = {}
        self.class_contents: Dict[str, str] = {}
        self.current_file: str = ""
    
    def analyze_file(self, file_path: str) -> None:  # Correct indentation
        """Analyze a single C# file and extract class information"""
        self.current_file = file_path
        content = None
        encodings = ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']
        
        # Try different encodings
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    print(f"Successfully read {file_path} with {encoding} encoding")
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                return
        
        if content is None:
            print(f"Warning: Could not read {file_path} with any supported encoding. Skipping file.")
            return
            
        try:
            self.class_contents[file_path] = content
            content_no_comments = self._remove_comments(content)
            
            # Find all class declarations
            class_matches = re.finditer(r'(?:public|private)\s+class\s+(\w+)', content_no_comments)
            
            for class_match in class_matches:
                class_name = class_match.group(1)
                class_start = class_match.end()
                class_content = self._extract_class_content(content_no_comments[class_start:])
                
                if class_name not in self.class_dict:
                    self.class_dict[class_name] = ClassStructure()
                
                self._analyze_class_content(class_name, class_content)
                
        except Exception as e:
            print(f"Error processing file content {file_path}: {e}")

    def _find_static_members(self, class_content: str, class_name: str) -> None:
        """Find all static methods and properties in the class content"""
        # Find static methods
        static_method_pattern = r'public\s+static\s+(?!class|struct|enum|interface)[\w<>[\]]+\s+(\w+)\s*\([^)]*\)'
        static_methods = re.finditer(static_method_pattern, class_content)
        for method in static_methods:
            self.class_dict[class_name].static_methods.append(method.group(1))

        # Find static properties
        static_property_pattern = r'public\s+static\s+[\w<>[\]]+\s+(\w+)\s*\{[^}]*\}'
        static_properties = re.finditer(static_property_pattern, class_content)
        for prop in static_properties:
            self.class_dict[class_name].static_properties.append(prop.group(1))


    def _analyze_class_content(self, class_name: str, class_content: str) -> None:
        """Analyze the content of a class including its members, methods, and references"""
        # Find public methods
        self._find_public_methods(class_content, class_name)
        
        # Find public properties
        self._find_public_properties(class_content, class_name)
        
        # Find Unity serialized fields
        self._find_unity_serialized_fields(class_content, class_name)

        # Add static analysis
        self._find_static_members(class_content, class_name)

    def analyze_static_references(self) -> None:
        """Analyze static references between classes"""
        for file_path, content in self.class_contents.items():
            content_no_comments = self._remove_comments(content)
            
            current_class_match = re.search(r'(?:public|private)\s+class\s+(\w+)', content_no_comments)
            if not current_class_match:
                continue

            current_class = current_class_match.group(1)
            
            for referenced_class in self.class_dict.keys():
                if referenced_class == current_class:
                    continue

                # Basic static patterns
                basic_patterns = [
                    fr'{referenced_class}\.\w+\s*\(',           # Method calls
                    fr'{referenced_class}\.\w+\s*[^(]',         # Property access
                    fr'{referenced_class}\.\w+\s*[=;]',         # Field access
                    fr'using\s+static\s+{referenced_class}',    # Static using
                    fr'{referenced_class}<[^>]+>\.\w+\s*\('     # Generic static calls
                ]
                
                # Singleton patterns
                singleton_patterns = [
                    fr'{referenced_class}\.Instance\b',
                    fr'{referenced_class}\.Current\b',
                    fr'{referenced_class}\.GetInstance\(\)'
                ]
                
                # Event system patterns
                event_patterns = [
                    fr'{referenced_class}\.Send\b',
                    fr'{referenced_class}\.AddListener\b',
                    fr'{referenced_class}\.RemoveListener\b',
                    fr'{referenced_class}\.Broadcast\b',
                    fr'{referenced_class}\.Dispatch\b',
                    fr'{referenced_class}\.Subscribe\b',
                    fr'{referenced_class}\.Publish\b'
                ]
                
                # Unity-specific patterns
                unity_patterns = [
                    fr'{referenced_class}\.Find\b',
                    fr'{referenced_class}\.FindObjectOfType\b',
                    fr'{referenced_class}\.Instantiate\b',
                    fr'{referenced_class}\.Destroy\b'
                ]
                
                # Common static utility patterns
                utility_patterns = [
                    fr'{referenced_class}\.Create\b',
                    fr'{referenced_class}\.Get\b',
                    fr'{referenced_class}\.Initialize\b',
                    fr'{referenced_class}\.Parse\b',
                    fr'{referenced_class}\.TryParse\b',
                    fr'{referenced_class}\.From\w+\b'
                ]

                all_patterns = (basic_patterns + singleton_patterns + 
                            event_patterns + unity_patterns + utility_patterns)

                # Check each pattern
                for pattern in all_patterns:
                    matches = re.finditer(pattern, content_no_comments)
                    if any(matches):
                        self.class_dict[referenced_class].static_reference_count += 1
                        self.class_dict[referenced_class].static_referenced_by.add(current_class)
                        break  # Count only once per class

    def _find_public_methods(self, class_content: str, class_name: str) -> None:
        """Find all public methods in the class content"""
        method_pattern = r'public\s+(?!class|struct|enum|interface)[\w<>[\]]+\s+(\w+)\s*\([^)]*\)'
        methods = re.finditer(method_pattern, class_content)
        for method in methods:
            self.class_dict[class_name].public_methods.append(method.group(1))

    def _find_public_properties(self, class_content: str, class_name: str) -> None:
        """Find all public properties in the class content"""
        property_pattern = r'public\s+[\w<>[\]]+\s+(\w+)\s*\{[^}]*\}'
        properties = re.finditer(property_pattern, class_content)
        for prop in properties:
            self.class_dict[class_name].public_properties.append(prop.group(1))

    def _find_unity_serialized_fields(self, class_content: str, class_name: str) -> None:
        """Find Unity serialized fields"""
        serialized_pattern = r'\[SerializeField\]\s*(?:private|protected)\s+[\w<>[\]]+\s+(\w+)'
        serialized_fields = re.finditer(serialized_pattern, class_content)
        for field in serialized_fields:
            self.class_dict[class_name].unity_serialized_fields.append(field.group(1))

    def _remove_comments(self, content: str) -> str:
        """Remove C# comments from the content"""
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content

    def _extract_class_content(self, content: str) -> str:
        """Extract the content between the first { and its matching }"""
        bracket_count = 0
        start_index = content.find('{')
        
        if start_index == -1:
            return ""
            
        for i in range(start_index, len(content)):
            if content[i] == '{':
                bracket_count += 1
            elif content[i] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    return content[start_index:i + 1]
        
        return content[start_index:]

    def analyze_references(self) -> None:
        """Analyze references between classes based on specific criteria"""
        # Reset reference counts
        for structure in self.class_dict.values():
            structure.reference_count = 0
            structure.referenced_by.clear()

        for file_path, content in self.class_contents.items():
            content_no_comments = self._remove_comments(content)
            
            # Find current class name
            current_class_match = re.search(r'(?:public|private)\s+class\s+(\w+)', content_no_comments)
            if not current_class_match:
                continue

            current_class = current_class_match.group(1)
            
            # For each potential referenced class
            for referenced_class in self.class_dict.keys():
                if referenced_class == current_class:
                    continue
                
                # Check for class member declarations (case 1)
                member_pattern = fr'(?:private|protected|public)\s+{referenced_class}\s+\w+'
                
                # Check for method parameters (case 2)
                param_pattern = fr'\([^)]*{referenced_class}\s+\w+[^)]*\)'
                
                # Check for local variables in method bodies (case 3)
                local_var_pattern = fr'{referenced_class}\s+\w+\s*[=;]'
                
                # Additional Unity-specific patterns
                unity_patterns = [
                    fr'\[SerializeField\]\s*(?:private|protected)\s+{referenced_class}\s+\w+',  # SerializeField
                    fr'GetComponent\s*<\s*{referenced_class}\s*>',  # GetComponent
                    fr'AddComponent\s*<\s*{referenced_class}\s*>',  # AddComponent
                    fr'FindObjectOfType\s*<\s*{referenced_class}\s*>',  # FindObjectOfType
                    fr'Instantiate\s*<\s*{referenced_class}\s*>',  # Instantiate
                    fr'RequireComponent\s*\(\s*typeof\s*\(\s*{referenced_class}\s*\)\s*\)'  # RequireComponent
                ]
                
                # Additional C# patterns
                csharp_patterns = [
                    fr':\s*{referenced_class}\b',  # Inheritance
                    fr'where\s+\w+\s*:\s*{referenced_class}',  # Generic constraints
                    fr'List<{referenced_class}>',  # Generic collections
                    fr'Dictionary<[^,]*,\s*{referenced_class}>',  # Dictionary value type
                    fr'Dictionary<{referenced_class},\s*[^>]*>',  # Dictionary key type
                ]
                
                all_patterns = [member_pattern, param_pattern, local_var_pattern] + unity_patterns + csharp_patterns
                
                # Check each pattern
                for pattern in all_patterns:
                    if re.search(pattern, content_no_comments):
                        self.class_dict[referenced_class].reference_count += 1
                        self.class_dict[referenced_class].referenced_by.add(current_class)
                        break  # Count only once per class

def search_and_analyze_csharp_files(search_directory: str) -> CSharpAnalyzer:
    """Search for C# files and analyze their structure"""
    analyzer = CSharpAnalyzer()
    
    # First pass: analyze class structure
    for root, _, files in os.walk(search_directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                print(f"Analyzing structure: {file_path}")
                analyzer.analyze_file(file_path)
    
    # Second pass: analyze references
    print("\nAnalyzing class references...")
    analyzer.analyze_references()
    
    # Add this line to analyze static references
    analyzer.analyze_static_references()  # <-- Missing!

    return analyzer


def save_analysis_results(analyzer: CSharpAnalyzer, output_file: str) -> None:
    print("\n=== Starting Analysis Results Save Process ===")
    
    # Print absolute paths for debugging
    print(f"Current working directory: {os.getcwd()}")
    absolute_output_path = os.path.abspath(output_file)
    print(f"Absolute output file path: {absolute_output_path}")
    
    # Check if analyzer has any data
    if not analyzer.class_dict:
        print("Warning: No classes found in analyzer. Nothing to save.")
        return
    
    print(f"Found {len(analyzer.class_dict)} classes to analyze")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir:
        print(f"Output directory path: {output_dir}")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except Exception as e:
                print(f"Error creating output directory: {e}")
                return
        else:
            print("Output directory already exists")

    try:
        print(f"Attempting to open file: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            print("Successfully opened output file")
            f.write("=== C# Class Analysis Results ===\n\n")
            
            # Sort classes by reference count
            print("Sorting classes by reference count...")
            sorted_classes = sorted(
                analyzer.class_dict.items(),
                key=lambda x: (-(x[1].reference_count + x[1].static_reference_count), x[0])
            )
            print(f"Sorted {len(sorted_classes)} classes")
            
            # Main detailed results
            #print("\nWriting detailed class information...")
            for class_name, structure in sorted_classes:
                #print(f"Processing class: {class_name}")
                f.write(f"Class: {class_name}\n")
                f.write(f"  Instance Reference Count: {structure.reference_count}\n")
                f.write(f"  Static Reference Count: {structure.static_reference_count}\n")

                if structure.referenced_by:
                    f.write("  Referenced By Classes(Instance):\n")
                    for ref_class in sorted(structure.referenced_by):
                        f.write(f"    - {ref_class}\n")
                f.write("\n")
                
                if structure.static_referenced_by:
                    f.write("  Referenced By Classes (Static):\n")
                    for ref_class in sorted(structure.static_referenced_by):
                        f.write(f"    - {ref_class}\n")
                
                if structure.static_methods:
                    f.write("  Static Methods:\n")
                    for method in structure.static_methods:
                        f.write(f"    - {method}\n")
                
                if structure.static_properties:
                    f.write("  Static Properties:\n")
                    for prop in structure.static_properties:
                        f.write(f"    - {prop}\n")

                f.write("  Public Methods:\n")
                for method in structure.public_methods:
                    f.write(f"    - {method}\n")
                    
                f.write("\n  Public Properties:\n")
                for prop in structure.public_properties:
                    f.write(f"    - {prop}\n")
                    
                f.write("\n  Unity Serialized Fields:\n")
                for field in structure.unity_serialized_fields:
                    f.write(f"    - {field}\n")
                
                f.write("\n" + "="*50 + "\n\n")
            
            # Summary section
            print("\nWriting summary section...")
            f.write("\n=== Frequently Referenced Classes (Count >= 1) ===\n\n")
            frequent_classes = [
                (class_name, structure.reference_count, structure.static_reference_count) 
                for class_name, structure in sorted_classes 
                if structure.reference_count >= 1 or structure.static_reference_count >= 1
            ]
            
        if frequent_classes:
            print(f"Found {len(frequent_classes)} frequently referenced classes")
            for class_name, instance_count, static_count in frequent_classes:
                f.write(f"Class: {class_name} Instance Count: {instance_count} Static Count: {static_count}\n")
        else:
            print("No frequently referenced classes found")
            f.write("No classes with reference count greater than 1 found.\n")

        # Verify file exists and get its size
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"File successfully created and written. Size: {file_size} bytes")
            print(f"File can be found at: {absolute_output_path}")
        else:
            print("Warning: File was not found after writing!")

        print(f"\nSuccessfully saved analysis results to: {output_file}")
        
    except Exception as e:
        print(f"\nError while saving analysis results: {e}")
        print(f"Failed to write to: {output_file}")

def print_frequent_references(analyzer: CSharpAnalyzer) -> None:
    # Current version only uses instance reference_count
    # Should be updated to include static references:
    sorted_classes = sorted(
        analyzer.class_dict.items(),
        key=lambda x: (-(x[1].reference_count + x[1].static_reference_count), x[0])
    )
    
    # Filter and print classes with reference count > 1
    frequent_classes = [
        (class_name, structure.reference_count, structure.static_reference_count) 
        for class_name, structure in sorted_classes 
        if structure.reference_count >= 1 or structure.static_reference_count >= 1
    ]
    
    if frequent_classes:
        for class_name, instance_count, static_count in frequent_classes:
            print(f"Class: {class_name} Instance Count: {instance_count} Static Count: {static_count}")
    else:
        print("No classes with reference count greater than 1 found.")

def copy_frequent_referenced_files(analyzer: CSharpAnalyzer, search_directory: str, destination_directory: str) -> None:
    """
    Copy files containing frequently referenced classes (reference count >= 1) to the destination directory.
    
    Parameters:
    - analyzer: CSharpAnalyzer instance containing the analysis results
    - search_directory: Root directory to search for .cs files
    - destination_directory: Directory where to copy the files
    """
    # Ensure the destination directory exists
    if os.path.exists(destination_directory):
        shutil.rmtree(destination_directory)
    os.makedirs(destination_directory, exist_ok=True)

    # Get classes with reference count > 1
    frequent_classes = {
        class_name
        for class_name, structure in analyzer.class_dict.items()
        if structure.reference_count >= 1 or structure.static_reference_count >= 1  # Include static references
    }

    # Keep track of copied files to avoid duplicates
    copied_files = set()
    files_copied = 0

    for root, _, files in os.walk(search_directory):
        for file in files:
            if not file.endswith('.cs'):
                continue
                
            file_path = os.path.join(root, file)
            content = None
            encodings = ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']
            
            # Try different encodings
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error accessing file {file_path}: {e}")
                    break
            
            if content is None:
                print(f"Warning: Could not read {file_path} with any supported encoding. Skipping file.")
                continue
                    
            # Check if the file contains any of the frequently referenced classes
            for class_name in frequent_classes:
                class_pattern = fr'(?:public|private)\s+class\s+{class_name}\b'
                if re.search(class_pattern, content):
                    if file_path not in copied_files:
                        shutil.copy(file_path, destination_directory)
                        copied_files.add(file_path)
                        files_copied += 1
                        print(f"Copied: {file_path} -> {destination_directory}")
                        break

def main():
    search_directory = 'Projects/SampleProject/Scripts'
    analysis_output = 'out/class_analysis_results.txt'
    frequent_classes_directory = r'out'
    
    # Analyze all C# files
    analyzer = search_and_analyze_csharp_files(search_directory)
    
    # Print frequently referenced classes summary
    print_frequent_references(analyzer)
    
    # Copy files containing frequently referenced classes
    copy_frequent_referenced_files(analyzer, search_directory, frequent_classes_directory)

    # Save detailed analysis results
    save_analysis_results(analyzer, analysis_output)

if __name__ == "__main__":
    main()