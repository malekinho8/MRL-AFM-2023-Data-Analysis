from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

# Create a molecule object for Rhodamine B using its SMILES string
rhodamine_b_smiles = "CCN(C(C)C)c1ccc2c(c1)C(=O)c3ccccc3C2=O"
rhodamine_b_mol = Chem.MolFromSmiles(rhodamine_b_smiles)

# create a molecule object for c9-anedithiol using its SMILES string (SCCCCCCCCCS)
c9_anedithiol_smiles = "SCCCCCCCCCS"
c9_anedithiol_mol = Chem.MolFromSmiles(c9_anedithiol_smiles)

# Add Hydrogens
rhodamine_b_mol = Chem.AddHs(rhodamine_b_mol)
c9_anedithiol_mol = Chem.AddHs(c9_anedithiol_mol)

# use the GetDistanceMatrix function to get the distance matrix
# for the molecule
distance_matrix = Chem.GetDistanceMatrix(rhodamine_b_mol)
distance_matrix_c9 = Chem.GetDistanceMatrix(c9_anedithiol_mol)

# calculate the max size of the molecule based on the distance matrix
max_size = np.max(distance_matrix)
max_size_c9 = np.max(distance_matrix_c9)

# Print the distance matrix
print(distance_matrix)
