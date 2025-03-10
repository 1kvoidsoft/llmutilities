import os

def generate_folder_structure(search_directory, output_file, exclude_file):
    # Read exclude folders
    exclude_folders = []
    if os.path.exists(exclude_file):
        with open(exclude_file, 'r') as f:
            exclude_folders = [line.strip() for line in f]

    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(search_directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_folders]
            
            level = root.replace(search_directory, '').count(os.sep)
            indent = '│   ' * (level)
            
            relative_path = os.path.basename(root)
            if level == 0:
                f.write(f"{relative_path}/\n")
            else:
                f.write(f"{indent[:-4]}├── {relative_path}/\n")
            
            subindent = '│   ' * (level + 1)
            for i, file in enumerate(sorted(files)):
                is_last = (i == len(files) - 1) and not dirs
                prefix = '└── ' if is_last else '├── '
                f.write(f"{subindent}{prefix}{file}\n")

# Example usage:
search_directory = r'F:\Projects\Glove2024\src'
output_file = 'folder_structure.txt'
exclude_file = 'exclude_folders.txt'

generate_folder_structure(search_directory, output_file, exclude_file)