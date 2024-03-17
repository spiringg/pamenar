import os  # Add this line
import requests
import jinja2 
from bs4 import BeautifulSoup 
import urllib.parse 
import socket




API_KEY = "AIzaSyAFEQrookitKCFMpcAlOlj6fmJZWEHZdl8" 
PROJECT_ID = "f368b2f9038cd4f85"  


VERSION = "1.5"  # Update as needed



def calculate_keyword_density(text, keyword):
    text = text.lower()
    keyword = keyword.lower()
    word_count = len(text.split())  
    keyword_count = text.count(keyword)
    if word_count == 0:
        return 0.0 
    else:
        return (keyword_count / word_count) * 100

def get_seo_data(keyword, target_region=None): 
 # Optional target_region
    gl_value = None  # Initialize gl_value



    if target_region:   
        # Construct API URL with 'gl' parameter if target_region is provided
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={PROJECT_ID}&q={keyword}&gl={target_region}"
        gl_value = target_region
    else:
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={PROJECT_ID}&q={keyword}"

    response = requests.get(url)
    response.raise_for_status() 

    data = response.json()
    items = data.get('items', [])  
    headers = {
        'User-Agent': 'MySEOAnalysisScript/1.6 (https://mywebsite.com)'  
    }
    output_data = []
    for result in items[:5]:
        title_density = calculate_keyword_density(result.get('title', ''), keyword)
        desc_density = calculate_keyword_density(result.get('snippet', ''), keyword)

        # Extract and count headings
        link = result.get('link')
        response = requests.get(link) 
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')

        paragraph_count = len(paragraphs)
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        heading_data = []
        heading_counts = {f"h{i}": 0 for i in range(1, 7)} 

        for heading in headings:
            heading_tag = heading.name  
            heading_counts[heading_tag] += 1  
            heading_data.append({
                "tag": heading_tag, 
                "text": heading.text.strip(),  
            })
        # Calculate keyword density in paragraphs
        all_paragraph_text = " ".join([p.text for p in paragraphs])
        paragraph_density = calculate_keyword_density(all_paragraph_text, keyword)

        # Extract images and count by type
        images = soup.find_all('img')
        image_counts = {}

        for image in images:
            src = image.get('src')
            if src: 
                _, file_extension = os.path.splitext(src)  
                image_type = file_extension.lstrip('.').lower()  
                image_counts[image_type] = image_counts.get(image_type, 0) + 1  

        # Attempt to find dates
        publish_date = soup.find("meta", attrs={"name": "date"}) 
        if publish_date:
            publish_date = publish_date.get("content")

        modify_date = soup.find("meta", attrs={"property": "article:modified_time"})
        if modify_date:
            modify_date = modify_date.get("content")










 # Extract links
        link = result.get('link')
        response = requests.get(link) 
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')

        internal_links = 0
        external_links = 0
        base_url = urllib.parse.urlparse(link).netloc  # Get the base domain

        for a_tag in links:
            href = a_tag.get('href')
            if href:
                link_domain = urllib.parse.urlparse(href).netloc 
                if link_domain == base_url:
                    internal_links += 1
                else:
                    external_links += 1
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        meta_data = []
        for tag in meta_tags:
            meta_data.append({
                'name': tag.get('name'),
                'property': tag.get('property'), 
                'content': tag.get('content')
            })

        output_data.append({
            "title": result.get('title'),
            "description": result.get('snippet'),
            "url": result.get('link'),
            "title_length": len(result.get('title', '')),
            "desc_length": len(result.get('snippet', '')), 
            "keyword_in_title": keyword.lower() in result.get('title', '').lower(),
            "keyword_in_desc": keyword.lower() in result.get('snippet', '').lower(),
            "title_density": title_density,
            "desc_density": desc_density,
            "headings": heading_data,
            "heading_counts": heading_counts,  
         "image_counts": image_counts,
            "publish_date": publish_date,
            "modify_date": modify_date,
            'meta_tags': meta_data,
            'paragraph_count': paragraph_count,
            'paragraph_density': paragraph_density,
            'internal_links': internal_links,
            'external_links': external_links,
            'script_ip_address': socket.gethostbyname(socket.gethostname()),
            'gl_parameter': gl_value,
'user_agent': headers['User-Agent']  # Store the user agent            
        })

    return output_data

# ... rest of your code (Jinja2 template loading, etc.) ...















if __name__ == "__main__":
    keyword = input("Enter your keyword: ")
    results = get_seo_data(keyword)

    template_loader = jinja2.FileSystemLoader("./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("results.html")
    output_text = template.render(results=results, VERSION=VERSION, keyword=keyword) 

    with open("seo_results.html", "w", encoding='utf-8') as f:
        f.write(output_text)
