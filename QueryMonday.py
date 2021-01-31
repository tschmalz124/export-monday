import requests

class QueryMonday:
    """
    Class to run queries against Monday.com API
    """

    def __init__(self, apiKey):
        """
        Generate API url and header with API key authorization

        Parameters
        ----------
        apiKey : str
            Monday.com API key
        """
        self.api_url = 'https://api.monday.com/v2'
        self.headers = {'Authorization': apiKey}



    def execute_query(self, query):
        """
        Executes query of Monday data.

        Parameters
        ----------
        query : str
            A GraphQL query

        Returns
        -------
        dict
            Results of query in a json format

        """
        data = {'query': query}
        results = requests.post(url=self.api_url, json=data, headers=self.headers)
        return results.json()
