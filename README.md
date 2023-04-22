# Say Cheese!🫡 507_final_project

### How to interact with the program:

I have created a user interface using flask, and have add links to all the main functions in the flask app homepage. User may download my project code and install required packages, and then start from flask's local homepage: http://localhost:5000/ to play around with my program.

The functions on http://localhost:5000/ include:
- 5 live charts build based on the cheese data, including cheese origins by country and by state (map + barchart), pirchart of US cheese's rind distribution, a similarity cheese network based on how many common attributes cheeses share among each other.
- Users can also enter their favored cheeses to get most similar or different cheeses.

### Required Python Packages:
- Flask
- requests
- BeautifulSoup (bs4)
- json
- re
- networkx
- plotly
- pyvis
- pandas
- numpy

### Data Sources
#### cheese.com
- URLs for data and documentation: https://www.cheese.com/ 
- Formats: HTML
- Access: Scraped URLs and cheese data from cheese.com using the BeautifulSoup library in Python. Cached the URLs in a "urls.json" file to reduce website requests.
- Summary:
  - Records available: 1800
  - Records retrieved: 1800 (cached in "cheese_cache.json")
- Description:
  - Each record represents a cheese variety and includes name, country of origin, region, type, fat content, texture, color, flavor, aroma, vegetarian, producers, synonyms and description.
  - Important fields/attributes for the project: 
    - name, url, milk, country of origin, region, type, fat content, texture, rind, color, flavor, vegetarian, description

#### Urls.json
- URLs for data and documentation: https://github.com/HaihongZheng001/507_final_project/blob/main/data/urls.json
- Format(s): JSON
- Access: Created a "urls.json" file to cache the URLs of cheese varieties on cheese.com, reducing website requests.
- Summary:
  - Records available: 1800 (same as number of cheese records in "cheese_cache.json")
  - Records retrieved: 1800
- Description:
  - Stored record as dictionaries and saved as json file.
  - Each record contains the URL for a cheese variety on cheese.com.
  - The key is the name of the cheese, and the value of the key is the url that can be add to the base url cheese.com/ to retrieve the corresponding cheese data.

#### Cheese_cache.json
- URLs for data and documentation: https://github.com/HaihongZheng001/507_final_project/blob/main/data/cheese_cache.json
- Format(s): JSON
- Access: Cached the raw data for 1800 cheese varieties on cheese.com using the requests library and beautiful soup in Python, stored in a "cheese_cache.json" file to reduce website requests.
- Summary:
  - Records available: 1800
  - Records retrieved: 1800
- Description:
  - Stored each cheese variety data as a dictionary in a list.
  - Each record contains the raw data for a cheese variety on cheese.com and can speed up later data cleaning work.
  - Attributes include name, url, milk, country of origin, region, type, texture, rind, color, flavor, aroma, vegetarian, synonyms, description.

#### filtered_cheese_cache.json

- URLs for data and documentation: https://github.com/HaihongZheng001/507_final_project/blob/main/data/filtered_cheese_cache.json
- Format(s): JSON
- Access: Read cached complete cheese data locally, stored the filtered data in a "filtered_cheese_cache" file for later use in the project.
- Summary:
    Records available: 1125((some removed due to missing attributes)     
    Records retrieved: 1800

    Description:
    Contains filtered cheese data including Name, URL, Description, Country of origin, Region, Type, Milk, Rind, Texture, Flavor, Color, Aroma.
    Split type, milk, rind, texture,, flavor, aroma attributes for later analysis of similarity among cheeses

#### us_state_code_dict.json

- URLs for data and documentation: https://github.com/HaihongZheng001/507_final_project/blob/main/data/us_state_code_dict.json
- Format(s): JSON
- Access: Get the list of all state code online, using a dictionary format to store the state name and code.
- Summary:
    Records available: 50
    Records retrieved: 50

    Description: a dictionary of the US state names and code.

###### us_state_name_dict.json

- URLs for data and documentation: https://github.com/HaihongZheng001/507_final_project/blob/main/data/us_state_name_dict.json
- Format(s): JSON
- Access: Manually format the state names.
- Summary:
    Records available: 50
    Records retrieved: 50

    Description: Manually created list and match state names using the same format. Eg: NY -> New York, city name -> state name

## Interaction and Presentation Options 

### Description:

#### Intro: 
The cheese program provides a flask app for user interaction. Users can view live charts, network and get recommendations of cheeses based on the cheese similarity network.

#### Users can see:
- Common and Unique Cheese: displays the list of common/unique(have most/fewest similarities with other cheeses in aroma and flavor among the cheese network
- Similar and Different Cheese: displays a comparison of user chosen cheese and other cheeses, 
- Cheese Origin by Country/State Map: displays a map of the world/US, color-coded by the countries/state where the cheeses originates from.
- Cheese Origin by Country/State Barchart: displays a bar chart showing the number of cheese varieties originating from each country/state, 
- US Cheese Rind Pie Chart: displays a pie chart showing the percentage of cheese varieties in the US with different types of rinds.
- Cheese Similarity Network: displays an interactive network diagram showing the similarities in aroma and flavor between different cheese varieties. However, this option may take a few minutes to load due to its interactive nature. So I provided a screenshot option to give a preview.

### Interactive and presentation technologies:
Flask, plotly, pyvis

### How to interact:
Users can download project code, install and import required packages, then run the flask app locally. Start from the flask home page, click the links to each function and see/interact with the cheese program.

### Demo Link

