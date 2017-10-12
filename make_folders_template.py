#!/usr/bin/python

import os
import sys
import json
from collections import defaultdict
sys.path.append('/nfs/slac/g/suncatfs/data_catapp')
from tools import extract_atoms, check_reaction


"""
Dear all

Use this script to make the right structure for your folders.
Folders will be created automatically when you run the script with python.
Start by copying the script to a folder in your username,
and assign the right information to the variables below.

You can change the parameters and run the script several times if you,
for example, are using different functionals or are doing different reactions
on different surfaces.
"""

username = os.environ['USER']

# ---------publication info------------

title = 'Fancy title'  # work title if not yet published
authors = ['Doe, John', 'Einstein, Albert']  # name required
journal = ''
volume = ''
number = ''
pages = ''
year = '2017'  # year required
publisher = ''
doi = ''

DFT_codes = ['']  # for example 'Quantum ESPRESSO'
DFT_functionals = ['']  # For example 'BEEF-vdW'

#  ---------molecules info-----------

# reactants[i] -> products_A[i] + products_B[i]

reactions = [
    # Examples
    {'reactants': ['CCH3', 'CH3star'], 'products_A': ['C', 'CH3gas'], 'products_B': ['CH3', 'star']},
    ##{'reactants': ['COstar'], 'products_A': ['CO-COgas'], 'products_B': ['star']},
    #{'reactants': ['CH2star', 'CH3star'], 'products_A': ['CH4gas-H2gas', 'CH4gas-0.5H2gas'], 'products_B': ['star', 'star']},
]

"""
Include the phase if necessary:

'star' for empty site or adsorbed phase. Only necessary to put 'star' if
gas phase species are also involved.
'gas' if in gas phase

Remember to include the adsorption energy of reaction intermediates, taking
gas phase molecules as references (preferably H20, H2, CH4, CO, NH3).
For example, we can write the desorption of CH2 as:
CH2* -> CH4(g) - H2(g) + *
Here you would have to write 'CH4gas-H2gas' as "products_A" entry.

See example:
reactants = ['CH2star', 'CH3star']
products_A = ['CH4gas-H2gas', 'CH4gas-0.5H2gas']
products_B = ['star', 'star']
"""

# ---------------surface info---------------------

# If complicated structure: use term you would use in publication
surfaces = ['Pt']
facets = ['111']

#  ----------- You're done!------------------------

# Check reactions
for reaction_data in reactions:
    assert len(reaction_data['reactants']) == len(
        reaction_data['products_A']) == len(reaction_data['products_B'])
    for AB, A, B in zip(reaction_data['reactants'], reaction_data['products_A'], reaction_data['products_B']):
        check_reaction(AB, A, B)

# Set up directories
base = '/nfs/slac/g/suncatfs/data_catapp/%s/' % username

if not os.path.exists(base):
    os.mkdir(base)

publication_shortname = '%s_%s_%s' % (authors[0].split(',')[0].lower(),
                                      title.split()[0].lower(), year)

publication_base = base + publication_shortname + '/'

if not os.path.exists(publication_base):
    os.mkdir(publication_base)

# save publication info to publications.txt
publication_dict = {'title': title,
                    'authors': authors,
                    'journal': journal,
                    'volume': volume,
                    'number': number,
                    'pages': pages,
                    'year': year,
                    'publisher': publisher,
                    'doi': doi,
                    }

pub_txt = publication_base + 'publication.txt'
json.dump(publication_dict, open(pub_txt, 'wb'))


def tree():
    return defaultdict(tree)

create = tree()  # list of directories to be made
for DFT_code in DFT_codes:
    create[DFT_code]
    for DFT_functional in DFT_functionals:
        create[DFT_code][DFT_functional]
        for reaction_data in reactions:
            for i in range(len(reaction_data['reactants'])):
                reaction = '%s_%s_%s' % (reaction_data['reactants'][i], reaction_data[
                                         'products_A'][i], reaction_data['products_B'][i])
                create[DFT_code][DFT_functional][reaction]
                for surface in surfaces:
                    create[DFT_code][DFT_functional][reaction][surface]
                    for facet in facets:
                        create[DFT_code][DFT_functional][
                            reaction][surface][facet]


def rec(directory, current_path):
    """
    Create tree of directories from dictionary
    Credit: https://stackoverflow.com/questions/22058010/python-create-file-directories-based-on-dictionary-key-names
    """
    if len(directory):
        for direc in directory:
            rec(directory[direc], os.path.join(current_path, direc))
    else:
        if not os.path.exists(current_path):
            os.makedirs(current_path)
            print(' - created {current_path}'.format(**locals()))

rec(create, publication_base)