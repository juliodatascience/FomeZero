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


st.set_page_config(page_title='Cities', page_icon = "🏙️",layout="wide", initial_sidebar_state="expanded")

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
df1['aggregate_rating'] = df1['aggregate_rating'].astype(float)
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
# Layout no StreamLit - FomeZero Cidades
#===============================================================
st.title('🏙️Visão Cidades')

with st.container():
    st.markdown('##### Top 10 Cidades com mais Restaurantes na Base de Dados')
    columns = ['restaurant_id','city', 'restaurant_name',]

    # Group the DataFrame by cities and restaurant_name to get the count of restaurants per city
    grouped_cities = df1.loc[:,['city', 'restaurant_name']].groupby('city').count().sort_values(by='restaurant_name',ascending =False).reset_index().head(10)
    
    fig = px.bar(data_frame = grouped_cities, x=grouped_cities['city'], y = grouped_cities['restaurant_name'])
    fig.update_layout(xaxis_title='Cidade', yaxis_title='Quantidade de Restaurantes')
    st.plotly_chart(fig,use_container_width=True)
    
    col1,col2 = st.columns(2)
    
    with col1:
        st.markdown('##### 7 Cidades com Restaurantes com média de avaliação maior ou igual a 4')
        columns = ['restaurant_id','aggregate_rating']

        condicao= (df1['aggregate_rating']>=4.0)
        grouped_count_cities = df1.loc[condicao,['city', 'restaurant_id']].groupby('city').count().sort_values(by='restaurant_id',ascending =False).reset_index().head(7)
        fig = px.bar(data_frame = grouped_count_cities, x=grouped_count_cities['city'], y = grouped_count_cities['restaurant_id'])
        fig.update_layout(xaxis_title='Cidade', yaxis_title='Quantidade de Restaurantes')
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        st.markdown('##### Cidades com Restaurantes com média de avaliação abaixo de 2.5')
        columns = ['restaurant_id','aggregate_rating']

        condicao= (df1['aggregate_rating']<=2.5)
        grouped_count_cities = df1.loc[condicao,['city', 'restaurant_id']].groupby('city').count().sort_values(by='restaurant_id',ascending =False).reset_index().head(7)
        fig = px.bar(data_frame = grouped_count_cities, x=grouped_count_cities['city'], y = grouped_count_cities['restaurant_id'])
        fig.update_layout(xaxis_title='Cidade', yaxis_title='Quantidade de Restaurantes')
        st.plotly_chart(fig,use_container_width=True)
            
    
    st.markdown('##### Top 10 Cidades com mais restaurantes com tipos culinários distintos')
    columns = ['country_name','city', 'cuisines']
    df_city_cuisines = df1.loc[:,columns].groupby(['country_name','city']).nunique().sort_values(by=['cuisines'], ascending=False).reset_index().head(10)
    fig = px.bar(data_frame = df_city_cuisines, x='city', y = 'cuisines', color = 'country_name')
    fig.update_layout(xaxis_title='Cidades', yaxis_title='Quantidade de Tipos de Culinárias Únicos')
    st.plotly_chart(fig,use_container_width=True)