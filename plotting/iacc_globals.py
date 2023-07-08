import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from main import preprocess_dataframe

sheets_to_keep = ["ASW", "LEV"]
data_dict = pd.read_excel("./data/data.xlsx", sheet_name=sheets_to_keep)
asw_data = data_dict["ASW"]
lev_data = data_dict["LEV"]

to_numeric = lambda s: f"{0.}"

asw_data = preprocess_dataframe(asw_data, "ASW")
lev_data = preprocess_dataframe(asw_data, "LEV")

print(asw_data.describe())
print(lev_data.describe())
