# loading all required libraries
from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import pandas as pd

# URLs for web scraping
url_varicent = 'https://www.varicent.com/blog'
url_everstage = 'https://www.everstage.com'

# Categories and corresponding keywords (category keywords taken from the input document)
categories_keywords = {
    'Finance': ['economics', 'stock market', 'financial management', 'investment', 'capital', 'fiscal policy'],
    'Marketing': ["marketing strategy", "consumer behavior", "branding", "advertising", "market research", "digital marketing"],
    'Human Resources (HR)': ["recruitment", "talent management", "organizational culture", "employee engagement", "workforce planning", "diversity and inclusion"],
    'Operations Management': ["supply chain", "logistics", "production", "quality control", "inventory management", "operational efficiency"],
    'Information Technology (IT)': ["information systems", "cybersecurity", "data analytics", "software development", "cloud computing", "IT infrastructure"],
    'Entrepreneurship': ["start-up", "venture capital", "innovation", "business model", "scaling business", "entrepreneurial finance"],
    'Strategy': ["competitive strategy", "business planning", "strategic management", "corporate governance", "business policy", "organizational strategy"]
}


def crawlWebPage(url):
    # Fetching web pages
    webpage = requests.get(url)
    # Encoding to utf-8
    webpage.encoding = 'utf-8'
    # Creating BeautifulSoup objects for parsing HTML
    return BeautifulSoup(webpage.text, 'html.parser')

def create_dataframe(titles, author_names, dates, article_urls, article_texts):
    # Creating a DataFrame for Everstage blog data
    data = {
        'title': titles,
        'author': author_names,
        'publication_date': dates,
        'article_url': article_urls,
        'article_text': article_texts
    }
    return pd.DataFrame(data)

def createEverstageBlogDataframe() :
    # Adding /blog for everstage url to get the correct url for all article_text
    soup_everstage = crawlWebPage(url_everstage + '/blog')

    # Extracting title and artilce_url data from Everstage blog
    titles = []
    article_urls = []
    blog_everstage = soup_everstage.find_all(class_='blog-title-link w-inline-block')
    for i in blog_everstage: 
        titles.append(i.contents[0].get_text())
        article_urls.append(url_everstage + i['href'])

    # Extracting author name and publication date data from Everstage blog
    author = soup_everstage.find_all(class_= 'author-name')
    author_names = [author_name.text.strip() for author_name in author]

    pub_date = soup_everstage.find_all(class_= 'post-date')
    publication_dates = [date.text.strip() for date in pub_date]

    # Formatting publication dates
    dates = []
    for date in publication_dates:
        date = date.split(" ")
        #using date[0][:3] to get the same date format for featured article and other articles 
        dates.append((date[0][:3] + ' ' + ' '.join(date[1:])))

    # Creating a DataFrame for Everstage blog data
    data = {
        'title': titles,
        'author': author_names,
        'publication_date': dates,
        'article_url': article_urls
    }
    everstage_blog_temp_df = pd.DataFrame(data)

    # Cleaning and filtering DataFrame
    # Converting publication date from object format to datetime format
    everstage_blog_temp_df['publication_date'] =  pd.to_datetime(everstage_blog_temp_df['publication_date'], format='%b %d, %Y', errors='coerce')
    everstage_blog_temp_df = everstage_blog_temp_df[everstage_blog_temp_df.publication_date.notnull()]
    # Extracting the 5 latest articles published from the dataframe
    everstage_blog_temp_df = everstage_blog_temp_df.sort_values(by= 'publication_date', ascending=False).head(5)

    # Extracting article body from Everstage blog
    article_texts = []
    for page in everstage_blog_temp_df.article_url:
        soup = crawlWebPage(page)
        article_texts.append(soup.find_all('div', class_='blog-rich-text w-richtext')[0].text.strip())

    # Creating datafram for Everstage blog data.
    return create_dataframe(everstage_blog_temp_df.title, everstage_blog_temp_df.author, everstage_blog_temp_df.publication_date, everstage_blog_temp_df.article_url, article_texts)

def createVaricentBlogDataframe():
    # Extracting data from Varicent blog
    # Extracting url and title of the featured articles
    soup_varicent = crawlWebPage(url_varicent)
    header_blogs = soup_varicent.find_all(class_ = 'post-title')
    titles = []
    article_urls = []
    for blog in header_blogs:
        article_urls.append(blog.contents[0]['href'])
        titles.append(blog.contents[0].get_text())
    # Extracting url and title from the rest of the articles
    body_blogs = soup_varicent.find_all('h2', class_ = 'h7 mt-2 mb-3')
    for blog in body_blogs:
        article_urls.append(blog.contents[0]['href'])
        titles.append(blog.contents[0].get_text())

    # Extracting additional data from Varicent blog
    published_dates = []
    article_texts = []
    authors = []
    for url in article_urls:
        soup = crawlWebPage(url)
        script_tag = soup.find_all('script', type='application/ld+json')
        json_data = json.loads(str(script_tag[0].contents[0]))
        published_dates.append(json_data.get('datePublished').split('T')[0])
        article_texts.append(soup.find('span', id='hs_cos_wrapper_post_body').get_text())
        authors.append(soup.find('div', class_='col-auto blog-post-author-title').a.get_text().strip())

    # Creating a DataFrame for Varicent blog data
    varicent_blog_df = create_dataframe(titles, authors, published_dates, article_urls, article_texts)

    # Cleaning and filtering DataFrame
    varicent_blog_df['publication_date'] =  pd.to_datetime(varicent_blog_df['publication_date'], format='%Y-%m-%d', errors='coerce')
    return varicent_blog_df.sort_values(by='publication_date', ascending=False).head(5)


# Function for categorization
def categorize_article(article_text, categories):
    for category, keywords in categories.items():
        if any(keyword in article_text.lower() for keyword in keywords):
            return category
    return 'Uncategorized'


def exportToSqlite(dataframe):
    # Connecting to SQLite database
    conn = sqlite3.connect('blog_scraping.sqlite')
    # Creating a table based on the DataFrame
    dataframe.to_sql('ten_latest_blogs', conn, if_exists='replace')
    # Closing the connection
    conn.close()

def main():
    # Crawl blogs and get latest 5 blogs from each websites.
    everstage_blog_df = createEverstageBlogDataframe()
    varicent_blog_df = createVaricentBlogDataframe()
    # Concatenating DataFrames
    concatenated_df = pd.concat([everstage_blog_df, varicent_blog_df])
    # Applying categorization to the concatenated DataFrame
    category =[]
    for article_text in concatenated_df.article_text:
        category.append(categorize_article(article_text, categories_keywords))
    concatenated_df['category'] = category

    # Dropping unnecessary column
    concatenated_df = concatenated_df.drop(columns = 'article_url')
    exportToSqlite(concatenated_df)

if __name__ == "__main__":
    main()
