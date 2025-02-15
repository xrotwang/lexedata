---
title: 'Lexedata: A Python toolbox to edit CLDF lexical datasets'
tags:
  - Python
  - linguistics
  - wordlist
  - cross-linguistic data format
authors:
  - name: Gereon A. Kaiping
    orcid: 0000-0002-8155-9089
    affiliation: 1
  - name: Melvin S. Steiger
    orcid: 0000-0001-7300-0704
    affiliation: 2
  - name: Natalia Chousou-Polydouri
    orcid: 0000-0002-5693-975X
    affiliation: "2,3"
affiliations:
 - name: Department of Geography, Universität Zürich, CH
   index: 1
 - name: Department of Comparative Linguistics, Universität Zürich, CH
   index: 2
 - name: Center for the Interdisciplinary Study of Language Evolution, Universität Zürich, CH
   index: 3
date: 01 February 2022
bibliography: bibliography.bib
---
# Summary
Lexedata is a collection of tools to support the editing process of comparative
lexical data. Wordlists are a comparatively easily
collected type of language documentation that is nonetheless quite data-rich and useful for the systematic
comparison of languages [@list2021lexibank]. They are an important resource in
comparative and historical linguistics, including their use as raw data for
language phylogenetics [@gray2009language;@grollemund2015bantu].

The `lexedata` python package uses the “Cross-Linguistic Data Format” (CLDF,
@cldf11, @cldf-paper) as main data format for a relational database containing
forms, languages, concepts, and etymological relationships. The CLDF
specification builds on top of the CSV for the Web (CSVW,
@pollock2015metadata) specs by the W3C, and as such consists of one or more
comma-separated value (CSV) files that get their semantics from a metadata file
in JSON format.

# Statement of Need
Maintaining the integrity as relational database is difficult using general CSV
editing tools. This holds in particular for the usual dataset size of
hundreds of languages and concepts, and formats unfamiliar to most linguists.

![Overview over the functionality in Lexedata.\label{fig:structure}](structure.png)

The individual Python scripts of Lexedata implement various helper functions
that frequently arise when working with comparative wordlists for multiple
languages, as shown in \autoref{fig:structure}. Tasks include importing data
from MS Excel sheets of various common formats into CLDF, Automatic Cognate
Detection (ACD, @list2017potential) using Lexstat [@list2012lexstat], checking
for homophones, or manipulating etymological judgements. Lexedata provides
import and export functions to formats more familiar to linguists, and checks
integrity for bulk edit and import functions it provides.

# Research use
The export to phylogenetic alignments, derived from BEASTling
[@maurits2017beastling;@beastling14], has already been used in different language
phylogenetics projects that are currently under review
[@kaiping2019subgrouping;@kaiping2021burst]. The
more extensive lexical dataset editing functionality is used by projects
at UC Berkeley and Universität Zürich for Arawakan and Mawetí-Guaraní languages
and
at Universiteit Gent for Bantu [@gunnink2022bantu].
Precursor scripts have also
been used for Timor-Alor-Pantar and Austronesian languages [@lexirumah-paper].

# Acknowledgement
Development of Lexedata was funded by the Swiss National Science Foundation
(SNSF) Sinergia Project “Out of Asia” CRSII5_183578.

# References
