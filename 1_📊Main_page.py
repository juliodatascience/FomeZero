import pandas as pd
import inflection
import streamlit as st
import base64
from PIL import Image
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(page_title='Main Page', page_icon = '📊',layout="wide",initial_sidebar_state="collapsed")

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
# Layout no StreamLit - FomeZero
#===============================================================
st.title('Fome Zero!')
st.header('O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.subheader('Temos as seguintes marcas dentro de nossa plataforma')


with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        #st.markdown('##### Restaurantes Cadastrados')
        number_restaurants = df1.loc[:,'restaurant_id'].nunique()
        st.metric(value=number_restaurants, label='Restaurantes Cadastrados')
    with col2:
        #st.markdown('##### Países Cadastrados')
        n_countries = df1.loc[:, 'country_code'].nunique()
        st.metric(value=n_countries, label='Países Cadastrados')
    with col3:
        #st.markdown('##### Cidades Cadastradas')
        n_cities = df1.loc[:, 'city'].nunique()
        st.metric(value=n_cities, label='Cidades Cadastradas')
    with col4:
        #st.markdown('##### Avaliações Feitas na Plataforma')
        sum_votes = df1.loc[:, 'votes'].sum()
        st.metric(value=sum_votes, label='Avaliações Feitas na Plataforma')
    with col5:
        #st.markdown('##### Tipos de culinárias Oferecidas')
        n_cuisines = df1.loc[:,'cuisines'].nunique()
        st.metric(value=n_cuisines, label='Tipos de culinárias Oferecidas')
    
    map = folium.Map()
    
    cluster = MarkerCluster().add_to(map)
    for index,location in df1.iterrows():
      #folium.CircleMarker([location['latitude'], location['longitude']],
                    #popup=location[['city','aggregate_rating']], zoom_start = 11).add_to(cluster)
       folium.Marker([location['latitude'], location['longitude']],
                    popup=location[['city']], zoom_start = 11).add_to(cluster)
       
       

    folium_static(map, width=1024,height=600)
