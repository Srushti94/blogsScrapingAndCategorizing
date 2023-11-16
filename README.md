# Blog Scraping and Categorization Script

This python script is designed to scrape the latest 5 articles from specified blogs, extract details such as title, author(s), publication date, and article text. It categorizes the article based on predefined keywords. This script utilizes `requests`, `BeautifulSoup`, `pandas`, and `sqlite3` libraries for web scraping, data manipulation, and SQLite datbase interaction.

## Prerequisites

Before running the script, make sure you have the necessary libraries installed. You can install them using the following command:

```
pip install beautifulsoup4
pip install requests
```

## Usage
1. Clone the Repository:
```
git clone https://github.com/yourusername/blog-scraping-script.git
cd blog-scraping-script
```

2. Run the Script:

Execute the script using the following command:

```
python blog_scraping_script.py
```
The script will scrape the latest articles from the specified blogs, categorize them, and store the data in an SQLite database named blog_scraping.sqlite.

3. Output:

The script will create a table named `ten_latest_blogs` in the SQLite database, containing the details of the ten latest articles from both blogs, along with their assigned categories.

### Customization
The script uses predefined categories and keywords for categorizing articles. You can modify the categories_keywords dictionary in the script to suit your specific categorization needs.