import pandas as pd
import inflection
import streamlit as st
import base64
from PIL import Image
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Countries', page_icon = "🌍",layout="wide", initial_sidebar_state="expanded")

#-----------------------------------Funções------------------------------------------------------#
def rename_columns(dataframe):
  df = dataframe.copy()
  title = lambda x: inflection.titleize(x)
  snakecase = lambda x: inflection.underscore(x)
  spaces = lambda x: x.replace(" ", "")
  cols_old = list(df.columns)
  cols_old = list(map(title, cols_old))
  cols_old = list(map(spaces, cols_old))
  cols_new = list(map(snakecase, cols_old))
  df.columns = cols_new
  return df

def create_price_type(price_range):
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"

def country_name(country_id):
  return COUNTRIES[country_id]


df = pd.read_csv('datasets/zomato.csv')

#Limpeza dos dados
df1 = rename_columns(df)

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
#Retornando o nome dos países de acordo com o código
df1['country_name'] = df1['country_code'].map(country_name)
#Retornando categoria dos preços
df1['category_price'] = df1['price_range'].apply(create_price_type)

#Excluindo NaN
df1= df1.dropna()

#Deixando as culinárias 1 por linha
df1['cuisines'] = df1['cuisines'].astype(str)
df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

condicao = df1['cuisines']=='Drinks Only'
df1 = df1.drop(df1[condicao].index)
condicao2 = df1['cuisines']=='Mineira'
df1 = df1.drop(df1[condicao2].index)

#Remover linhas duplicadas
df1 = df1.drop_duplicates(subset=['restaurant_id'])
#===============================================================
# Barra Lateral
#===============================================================

with st.container():
    

    image_path = 'images/logo.png'
    image = Image.open(image_path)
    
    st.sidebar.image(image,width=30)
    st.sidebar.header('Fome Zero')
        
    countries_names = df1['country_name'].unique()

    st.sidebar.subheader('Filtros')
    countries_options = st.sidebar.multiselect(
        'Escolha os países que Deseja visualizar os Restaurantes',
        countries_names,
        default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
    )
    linhas_selecionadas = df1['country_name'].isin(countries_options)
    df1 = df1.loc[linhas_selecionadas,:]

    st.sidebar.subheader('Dados Tratados')
    #Create button download
    df1_64_encode = df1.to_csv(index=False).encode('utf-8')
    df1_64_encode = base64.b64encode(df1_64_encode).decode()
    st.sidebar.download_button(label="Download",
        data=df1_64_encode,
        file_name='data.csv',
        mime='text/csv',)
#===============================================================
# Layout no StreamLit - FomeZero Países
#===============================================================
st.title('🌍Visão Países')


with st.container():
    st.markdown('##### Quantidades de Restaurantes Registrados por País')
 

    df1_country = (df1.loc[:,['restaurant_id', 'country_name']].groupby('country_name')
                   .count()
                   .sort_values(by='restaurant_id', ascending =False)
                   .reset_index())
    fig = px.bar(data_frame = df1_country, x=df1_country['country_name'], y = df1_country['restaurant_id'])
    fig.update_layout(xaxis_title='Países', yaxis_title='Quantidade de Restaurantes')
    st.plotly_chart(fig,use_container_width=True)
    
    st.markdown('##### Quantidades de Cidades Registrados por País')
    columns = ['city', 'country_name']

    df1_cities = df1.loc[:,columns].groupby('country_name').nunique().sort_values(by='city', ascending = False).reset_index()
    fig_cities = px.bar(data_frame = df1_cities, x=df1_cities['country_name'], y = df1_cities['city'])
    fig_cities.update_layout(xaxis_title='Países', yaxis_title='Quantidade de Cidades')
    st.plotly_chart(fig_cities,use_container_width=True)
    
    col1,col2 = st.columns(2)
    
    with col1:
        st.markdown('###### Média de avaliações feitas por País')
        df1_votes_country = df1.loc[:,['votes', 'country_name']].groupby('country_name').mean().sort_values(by='votes', ascending=False).reset_index()
        fig_votes = px.bar(data_frame = df1_votes_country, x=df1_votes_country['country_name'], y = df1_votes_country['votes'])
        fig_votes.update_layout(xaxis_title='Países', yaxis_title='Quantidade de Avaliações')
        st.plotly_chart(fig_votes,use_container_width=True)
    with col2:
        st.markdown('###### Média de preço de um prato para duas pessoas')
        df1_mean_country = df1.loc[:,['average_cost_for_two', 'country_name']].groupby('country_name').mean().sort_values(by='average_cost_for_two', ascending=False).reset_index()
        fig_mean = px.bar(data_frame=df1_mean_country, x=df1_mean_country['country_name'],y=df1_mean_country['average_cost_for_two'])
        fig_mean.update_layout(xaxis_title='Países', yaxis_title='Preço de prato para duas pessoas')
        st.plotly_chart(fig_mean,use_container_width=True)