from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime

app = Flask(__name__)


## CANADA PRIME RATE STATS 
def get_canada_prime_rate_stats():
    url = "https://ycharts.com/indicators/canada_prime_rate"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find the "Stats" heading (could be h3, h4, etc.)
    stats_heading = soup.find(lambda tag: tag.name in ["h3", "h4", "h5"] and "Stats" in tag.get_text())
    
    if not stats_heading:
        raise ValueError("Could not locate 'Stats' section")
    
    # Try to find the container right after the heading
    container = stats_heading.find_next_sibling()
    if not container:
        container = stats_heading.parent.find_next_sibling()

    stats_data = []

    # Try definition list first
    dts = container.find_all("dt") if container else []
    dds = container.find_all("dd") if container else []
    if dts and len(dts) == len(dds):
        for dt, dd in zip(dts, dds):
            label = dt.get_text(strip=True)
            value_text = dd.get_text(strip=True)  # Keep original text
            stats_data.append({"label": label, "value": value_text})
        return stats_data

    # If not <dl>, try generic div/span pairs
    rows = container.find_all("div") if container else []
    for row in rows:
        spans = row.find_all("span")
        if len(spans) >= 2:
            label = spans[0].get_text(strip=True)
            value_text = spans[1].get_text(strip=True)  # Keep original text
            stats_data.append({"label": label, "value": value_text})

    # If still empty, try broader search near heading
    if not stats_data:
        # Look for any text containing common stat labels
        possible_labels = ["Last Value", "Latest Period", "Last Updated", "Next Release", "Long Term Average", "Average Growth Rate", "Value from Last Week", "Change from Last Week", "Value from 1 Year Ago", "Change from 1 Year Ago", "Frequency"]
        
        for label_text in possible_labels:
            elem = soup.find(string=lambda text: text and label_text in text)
            if elem:
                parent = elem.parent
                # Look for the next element that contains either a percentage OR looks like a date
                # Find the next sibling that has text content
                next_elem = parent.find_next(string=True)
                if next_elem:
                    # Navigate up to the parent element and get all text siblings
                    current_elem = parent.next_sibling
                    while current_elem:
                        if hasattr(current_elem, 'get_text'):
                            value_text = current_elem.get_text(strip=True)
                            if value_text and (('%' in value_text) or 
                                             any(month in value_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or
                                             value_text.replace('.', '').replace(',', '').replace(' ', '').isdigit()):
                                stats_data.append({"label": label_text, "value": value_text})
                                break
                        elif hasattr(current_elem, 'string') and current_elem.string:
                            value_text = current_elem.string.strip()
                            if value_text and (('%' in value_text) or 
                                             any(month in value_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or
                                             value_text.replace('.', '').replace(',', '').replace(' ', '').isdigit()):
                                stats_data.append({"label": label_text, "value": value_text})
                                break
                        current_elem = current_elem.next_sibling

    return stats_data

@app.route('/canada-rate-stats', methods=['GET'])
def canada_prime_rate_stats():
    try:
        data = get_canada_prime_rate_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## CANADA PRIME RATE AND DATE
def get_canada_prime_rate_history():
    url = "https://ycharts.com/indicators/canada_prime_rate"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table", class_="table")
    
    all_data = []
    for table in tables:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                date_text = cols[0].get_text(strip=True)
                rate_text = cols[1].get_text(strip=True).replace("%", "")
                
                # Skip rows that don't look like real dates
                if not any(month in date_text for month in [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]):
                    continue

                try:
                    parsed_date = datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    continue  

                try:
                    rate = float(rate_text)
                except ValueError:
                    continue

                all_data.append({
                    "date": parsed_date,
                    "prime_rate": rate
                })
    
    return all_data

@app.route('/canada-prime-rate', methods=['GET'])
def canada_prime_rate():
    try:
        data = get_canada_prime_rate_history()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## USA PRIME RATE STATS
def get_us_prime_rate_stats():
    url = "https://ycharts.com/indicators/us_bank_prime_loan_rate"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find the "Stats" heading (could be h3, h4, etc.)
    stats_heading = soup.find(lambda tag: tag.name in ["h3", "h4", "h5"] and "Stats" in tag.get_text())
    
    if not stats_heading:
        raise ValueError("Could not locate 'Stats' section")
    
    # Try to find the container right after the heading
    container = stats_heading.find_next_sibling()
    if not container:
        container = stats_heading.parent.find_next_sibling()

    stats_data = []

    # Try definition list first
    dts = container.find_all("dt") if container else []
    dds = container.find_all("dd") if container else []
    if dts and len(dts) == len(dds):
        for dt, dd in zip(dts, dds):
            label = dt.get_text(strip=True)
            value_text = dd.get_text(strip=True)  # Keep original text
            stats_data.append({"label": label, "value": value_text})
        return stats_data

    # If not <dl>, try generic div/span pairs
    rows = container.find_all("div") if container else []
    for row in rows:
        spans = row.find_all("span")
        if len(spans) >= 2:
            label = spans[0].get_text(strip=True)
            value_text = spans[1].get_text(strip=True)  # Keep original text
            stats_data.append({"label": label, "value": value_text})

    # If still empty, try broader search near heading
    if not stats_data:
        # Look for any text containing common stat labels
        possible_labels = ["Last Value", "Latest Period", "Last Updated", "Next Release", "Long Term Average", "Average Growth Rate", "Value from Last Week", "Change from Last Week", "Value from 1 Year Ago", "Change from 1 Year Ago", "Frequency"]
        
        for label_text in possible_labels:
            elem = soup.find(string=lambda text: text and label_text in text)
            if elem:
                parent = elem.parent
                # Look for the next element that contains either a percentage OR looks like a date
                # Find the next sibling that has text content
                next_elem = parent.find_next(string=True)
                if next_elem:
                    # Navigate up to the parent element and get all text siblings
                    current_elem = parent.next_sibling
                    while current_elem:
                        if hasattr(current_elem, 'get_text'):
                            value_text = current_elem.get_text(strip=True)
                            if value_text and (('%' in value_text) or 
                                             any(month in value_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or
                                             value_text.replace('.', '').replace(',', '').replace(' ', '').isdigit()):
                                stats_data.append({"label": label_text, "value": value_text})
                                break
                        elif hasattr(current_elem, 'string') and current_elem.string:
                            value_text = current_elem.string.strip()
                            if value_text and (('%' in value_text) or 
                                             any(month in value_text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or
                                             value_text.replace('.', '').replace(',', '').replace(' ', '').isdigit()):
                                stats_data.append({"label": label_text, "value": value_text})
                                break
                        current_elem = current_elem.next_sibling

    return stats_data

@app.route('/us-rate-stats', methods=['GET'])
def us_prime_rate_stats():
    try:
        data = get_us_prime_rate_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## USA PRIME RATE AND DATE
def get_us_prime_rate_history():
    url = "https://ycharts.com/indicators/us_bank_prime_loan_rate"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table", class_="table")
    
    all_data = []
    for table in tables:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                date_text = cols[0].get_text(strip=True)
                rate_text = cols[1].get_text(strip=True).replace("%", "")
                
                # Skip rows that don't look like real dates
                if not any(month in date_text for month in [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]):
                    continue

                # Try to convert date to yyyy-mm-dd
                try:
                    parsed_date = datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    continue  # skip rows that aren't valid dates

                try:
                    rate = float(rate_text)
                except ValueError:
                    continue

                all_data.append({
                    "date": parsed_date,
                    "prime_rate": rate
                })
    
    return all_data

@app.route('/us-prime-rate', methods=['GET'])
def us_prime_rate():
    try:
        data = get_us_prime_rate_history()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/prime-rates', methods=['GET'])
def prime_rates():
    data = {
        "Canada": {
            "prime_rate": g_et_canada_prime_rate_history(),
            "last_updated": str(date.today())
        },
        "US": {
            "prime_rate": get_us_prime_rate_history(),
            "last_updated": str(date.today())
        }
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True) 