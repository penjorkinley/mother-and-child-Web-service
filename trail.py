import requests
def healthapi():
    
    url = ('https://newsapi.org/v2/top-headlines?'
        'country=us&'
        'category=health&'
        'apiKey=fd043899448f4e429d3d038a4cbd9829')
    response = requests.get(url)
    print (response.json()['articles'][1]['title']) 

healthapi()