import requests
import os



# Implemention of FDA Data-base API Class
class DrugAPI:
    
    def __init__(self,drug_name):
        self.drug_name = drug_name

#check If the Drug in the FDA DB
    def check_fda_approval(self,drug_name):
        base_url = 'https://api.fda.gov/drug/'
        endpoint = 'label.json'
        params = {
            'search': f'openfda.brand_name:"{drug_name}"',
            'limit': 1
        }
        url = base_url + endpoint
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                base_url = 'https://api.fda.gov/drug/'
                endpoint = 'label.json'
                params = {'search': f'openfda.brand_name:"{drug_name}"','limit': 1}
                url = base_url + endpoint
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    return f'Error: {response.status_code}'
            else:
                return "Drug not found in FDA database."

# conver results to HTML - used for debugging-
    def convert_to_html(self, data, drug_name):
        # Check if data is a string (indicating an error or not found message)
        if isinstance(data, str):
            html_content = f"<html><head><title>Drug Info</title></head><body><h1>{data}</h1></body></html>"
        else:
            # Start HTML document
            html_content = "<html><head><title>Drug Info</title></head><body>"
            html_content += f"<h1>Information for {drug_name}</h1>"
            html_content += "<table border='1'>"

            # Check if there are results
            if 'results' in data:
                for key, value in data['results'][0].items():
                    html_content += f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"
            else:
                html_content += "<tr><td>No data available for this drug.</td></tr>"

            # End HTML document
            html_content += "</table></body></html>"

        # Saving to an HTML file
        file_path = os.path.join(os.getcwd(), f"{drug_name}_info.html")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML file saved: {file_path}")


