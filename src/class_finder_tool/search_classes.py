import os
import shutil
import re
import sys

def search_and_copy_classes(search_directory, destination_directory, class_list_str, dest_suffix=""):
    """
    Searches for class definitions in C# files in the given directory,
    and copies files containing the target classes directly to the destination directory.
    
    Args:
        search_directory (str): Directory to search for class files
        destination_directory (str): Directory to copy found files to
        class_list_str (str): Comma-separated string of class names to search for
                             Example: "EditIcon","CreationEditCtrl","TreeNodeInfo"
        dest_suffix (str, optional): Suffix to add to destination filenames (e.g. "Old" -> class1Old.cs)
    """
    # Parse the class list string into a list of class names
    class_list = [cls.strip('"\'') for cls in class_list_str.split(',')]
    
    # Ensure the destination directory exists
    if os.path.exists(destination_directory):
        shutil.rmtree(destination_directory)
    os.makedirs(destination_directory, exist_ok=True)
    
    # List of encodings to try
    encodings = ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']
    
    # Dictionary to track which files contain which classes
    found_classes = {cls: [] for cls in class_list}
    found_files = []
    
    print(f"Searching for {len(class_list)} classes in {search_directory}...")
    
    # Walk through the directory structure
    for root, dirs, files in os.walk(search_directory):
        for file in files:
            # Only look at C# files (could be expanded to include other languages)
            if file.endswith(('.cs', '.js')):
                file_path = os.path.join(root, file)
                
                # Try different encodings
                content_read = False
                file_content = ""
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            file_content = f.read()
                            content_read = True
                            break  # Successfully read the file
                    except UnicodeDecodeError:
                        continue  # Try next encoding
                    except Exception as e:
                        print(f"Error accessing file {file_path}: {e}")
                        break
                
                if not content_read:
                    print(f"Warning: Could not read {file_path} with any supported encoding. Skipping file.")
                    continue
                
                # Check if any of the target classes are defined in this file
                for class_name in class_list:
                    # Look for class definition patterns: "class ClassName" or "class ClassName:"
                    class_pattern = rf'\bclass\s+{re.escape(class_name)}\s*[:\{{]|\bclass\s+{re.escape(class_name)}$'
                    if re.search(class_pattern, file_content):
                        # Add suffix to the filename if provided
                        if dest_suffix:
                            base, ext = os.path.splitext(file)
                            filename_with_suffix = f"{base}{dest_suffix}{ext}"
                            destination_file = os.path.join(destination_directory, filename_with_suffix)
                        else:
                            destination_file = os.path.join(destination_directory, file)
                        
                        # Handle file name conflicts by appending class name if needed
                        if os.path.exists(destination_file) and destination_file not in found_files:
                            base, ext = os.path.splitext(os.path.basename(destination_file))
                            if dest_suffix:
                                # If we already added a suffix, remove it before adding class name
                                base = base[:-len(dest_suffix)] if base.endswith(dest_suffix) else base
                                destination_file = os.path.join(destination_directory, f"{base}_{class_name}{dest_suffix}{ext}")
                            else:
                                destination_file = os.path.join(destination_directory, f"{base}_{class_name}{ext}")
                        
                        # Copy the file if it hasn't been copied yet
                        if destination_file not in found_files:
                            shutil.copy(file_path, destination_file)
                            found_files.append(destination_file)
                            print(f"Found class {class_name} in {file_path}")
                            print(f"  Copied to {destination_file}")
                        
                        found_classes[class_name].append(file_path)
    
    # Create a report file
    report_path = os.path.join(destination_directory, "search_report.txt")
    with open(report_path, 'w') as report:
        report.write("CLASS SEARCH RESULTS\n")
        report.write("===================\n\n")
        
        for class_name in class_list:
            if found_classes[class_name]:
                report.write(f"{class_name}: Found in {len(found_classes[class_name])} files\n")
                for file_path in found_classes[class_name]:
                    report.write(f"  - {file_path}\n")
            else:
                report.write(f"{class_name}: Not found\n")
        
        # Count total files found
        total_files = len(found_files)
        report.write(f"\nTotal files containing target classes: {total_files}\n")
        if dest_suffix:
            report.write(f"Files were copied with suffix: '{dest_suffix}'\n")
    
    print(f"\nSearch complete. Results saved to {report_path}")
    print(f"Files copied to {destination_directory}")
    if dest_suffix:
        print(f"Files were renamed with suffix: '{dest_suffix}'")
    
    # Return summary stats
    return {
        "total_classes_found": sum(1 for cls in found_classes.values() if cls),
        "total_files": total_files,
        "classes_not_found": [cls for cls, files in found_classes.items() if not files]
    }

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python search_classes.py <search_directory> <destination_directory> \"<class_list>\" [dest_suffix]")
        print("Example: python search_classes.py ./src ./output \"EditIcon,CreationEditCtrl,TreeNodeInfo\" Old")
        sys.exit(1)
    
    search_directory = sys.argv[1]
    destination_directory = sys.argv[2]
    class_list_str = sys.argv[3]
    
    # Optional suffix parameter
    dest_suffix = ""
    if len(sys.argv) > 4:
        dest_suffix = sys.argv[4]
    
    results = search_and_copy_classes(search_directory, destination_directory, class_list_str, dest_suffix)
    
    print(f"\nSummary:")
    print(f"- Found {results['total_classes_found']} out of {len(results['classes_not_found']) + results['total_classes_found']} classes")
    print(f"- Total files: {results['total_files']}")
    
    if results['classes_not_found']:
        print("\nClasses not found:")
        for cls in results['classes_not_found']:
            print(f"- {cls}")