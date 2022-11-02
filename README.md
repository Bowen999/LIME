# LIME: Large-scale Identification of Metabolomics Engine
Modern mass spectrometers can detect thousands of compounds in the biological samples with unprecedented sensitivity. And metabolomics is a technique to compare and discover the different of compounds (metabolites) in different samples. As a study primarily concerned with compounds in organisms, metabolomics is regarded as the most phenotype-reflective omics. One of the most challenging phases in metabolomics analysis is the annotation and identification of the compounds. Although many databases have been created and a huge number of compounds are present, there is not a complete overlap and no uniform naming standards among them, making manual large-scale searching become a highly time-consuming and error-prone task.  

LIME is a high-throughput metabolite annotation tool for post-processed liquid chromatography-mass spectrometry (LC-MS) metabolomic data.  
MS1 Features (m/z, retention time) that uploaded are searched for in LIME-integrated databases and sorted by score. The database of LIME includes 286,268 unique chemical structures when ignoring stereochemistry and charge, which were integrated from [Human Metabolome Database (HMDB)](https://hmdb.ca), [Chemical Entities of Biological Interest (ChEBI)](https://www.ebi.ac.uk/chebi/), and [LIPID MAPS](https://www.lipidmaps.org), three mainstream metabolite databases. InChIKey, a fixed-length format derived from [IUPAC International Chemical Identifier (InChI)](https://www.inchi-trust.org/) by hash, was used as the unique identifier of LIME.  
![featured](https://user-images.githubusercontent.com/87933959/199609413-63e3fe26-960e-4928-bb1d-cfef60115ef2.png)


## Input
input file should be a CSV file, first column is m/z, second column is retention time.  
<img width="912" alt="Screenshot 2022-11-02 at 5 55 53 PM" src="https://user-images.githubusercontent.com/87933959/199610047-fc034120-bc9e-438f-a54f-bccca7fe9be6.png">

## Output
### Putitave identity table
<img width="1070" alt="Screenshot 2022-11-02 at 5 56 36 PM" src="https://user-images.githubusercontent.com/87933959/199610151-ef3c2539-6698-4c04-9416-2e5b6ffbc11a.png">


### Statistical analysis 
![Figure_1](https://user-images.githubusercontent.com/87933959/199609825-10a8c7fd-0634-41ff-bda9-bce508a09de2.png)
![Figure_2](https://user-images.githubusercontent.com/87933959/199610248-461960f7-0d4a-4c49-8b4b-c06d50a1c2c3.png)

