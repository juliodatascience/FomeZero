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

st.set_page_config(page_title='Cuisines', page_icon = "🍽️",layout="wide", initial_sidebar_state="expanded")

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
df2 = df1.copy()
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
    df2 = df2.loc[linhas_selecionadas,:] 
  
    
    cuisines_names = df1['cuisines'].unique()
    cuisines_options = st.sidebar.multiselect(
        'Escolha os tipos de culinária',
        cuisines_names,
        default = ['BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian']
    )
    linhas_selecionadas_cuisines = df1['cuisines'].isin(cuisines_options)
    df1 = df1.loc[linhas_selecionadas_cuisines,:]

    st.sidebar.subheader('Dados Tratados')
    #Create button download
    df1_64_encode = df1.to_csv(index=False).encode('utf-8')
    df1_64_encode = base64.b64encode(df1_64_encode).decode()
    st.sidebar.download_button(label="Download",
        data=df1_64_encode,
        file_name='data.csv',
        mime='text/csv',)
#===============================================================
# Layout no StreamLit - FomeZero Culinárias
#===============================================================
st.title('🍽️Visão Culinárias')

st.markdown('### Melhores Restaurantes dos Principais tipos Culinários')
columns = ['restaurant_id','restaurant_name', 'aggregate_rating', 'cuisines']


df_best_restaurants = df1.loc[:,columns].groupby(['restaurant_id','restaurant_name', 'cuisines']).mean().sort_values(by= ['aggregate_rating', 'restaurant_id'], ascending = [False,True]).reset_index().head(10)
st.table(df_best_restaurants)

st.markdown('### Top 10 Restaurantes')
columns = ['restaurant_id','restaurant_name','country_name','city','cuisines','average_cost_for_two','aggregate_rating','votes']


df_best_restaurants = df1.loc[:,columns].sort_values(by= ['aggregate_rating', 'restaurant_id'], ascending = [False,True]).head(10)
st.table(df_best_restaurants)

col1,col2 = st.columns(2)

with col1:
    st.markdown('### Top 10 Melhores culinárias')
    columns = ['cuisines', 'aggregate_rating']

    df_cuisines = df2.loc[:,columns].groupby('cuisines').mean().sort_values(by='aggregate_rating', ascending = False).reset_index().head(10)
    fig = px.bar(data_frame = df_cuisines, x='cuisines', y = 'aggregate_rating')
    fig.update_layout(xaxis_title='Tipo de culinária', yaxis_title='Média da Avaliação Média')
    st.plotly_chart(fig,use_container_width=True)
with col2:
    st.markdown('### Top 10 Piores culinárias')
    columns = ['cuisines', 'aggregate_rating']

    df_cuisines = df2.loc[:,columns].groupby('cuisines').mean().sort_values(by='aggregate_rating', ascending = True).reset_index().head(10)
    fig = px.bar(data_frame = df_cuisines, x='cuisines', y = 'aggregate_rating')
    fig.update_layout(xaxis_title='Tipo de culinária', yaxis_title='Média da Avaliação Média')
    st.plotly_chart(fig,use_container_width=True)
    
