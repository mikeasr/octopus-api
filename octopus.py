import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta


class OctopusAPI:
    def __init__(self, api_key, mpan, serial_number, energy):
        self.api_key = api_key
        self.mpan = mpan
        self.serial_number = serial_number
        self.energy = energy
        self.base_url = self._make_baseurl()

    def get_consumption(self, group_by=None, start=None, end=None):
        endpoint = "consumption/"
        params = {
            'group_by': group_by,
            'period_from': start,
            'period_to': end
        }

        results = []
        next_url = self.base_url + endpoint

        while next_url:
            try:
                data = self._make_request(next_url, params)
                results.extend(data['results'])
                next_url = data.get('next')
            except Exception as e:
                raise RuntimeError(f"An unexpected error occurred: {e}")

        return results

    def get_yesterday(self, group_by=None):
        yesterday = datetime.now() - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        start = start.strftime("%Y-%m-%dT%H:%MZ")
        end = yesterday.replace(hour=23, minute=59, second=59)
        end = end.strftime("%Y-%m-%dT%H:%MZ")
        print(f"Start: {start}")
        print(f"End: {end}")
        return self.get_consumption(group_by, start)

    def _make_baseurl(self):
        base_url = 'https://api.octopus.energy/v1/'
        energy_type = [
                'electricity-meter-points',
                'gas-meter-points']
        return (f"{base_url}{energy_type[self.energy]}"
                f"/{self.mpan}/meters/{self.serial_number}/")

    def _make_request(self, url, params=None):
        auth = HTTPBasicAuth(self.api_key, None)
        try:
            r = requests.get(url, auth=auth, params=params)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")
