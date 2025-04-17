
"""
Script to generate a CSV file of protein domains for use with ESM C.
- Scans a directory for PDB files
- Extracts PDB ID names (without extension)
- Extracts protein sequence from each PDB file
- Adds topology information from a preloaded dictionary (first part before underscore)
- Creates a CSV with columns: pdb, sequence, topology
"""
import os
import csv
import argparse
import pickle
from pathlib import Path

def extract_sequence_from_pdb(pdb_file):
    """Extract amino acid sequence from PDB file."""
    three_to_one = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'
    }
    
    sequence = []
    prev_residue_num = None
    
    with open(pdb_file, 'r') as f:
        for line in f:
            if line.startswith('ATOM') and line[12:16].strip() == 'CA':
                residue_name = line[17:20].strip()
                residue_num = int(line[22:26].strip())
                
                # Skip if this is a duplicate residue (same number)
                if residue_num == prev_residue_num:
                    continue
                
                prev_residue_num = residue_num
                
                if residue_name in three_to_one:
                    sequence.append(three_to_one[residue_name])
    
    return ''.join(sequence)

def get_first_part(topology_value):
    """Extract first part of topology value before first underscore."""
    if not topology_value:
        return ''
    
    # Split by underscore and take the first part
    return topology_value.split('_')[0]

def main():
    parser = argparse.ArgumentParser(description='Generate CSV file of protein domains for ESM C')
    parser.add_argument('--dir', type=str, default='.', help='Directory containing PDB files')
    parser.add_argument('--output', type=str, default='esm_domains.csv', help='Output CSV filename')
    parser.add_argument('--topology-file', type=str, default='/home/gridsan/akolodziej/PDZ_clean/PDZ_tm_align_results_3.pkl', 
                        help='Path to the pickle file containing topology dictionary')
    args = parser.parse_args()
    
    pdb_dir = Path(args.dir)
    output_file = args.output
    
    # Load topology dictionary
    try:
        with open(args.topology_file, 'rb') as f:
            topologies_dict = pickle.load(f)
        print(f"Loaded topology dictionary with {len(topologies_dict)} entries")
    except Exception as e:
        print(f"Error loading topology dictionary: {e}")
        print("Continuing without topology information...")
        topologies_dict = {}
    
    # Get all PDB files in the directory
    pdb_files = list(pdb_dir.glob('*.pdb'))
    print(f"Found {len(pdb_files)} PDB files in {pdb_dir}")
    
    # Create the CSV file
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['pdb', 'sequence', 'topology']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each PDB file
        for pdb_file in pdb_files:
            pdb_id = pdb_file.stem  # Get filename without extension
            pdb_filename = pdb_file.name  # Get filename with extension
            
            # Get topology if available and extract first part
            full_topology = topologies_dict.get(pdb_filename, '')
            topology = get_first_part(full_topology)
            
            try:
                sequence = extract_sequence_from_pdb(pdb_file)
                writer.writerow({
                    'pdb': pdb_id,
                    'sequence': sequence,
                    'topology': topology
                })
                print(f"Processed {pdb_id}: {len(sequence)} residues, topology: {topology or 'N/A'}")
            except Exception as e:
                print(f"Error processing {pdb_id}: {e}")
    
    print(f"CSV file created: {output_file}")

if __name__ == "__main__":
    main()