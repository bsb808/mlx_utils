#!/usr/bin/env python3

import zipfile
import tempfile
import os
#import shutil
import xml.etree.ElementTree as ET
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
                print("--")
                print(etree.tostring(p_t, pretty_print=True, encoding='unicode'))
                p_t.text = etree.CDATA("% Your code here.       ")
            
    # Write the modified XML back to a file
    # Using xml_declaration=True to include the XML declaration in the output file
    for of in [output_file, './tmp.xml']:
        with open(of, 'wb') as f:
            #f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(etree.tostring(root, pretty_print=False, xml_declaration=False, encoding='UTF-8'))
    

# def replace_code_blocks_in_file(input_file, output_file):
#     # Define namespaces
#     ns = {
#         'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
#         'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'
#     }

#     # Parse the XML file
#     tree = ET.parse(input_file)
#     root = tree.getroot()

#     # Iterate through all <w:p> elements in the document
#     for p in root.findall('.//w:p', ns):
#         # Check if <w:p> has a style <w:pStyle> with value "code"
#         p_style = p.find('.//w:pPr/w:pStyle', ns)
#         if p_style is not None and p_style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'code':
#             # Check if it's inside mc:AlternateContent and skip those
#             if p.find('.//mc:AlternateContent', ns) is not None:
#                 continue

#             # Find the <w:t> element that contains the CDATA
#             t_element = p.find('.//w:r/w:t', ns)
#             if t_element is not None:
#                 # Check if the CDATA block contains specific code to replace
#                 if t_element.text and ('x = 1' in t_element.text or '% Remove' in t_element.text):
#                     # Replace CDATA content with the new text
#                     t_element.text = '% Your code here'

#     # Write the modified XML back to a file
#     tree.write(output_file, encoding='utf-8', xml_declaration=True)


def process_mlx_file(input_filename, output_filename):
    tmp_dir = tempfile.TemporaryDirectory()
    # Perform operations in the directory
    tmp_dir.cleanup()  # Manually remove the direc
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

        print("Clean up temp dir")
        # Perform operations in the directory
        #temp_dir.cleanup()  # Manually remove the direc

    tmp_dir = tempfile.TemporaryDirectory()
    # Perform operations in the directory
    tmp_dir.cleanup()  # Manually remove the direc

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

  If no output file is specified, the script will create a new file with '_assign' 
  appended to the original filename (before the extension).
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
    print(f"Processed {input_file} and created {output_file}")

if __name__ == "__main__":
    main()

