import os
import re

def normalize_help_md():
    input_dir = os.path.join('otm_builder', 'help', 'markdown')
    output_dir = os.path.join('otm_builder', 'help', 'convertido')
    output_path = os.path.join(output_dir, 'help_normalized.md')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Gather all .md files recursively from input_dir
    md_file_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                md_file_paths.append(os.path.join(root, file))

    # Read all files and combine lines
    all_lines = []
    for file_path in md_file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines.extend(f.readlines())

    original_line_count = len(all_lines)

    # Fix common encoding artifacts
    def fix_encoding_artifacts(text):
        replacements = {
            'Â': '',
            'â¢': '•',
            'â': '—',
            'â': '–',
            'â': '"',
            'â': '"',
            'â': "'",
            'â': "'",
            'â¢': '•',
            'â¦': '…',
            '\u200b': '',  # zero-width space
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    fixed_lines = [fix_encoding_artifacts(line) for line in all_lines]

    # Remove duplicate lines while preserving order
    seen = set()
    unique_lines = []
    for line in fixed_lines:
        stripped_line = line.rstrip('\n')
        if stripped_line not in seen:
            seen.add(stripped_line)
            unique_lines.append(line)
    duplicates_removed = original_line_count - len(unique_lines)

    # Normalize spacing: max one blank line between sections
    normalized_lines = []
    blank_line_count = 0
    for line in unique_lines:
        if line.strip() == '':
            blank_line_count += 1
            if blank_line_count <= 1:
                normalized_lines.append('\n')
            # else skip additional blank lines
        else:
            blank_line_count = 0
            normalized_lines.append(line if line.endswith('\n') else line + '\n')

    final_line_count = len(normalized_lines)

    # Write the normalized file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(normalized_lines)

    # Print summary
    print(f"Normalization complete.")
    print(f"Files read: {len(md_file_paths)}")
    print(f"Output path: {output_path}")
    print(f"Original lines: {original_line_count}")
    print(f"Final lines: {final_line_count}")
    print(f"Duplicate lines removed: {duplicates_removed}")

if __name__ == '__main__':
    normalize_help_md()
