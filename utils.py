import pandas as pd
import streamlit as st

def redemption_history_to_df(redemption_history):
    return pd.DataFrame(redemption_history) 


@st.cache_data
def get_image_by_path(path, _db):
    image = _db.download_file(path)
    return image

def get_image_by_path_no_cache(path, _db):
    return get_image_by_path(path, _db)
