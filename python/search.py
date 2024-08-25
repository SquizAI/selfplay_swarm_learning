from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import random
from concurrent.futures import ThreadPoolExecutor
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

# List of rare elements
RARE_ELEMENTS = [
    "Astatine", "Francium", "Rhenium", "Osmium", "Iridium", "Ruthenium",
    "Technetium", "Rhodium", "Palladium", "Tantalum", "Hafnium", "Scandium",
    "Tellurium", "Thulium", "Neptunium", "Protactinium", "Plutonium", "Promethium",
    "Curium", "Californium"
]

# Google Custom Search API configuration
API_KEY = "AIzaSyDVKT5fLzWzfvrRs4dlt_JOTaJ6CZou3sM"  # Your actual API key
CSE_ID = "f49c715abb2594dd5"    # Your actual custom search engine ID

def google_search(query, api_key, cse_id, num_results=3):
    """
    Function to perform a Google search using the Custom Search JSON API.
    """
    try:
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {'q': query, 'key': api_key, 'cx': cse_id, 'num': num_results}
        response = requests.get(url, params=params)
        response.raise_for_status()  # Ensure a successful request

        data = response.json()
        # Debugging: Print the response for analysis
        print(f"Google Search API Response for query '{query}':\n{data}")

        if 'items' not in data:
            print("No items found in the Google Search API response.")
            return {}

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error during Google search: {e}")
        return {}

def parse_links(results):
    """
    Function to parse links from the search results.
    """
    links = []
    if not results or 'items' not in results:
        print("No valid search results to parse links from.")
        return links

    for item in results.get('items', []):
        links.append(item['link'])  # Extract and append the link to the list

    # Debugging: Print the extracted links
    print(f"Extracted links: {links}")
    
    return links[:4]  # Limit to the first 4 links

def scrape_content(url):
    """
    Function to scrape the content from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join([para.get_text() for para in paragraphs])
        print(f"Scraped content from {url}:\n{content[:500]}...")  # Print first 500 characters
        return content
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None

def generate_summary(scraped_data):
    """
    Function to generate a summary of the content using Gemini.
    """
    if not scraped_data:
        return "No valid content to summarize."
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    concatenated_summary = "\n".join([f"URL: {url}\nContent: {text}" for url, text in scraped_data.items()])
    GENERATE_FORMATTED_SUMMARY_PROMPT = f"""Your task is to summarize a long text and break it down...
<text>
{concatenated_summary}
</text>"""
    try:
        result = llm.invoke(GENERATE_FORMATTED_SUMMARY_PROMPT)
        return result.content if result else "Summary generation failed."
    except Exception as e:
        print(f"Error during summary generation: {e}")
        return "Summary generation encountered an error."

def clean_scraped_data(scraped_data):
    """
    Function to clean and format the scraped website content using Gemini.
    """
    if not scraped_data:
        return "No valid content to clean."
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    concatenated_data = "\n".join([f"URL: {url}\nContent: {text}" for url, text in scraped_data.items()])
    CLEAN_SCRAPED_DATA_PROMPT = f"""Your task is to clean and format the following website content...
<text>
{concatenated_data}
</text>"""
    try:
        result = llm.invoke(CLEAN_SCRAPED_DATA_PROMPT)
        return result.content if result else "Content cleaning failed."
    except Exception as e:
        print(f"Error during content cleaning: {e}")
        return "Content cleaning encountered an error."

def perform_analysis(element):
    """
    Function to perform the full analysis of a given element.
    """
    query = f"{element} element properties"
    results = google_search(query, API_KEY, CSE_ID, num_results=4)
    links = parse_links(results)

    if not links:
        return {"element": element, "analysis": "No relevant links found during the search."}

    scraped_data = {}
    for link in links:
        content = scrape_content(link)
        if content:
            scraped_data[link] = content

    if not scraped_data:
        return {"element": element, "analysis": "No content could be scraped from the retrieved links."}

    with ThreadPoolExecutor() as executor:
        summary_future = executor.submit(generate_summary, scraped_data)
        clean_future = executor.submit(clean_scraped_data, scraped_data)

        summary_result = summary_future.result()
        clean_result = clean_future.result()

    return {
        "element": element,
        "scraped_data": scraped_data,
        "summary": summary_result,
        "cleaned_content": clean_result
    }

@app.route('/analyze/<element>', methods=['GET'])
def analyze_element(element):
    """
    Route to analyze a given element. Scrapes the web for relevant data.
    """
    try:
        element = element.capitalize()
        if element not in RARE_ELEMENTS:
            return jsonify({"error": "Invalid element or not in the list of rare elements."}), 400

        result = perform_analysis(element)

        if not result:
            raise ValueError("Failed to generate a valid analysis.")

        return jsonify(result)

    except Exception as e:
        print(f"Error during analysis: {traceback.format_exc()}")
        return jsonify({"element": element, "analysis": "Analysis failed. Please try again later."}), 500

@app.route('/analyze/random', methods=['GET'])
def analyze_random_element():
    """
    Route to analyze a randomly selected element.
    """
    random_element = random.choice(RARE_ELEMENTS)
    result = perform_analysis(random_element)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6060)
