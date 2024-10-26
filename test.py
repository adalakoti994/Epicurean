import os
import requests
import ssl
import logging
import pandas as pd
import kagglehub
from dotenv import load_dotenv
import streamlit as st

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# Ensure TLS 1.2
ssl._create_default_https_context = ssl._create_unverified_context

def load_recipes_data():
    dataset_path = kagglehub.dataset_download("thedevastator/better-recipes-for-a-better-life")
    logging.info("Dataset downloaded at: %s", dataset_path)
    
    # Load the dataset
    recipes_df = pd.read_csv(os.path.join(dataset_path, "recipes.csv"))
    return recipes_df

class RecipeAgent:
    def __init__(self, api_key, recipes_df):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.recipes_df = recipes_df

    def get_recipe(self, item_name):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        relevant_recipe = self.recipes_df[self.recipes_df['recipe_name'].str.lower() == item_name.lower()]
        
        if relevant_recipe.empty:
            return None

        recipe_details = relevant_recipe.to_dict(orient='records')[0]
        messages = [{"role": "user", "content": f"Provide cooking instructions for this recipe: {recipe_details}."}]
        
        response_data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=response_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching recipe: {e}")
            return None

class SeasonalRecipeAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def get_seasonal_recipes(self, item_name, location):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "user", "content": f"Suggest seasonal recipes for {item_name} in {location}."}]
        response_data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=response_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching seasonal recipes: {e}")
            return None

# Streamlit app execution
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error("API key not found. Please set it in the .env file.")
        st.stop()

    recipes_data = load_recipes_data()
    
    st.title("EpicureanAI")

    item_name = st.text_input("Enter Item Name:")
    recipe_type = st.selectbox("Choose Recipe Type:", ("Specific Recipe", "Seasonal Recipe"))
    location = st.text_input("Enter Location (for seasonal recipes):")

    if st.button("Get Recipe"):
        if recipe_type == "Specific Recipe":
            recipe_agent = RecipeAgent(api_key, recipes_data)
            recipe_response = recipe_agent.get_recipe(item_name)

            if recipe_response:
                content = recipe_response.get('choices', [{}])[0].get('message', {}).get('content', '')
                st.write(content)  # Display only the content
            else:
                st.error(f"No recipe found for '{item_name}'.")

        elif recipe_type == "Seasonal Recipe":
            seasonal_agent = SeasonalRecipeAgent(api_key)
            seasonal_response = seasonal_agent.get_seasonal_recipes(item_name, location)

            if seasonal_response:
                content = seasonal_response.get('choices', [{}])[0].get('message', {}).get('content', '')
                st.write(content)  # Display only the content
            else:
                st.error(f"Error retrieving seasonal recipes for '{item_name}'.")
