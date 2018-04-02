import requests
from retrying import retry

session = requests.Session()

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def geocode(ais_url, ais_key, ais_user, query_elements):
    url = ais_url + '/search/' + ' '.join(query_elements)

    params = {}
    if ais_key:
        params['gatekeeper'] = ais_key
    if ais_user:
        params['user'] = ais_user

    response = session.get(url, params=params, timeout=10)

    if response.status_code >= 500:
        raise Exception('5xx response')
    elif response.status_code != 200:
        return None

    return response.json()
