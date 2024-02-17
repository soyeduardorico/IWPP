import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

absFilePath = os.path.dirname(__file__)
rootData = os.path.join(absFilePath,  'data')
mapData = os.path.join(absFilePath,  'map')
NN_path = os.path.join(mapData,  'NN.geojson')
offset_items_path = os.path.join(mapData,  'Offset.xlsx')
development_items_path = os.path.join(mapData,  'Development.xlsx')


# Load data
@st.cache
def load_data():
    data = pd.read_excel(development_items_path)
    return data

data = load_data()

# Streamlit app
st.title('Development Data Analysis')

# Show raw data
if st.checkbox('Show raw data'):
    st.write(data)

# Filtering data
status_to_filter = st.slider('Filter to specific status', 0, data['status'].max(), 1)
filtered_data = data[data['status'] == status_to_filter]
st.write('Filtered Data:', filtered_data)

# Plotting (example: a simple bar chart for existing and proposed population)
if st.checkbox('Show Population Chart'):
    fig, ax = plt.subplots()
    ax.bar(filtered_data.index, filtered_data['existing_population'], label='Existing Population')
    ax.bar(filtered_data.index, filtered_data['proposed_population'], bottom=filtered_data['existing_population'], label='Proposed Population')
    ax.set_ylabel('Population')
    ax.set_title('Population by Area and Status')
    ax.legend()
    st.pyplot(fig)
