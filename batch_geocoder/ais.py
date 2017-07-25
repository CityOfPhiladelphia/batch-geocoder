import requests
from retrying import retry

session = requests.Session()

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def geocode(ais_url, ais_key, query_elements):
    url = ais_url + '/search/' + ' '.join(query_elements)
    if ais_key:
        url += '?gatekeeper=' + ais_key

    response = session.get(url)

    if response.status_code >= 500:
        raise Exception('5xx response')
    elif response.status_code != 200:
        return None

    return response.json()
