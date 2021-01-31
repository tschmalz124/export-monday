import ProcessBoards
import gspread
import sys

# Paths to necessary files
QUERY_PATH = 'templates/query_template.txt'
COLUMN_PATH = 'templates/columns_to_extract.txt'
RULES_PATH = 'templates/board_rules.yaml'
YAML_PATH = sys.argv[1]
GOOGLE_PATH = sys.argv[2]

# Gather information from Monday.com
pb = ProcessBoards.ProcessBoards(YAML_PATH, COLUMN_PATH, QUERY_PATH, RULES_PATH)
board_results = pb.extract_deals()
df_boards = pb.convert_df(board_results)

gc = gspread.service_account(filename=GOOGLE_PATH)
sh = gc.open_by_key( --Spreadsheet ID--)
worksheet = sh.worksheet('Raw Data (do not delete)')
worksheet.clear()
worksheet.update([df_boards.columns.values.tolist()] + df_boards.values.tolist(), value_input_option='USER_ENTERED')
