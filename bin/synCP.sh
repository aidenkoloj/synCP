#!/bin/bash

##############################################################################
# Script for Generating Synthetic Circular Permutations
#
# This script:
#   1. Downloads a PDB file based on provided ID or uses provided file (input is name without extension)
#   2. Cleans the PDB file (removes header and heteroatoms)
#   3. Isolates only chain A 
#   4. Renumbers residues starting from 1
#   5. Generates all possible synthetic circular permutations
#   6. Reorders the synCP from 1 
#
# Usage: ./script_name.sh <pdb_id> or <protein_file_name>
# Example: ./script_name.sh 2gtg
# Example: ./script_name.sh d1qzya1 (if d1qzya1.pdb exists in data directory and does not have END or TER lines)
##############################################################################

# Input validation
if [ $# -eq 0 ]; then
    echo "Error: No PDB ID provided"
    echo "Usage: $0 <pdb_id>"
    exit 1
fi

# Variables
pdb_input="$1"                            # PDB ID of interest
parent_dir=$(dirname $(pwd))               # Parent directory
data_dir="$parent_dir/data"                # Data storage directory
output_dir="$data_dir/${pdb_input}_synCPs" # Output directory for synthetic CPs
pdb_file="$data_dir/${pdb_input}.pdb"      # Path for the processed PDB file


# Create necessary directories
if [ ! -d "$data_dir" ]; then
    echo "Creating data directory at $data_dir..."
    mkdir -p "$data_dir"
fi

# Download and process PDB file if it doesn't exist
if [ -f "$pdb_file" ]; then
    echo "PDB file $pdb_input already exists at $pdb_file"
    echo "Cleaning $pdb_file"
    /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_selchain -A ${pdb_file} | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_delhetatm | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_reres -1 | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_keepcoord | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_head -10000000 > "${pdb_file}_clean"
    mv "${pdb_file}_clean" "$pdb_file"

else
    echo "Downloading and processing $pdb_input..."
    
    /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_fetch ${pdb_input} | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_selchain -A | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_delhetatm | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_reres -1 | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_keepcoord | \
        /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_head -10000000 > "$pdb_file"
    
    if [ -f "$pdb_file" ]; then
        echo "Successfully downloaded and processed $pdb_input"
    else
        echo "Failed to download or process $pdb_input"
        exit 1
    fi
fi

# Create output directory for synthetic CPs if it doesn't exist
if [ -d "$output_dir" ]; then
    echo "synCPs directory already exists at $output_dir"
else
    echo "Creating output directory for synthetic CPs..."
    mkdir -p "$output_dir"
fi

# synCP generation
echo "Generating synCPs in directory $outputdir"
python synCP_generate.py $pdb_file $output_dir

echo "Reordering the residue numbering for synCPs"

for file in $output_dir/*; do
    reres_name="${file}_reres"
    /home/ubuntu/miniforge3/envs/foldseek/bin/pdb_reres -1 "$file" > "$reres_name"
    mv "$reres_name" "$file"
done

# End of script message
echo "Processing complete for $pdb_input"
