import yaml
import pandas as pd
import QueryMonday

class ProcessBoards:
    def __init__(self, yaml_path, column_path, query_path, rules_path):
        """
        Parameters
        ----------
        yaml_path: str
            Filepath to yaml file containing Monday.com API key

        column_path: str
            Filepath to plaintext file containing names of columns (in lowercase)

        query_path: str
            Filepath to plaintext file containing query template

        rules_path: str
            Filepath to yaml file containing keywords used to include/exclude
            a board based on its name.
        """
        with open(yaml_path, 'r') as yaml_file:
            creds = yaml.safe_load(yaml_file)
            self.api_key = creds['apiKey']

        with open(column_path, 'r') as column_file:
            self.columns_list = column_file.read().splitlines()

        with open(query_path, 'r') as query_file:
            self.query_template = query_file.read()

        with open(rules_path, 'r') as rules_file:
            board_rules = yaml.safe_load(rules_file)
            self.include = board_rules['keywords']['include']
            self.exclude = board_rules['keywords']['exclude']

        self.page_num = 1

    def create_base(self, columns):
        '''
        Creates a dictionary with keys for each requested value.

        Parameters
        ----------
        columns : list
            A list containing the names of the columns to extract.

        Returns
        -------
        dict
            An "empty" dictionary with a key for all columns to extract.
        '''
        d = {}

        for i in columns:
            d[i] = None

        return d

    def extract_columns(self, board):
        '''
        Extracts the requested columns from a board and processes them
        into a DataFrame-friendly format.

        Parameters
        ----------
        columns : list
            Names of columns to extract from the board
        board : dict
            Dictionary containing Monday board information

        Returns
        -------
        list
            One dictionary in the list for each deal in that Monday board
        '''
        results = []
        board_name = board['name']

        for item in board['items']:
            deal = self.create_base(self.columns_list)
            deal['source'] = ' '.join(board_name.replace('CRM', '').split())
            deal_name = item['name']
            deal['account name'] = deal_name

            for col in item['column_values']:
                title = col['title'].lower()
                #If title is one of the columns requested, add value to dictionary
                if title in self.columns_list:
                    val = col['text']
                    deal[title] = val

            results.append(deal)

        return results

    def check_rules(self, board_name):
        '''
        Check if the board has deal information by checking board name against
        keywords.

        Parameters
        ----------
        board_name: str
        Name of board

        Returns
        -------
        bool
            True if name of board matches all rules, false if it fails any rule
        '''

        board_rules = []

        # Checking certain keywords are in the board name
        if isinstance(self.include, str):
            board_rules.append(self.include in board_name)
        elif isinstance(self.include, list):
            for kw in self.include:
                board_rules.append(kw in board_name)

        # Checking certain keywords are NOT in the board name
        if isinstance(self.exclude, str):
            board_rules.append(self.exclude not in board_name)
        elif isinstance(self.exclude, list):
            for kw in self.exclude:
                board_rules.append(kw not in board_name)

        return all(board_rules)

    def extract_deals(self):
        """
        Monday.com API doesn't support returning all boards, but does support
        pagination for 25 boards at a time.  This loops through pages until no
        more boards are returned.

        For each board, extracts information for columns specified in the column_file.

        Parameters
        ----------
        board_rules: list
            List of rules to identify boards with deal information based on the
            board's name.

        Returns
        -------
        DataFrame
            Each row corresponds to a single item (deal) from Monday.

        """
        monday = QueryMonday.QueryMonday(self.api_key)
        results = []

        while True:
            query = self.query_template.replace('${page_num}', str(self.page_num))
            query_results = monday.execute_query(query)
            # print(query_results)
            query_results = query_results['data']['boards']

            # Empty results -> all boards have been queried already
            if len(query_results) < 1:
                break

            for board in query_results:
                board_name = board['name'].lower()
                if self.check_rules(board_name):
                    board_results = self.extract_columns(board)
                    results.extend(board_results)

            self.page_num += 1

        return results

    def convert_df(self, results):
        '''
        Converts results from extract_deals method to a pandas DataFrame.  Also,
        adds in a column for the type of seller.

        Parameters
        ----------
        results: list of dict
            Results from extract_deals method

        Returns
        -------
        DataFrame
            Dataframe of the results
        '''
        # Re-order columns to match order in columns_list
        df_boards = pd.DataFrame(results).reindex(self.columns_list + ['type'], axis=1)

        # Coalesce price per seat and trade price into single column, then remove trade price
        df_boards['price per seat'] = df_boards['price per seat'].fillna(df_boards['trade price'])
        df_boards.drop('trade price', axis=1, inplace=True)

        # Add column to differentiate between direct and independent reseller
        df_boards['type'] = 'Independent Reseller'
        df_boards.loc[df_boards['source'].str.startswith('Direct'), 'type'] = 'Direct'

        return df_boards
