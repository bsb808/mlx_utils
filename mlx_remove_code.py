#!/usr/bin/env python3

import zipfile
import tempfile
import os
from lxml import etree
import re 
import argparse

def lxml_replace_code_blocks_in_file(input_file, output_file):
    # Define namespaces
    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'
    }

    # Parse the XML file
    # Need this to avoid loosing the CDATA
    tree = etree.parse(input_file, parser = etree.XMLParser(strip_cdata=False))
    root = tree.getroot()

    # Iterate through all <w:p> elements in the document
    for p in root.xpath('.//w:p', namespaces=ns):
        # Check if <w:p> has a style <w:pStyle> with value "code"
        p_style = p.find('.//w:pPr/w:pStyle', namespaces=ns)
        if (p_style is not None) and (p_style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'code'):
            # Find the w:t elements
            p_t = p.find('.//w:t', namespaces=ns)
            if (p_t is not None):
                #print("--")
                #print(etree.tostring(p_t, pretty_print=True, encoding='unicode'))
                p_t.text = etree.CDATA("% Your code here.       ")
            
    # Write the modified XML back to a file
    for of in [output_file, './tmp.xml']:
        with open(of, 'wb') as f:
            #f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(etree.tostring(root, pretty_print=False, xml_declaration=False, encoding='UTF-8'))
    
def process_mlx_file(input_filename, output_filename):
    # Step 1: Expand the zip archive into a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(input_filename, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Step 2: Read and modify the XML file
        # Read the content of the XML file
        xml_file_path = os.path.join(temp_dir, "matlab", "document.xml")

        # Parse the XML file
        lxml_replace_code_blocks_in_file(xml_file_path, xml_file_path)
        #replace_code_blocks_in_file(xml_file_path, xml_file_path)
        
        # Step 4: Recompress all files into a new zip archive
        if os.path.exists(output_filename):
            os.remove(output_filename)
            print(f"File '{output_filename}' has been removed.")

        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)


def modify_filename(file_name):
    """
    Modify the base name of a given file by removing '_soln' or appending '_nocode'.

    This function checks the base name of the input file (excluding the extension).
    - If the base name contains '_soln', it removes this substring.
    - If '_soln' is not found, it appends '_nocode' to the base name.
    The file extension remains unchanged.

    Args:
        file_name (str): The name of the file to be modified, including its extension.

    Returns:
        str: The modified file name with the appropriate changes to the base name.
    """
    # Separate the base name and extension
    base_name, ext = os.path.splitext(file_name)
    
    if '_soln' in base_name:
        # Remove '_soln' from the base name
        new_base_name = base_name.replace('_soln', '')
    else:
        # Append '_nocode' to the base name if '_soln' is not found
        new_base_name = base_name + '_nocode'
    
    # Combine the modified base name with the original extension
    new_file_name = new_base_name + ext
    return new_file_name


def main():
    parser = argparse.ArgumentParser(
        prog = 'mlx_soln2assign.py',
        description="Process an MLX file to replace CDATA content in the matlab/document.xml file.",
        epilog="""
Examples:
  1. Process an MLX file with default output naming.:
   input.mlx

  2. Process an MLX file with a specified output name:
     input.mlx -o output.mlx

Description:
  This script performs the following operations:
  1. Expands the input MLX file (which is a ZIP archive) into a temporary directory.
  2. Reads the 'matlab/document.xml' file within the expanded contents.
  3. Replaces all text within CDATA sections with 'CDATA[% Your code here]'.
  4. Saves the modified XML file.
  5. Recompresses all files in the temporary directory into a new MLX file.

  If no output file is specified, and the input file includes contains '_soln', 
  then the output file defaults to the input file name with the '_soln' substring removed. 
  If '_soln' is not found in the input file name, then '_nocode' is appended to the base name.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input_file", help="Path to the input MLX file")
    parser.add_argument("-o", "--output_file", help="Path to the output MLX file (optional)")
    args = parser.parse_args()

    input_file = args.input_file
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = modify_filename(input_file)

    process_mlx_file(input_file, output_file)
    print(f"Processed <{input_file}>, removed contents of code blocks and wrote to <{output_file}>.")

if __name__ == "__main__":
    main()

