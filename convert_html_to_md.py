#!/usr/bin/env python3
"""Convert HTML files in .reference/godel-docs/web/ to Markdown using markitdown."""

import os
from pathlib import Path
from markitdown import MarkItDown

def convert_html_to_md():
    # Input and output directories
    input_dir = Path(".reference/godel-docs/web")
    output_dir = Path(".reference/godel-docs/web-md")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize MarkItDown
    md = MarkItDown()
    
    # Find all HTML files
    html_files = list(input_dir.glob("*.html"))
    
    print(f"Found {len(html_files)} HTML files to convert")
    
    for html_file in html_files:
        # Generate output filename
        md_filename = html_file.stem + ".md"
        md_path = output_dir / md_filename
        
        print(f"Converting: {html_file.name} -> {md_filename}")
        
        try:
            # Convert HTML to Markdown
            result = md.convert(str(html_file))
            
            # Write Markdown to file
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result.text_content)
                
        except Exception as e:
            print(f"Error converting {html_file.name}: {e}")
    
    print(f"\nConversion complete! Markdown files saved to {output_dir}")

if __name__ == "__main__":
    convert_html_to_md()