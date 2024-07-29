## About

This open-source project aims to develop an innovative directory specifically for Open Source (O/S) software providers and service vendors. The project stands out in its thematic focus, being the only existing directory dedicated to this niche, and employs advanced methodologies to collect and curate its listings.

### Key Features

1. **Multi-Criteria Search:**
   - The directory allows users to search for O/S vendors and service providers using multiple criteria, ensuring that users can find precisely what they need based on a variety of parameters.

2. **Innovative Information Extraction:**
   - The project leverages cutting-edge technologies to extract information from various sources. This includes data scraping from official sources like INSEE and the websites of the companies themselves. The extraction process uses:
     - **SpaCy**: An open-source Natural Language Processing (NLP) framework in Python, known for its efficiency and versatility in handling large-scale text data.
     - **Semantic Alignment with Wikidata**: Ensuring that the extracted information is accurate and contextually relevant by aligning it semantically with data from Wikidata.

3. **Future Integration of Advanced AI:**
   - There are plans to integrate or test advanced AI technologies such as GPT-4 or equivalent open-source models in the future. These AI models will further enhance the accuracy and comprehensiveness of the information extraction process.

### Economic and Valuation Impact

The directory is designed to be a highly useful tool at the economic level. By providing a centralized, comprehensive, and easily searchable database of O/S providers, it adds significant value to the open-source ecosystem. Businesses and individuals can more easily find and connect with O/S vendors, fostering greater collaboration and growth within the industry.

### Planned European Dimension

The project currently focuses on local members but envisions expanding to include a European-wide directory. This European expansion will involve:

- Creating a variant localized for European members, starting with the CNLL (Conseil National du Logiciel Libre) members.
- Developing algorithms capable of searching pre-existing indexes or performing crawls to identify European companies in the O/S sector.
- Utilizing content analysis algorithms to ensure the directory's comprehensiveness and relevance.

### Technical Implementation

1. **Information Extraction Using SpaCy:**
   - SpaCy is employed to process large amounts of text data efficiently, extracting relevant details about O/S vendors from various sources.

2. **Semantic Alignment with Wikidata:**
   - The project uses semantic alignment techniques to ensure that the extracted data is not only accurate but also contextually relevant, leveraging the vast and structured dataset available on Wikidata.

### Future Development Goals

1. **Integration with Advanced AI Models:**
   - The project plans to explore the use of GPT-4 or similar open-source models to further refine the extraction and categorization processes.

2. **European Directory Expansion:**
   - By incorporating sophisticated search and content analysis algorithms, the project aims to expand its scope to cover the entire European market, providing a valuable resource for the continent's O/S ecosystem.

## Installation

To install the necessary dependencies, run the following command:

```bash
poetry shell
poetry install
```

## Tests

To run the tests, use the following command:

```bash
pytest
# or
make test
# or
nox
```
