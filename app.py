import os
import streamlit as st
import base64
from openai import OpenAI
import openai
#import tensorflow as tf  # si no se usa, puedes comentar para evitar import innecesario
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')

# --- Estilos visuales: fondo naranja y tipografía cursiva legible ---
st.markdown(
    """
    <style>
      /* Importar una tipografía cursiva legible desde Google Fonts */
      @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap');

      /* Fondo general de la app */
      [data-testid="stAppViewContainer"], .stApp, body {
        background-color: #FFA500 !important; /* naranja */
      }

      /* Fondo de la barra lateral (ligeramente distinto para contraste) */
      [data-testid="stSidebar"] > div:first-child {
        background-color: #ff9a1a !important;
      }

      /* Aplicar tipografía cursiva legible a toda la app */
      .stApp, .stApp * {
        font-family: 'Dancing Script', "Segoe Script", "Lucida Handwriting", cursive !important;
        font-style: italic !important;
        color: #111111 !important; /* texto oscuro para legibilidad */
      }

      /* Asegurar títulos y textos principales sean legibles */
      h1, h2, h3, h4, .markdown-text-container {
        color: #111111 !important;
      }

      /* Estilos para botones e inputs */
      .stButton>button, .stTextInput>div>div>input, textarea, .stTextArea>div>div>textarea {
        font-family: inherit !important;
        font-style: italic !important;
        color: #111111 !important;
      }

      /* Mantener el lienzo con fondo blanco para dibujar */
      .stCanvas, canvas {
        background-color: #FFFFFF !important;
      }

      /* Ajustes menores para contraste en el sidebar */
      [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: #111111 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('Tablero Inteligente')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
st.subheader("Dibuja el boceto en el panel  y presiona el botón para analizarla")

# Specify canvas parameters in application
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
#os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from environment
api_key = os.environ.get('OPENAI_API_KEY', '')

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key) if api_key else None

analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Describe in spanish briefly the image")
    
        # Create the payload for the completion request (manteniendo la estructura original)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model="gpt-4o-mini",  # o1-preview ,gpt-4o-mini
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                }
              ],
              max_tokens=500,
            )
            #response.choices[0].message.content
            if response.choices and response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            if Expert == profile_imgenh:
               st.session_state.mi_respuesta = response.choices[0].message.content  # full_response 
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
