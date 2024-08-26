import requests
from bs4 import BeautifulSoup
import json
import openai
import tiktoken

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Function to scrape all links from a given website
def scrape_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
    return links

# Function to retrieve and clean webpage content
def get_page_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text(separator=' ', strip=True)
    return content

# Function to generate questions using OpenAI GPT
def generate_questions(content):
    prompt = f"Generate 10 concise questions (less than 80 characters each) based on the following content:\n{content}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )
    questions = response.choices[0].text.strip().split("\n")
    return [q.strip() for q in questions if q.strip()]

# Function to identify relevant links from the scraped URLs
def identify_relevant_links(links, content, num_relevant=5):
    relevant_links = []
    for link in links:
        if len(relevant_links) >= num_relevant:
            break
        if link in content:
            relevant_links.append(link)
    return relevant_links

# Function to evaluate and validate the generated questions and links
def validate_output(questions, relevant_links):
    if len(questions) != 10 or not all(len(q) < 80 for q in questions):
        return False
    if len(relevant_links) < 2:
        return False
    return True

# Main function to process the entire workflow
def process_website(url):
    scraped_links = scrape_links(url)
    results = []

    for link in scraped_links:
        try:
            content = get_page_content(link)
            questions = generate_questions(content)
            relevant_links = identify_relevant_links(scraped_links, content)

            if validate_output(questions, relevant_links):
                results.append({
                    'url': link,
                    'content': content,
                    'questions': questions,
                    'relevant_links': relevant_links
                })
            else:
                print(f"Validation failed for {link}")
        except Exception as e:
            print(f"Error processing {link}: {e}")

    return results

# Save the results to a JSON file
def save_results_to_json(results, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)

# Example usage
if _name_ == "_main_":
    website_url = "https://example.com"  # Replace with your target website
    results = process_website(website_url)
    save_results_to_json(results)
    print("Processing complete. Results saved to output.json.")