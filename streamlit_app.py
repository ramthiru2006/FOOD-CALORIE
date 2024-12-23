import os
import tempfile
import streamlit as st
import pandas as pd
from PIL import Image, UnidentifiedImageError
import roboflow

# Apply custom styles with orange highlights
def apply_custom_styles():
    st.markdown(
        """
        <style>
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF5733; /* Orange color */
            text-align: center;
            margin-bottom: 20px;
        }
        .form-header {
            font-size: 1.5rem;
            color: #FF5733;
            margin-bottom: 10px;
        }
        .stButton > button {
            background-color: #FF5733;
            color: white; /* Ensures text remains visible */
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s, color 0.3s; /* Smooth transitions */
        }
        .stButton > button:hover {
            background-color: #E94E1B; /* Darker orange */
            color: white; /* Keeps text visible */
        }
        .stFileUploader label {
            color: #FF5733 !important;
        }
        .stMarkdown h3 {
            color: #FF5733;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Registration page
def registration_page():
    st.markdown('<div class="title">🍎 Register</div>', unsafe_allow_html=True)
    with st.form("Registration Form"):
        st.markdown('<div class="form-header">Enter your details below:</div>', unsafe_allow_html=True)
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        height = st.number_input("Height (in cm)", min_value=0)
        weight = st.number_input("Weight (in kg)", min_value=0)
        gender = st.radio("Gender", ["Male", "Female"])
        health_conditions = st.text_area("Health Conditions (if any)")
        submitted = st.form_submit_button("Register")
        if submitted:
            st.session_state['registered'] = True
            st.session_state.update({
                "name": name,
                "age": age,
                "height": height,
                "weight": weight,
                "gender": gender,
            })
            st.success(f"Registration complete! Welcome, {name}.")
    if st.button("Already Registered? Login"):
        st.session_state['registered'] = True

def detect_calories(image_path):
    """Detects food items and calculates total calories with nutrition breakdown."""
    
    # Initialize the Roboflow model
    rf = roboflow.Roboflow(api_key="apCOovyZR2H1HTkJd4fK")
    project = rf.workspace().project("calorie-detector-2")
    model = project.version("1").model

    model.confidence = 50  # Confidence threshold
    model.overlap = 25     # Overlap threshold
    calorie_mapping = {
        "Bhatura": {"calories": 321, "protein": 7, "carbs": 49, "fat": 11},
        "BhindiMasala": {"calories": 314, "protein": 5, "carbs": 19, "fat": 25},
        "Biryani": {"calories": 490, "protein": 16, "carbs": 72, "fat": 12},
        "Chole": {"calories": 323, "protein": 10, "carbs": 44, "fat": 12},
        "ShahiPaneer": {"calories": 967, "protein": 25, "carbs": 40, "fat": 80},
        "chicken": {"calories": 278, "protein": 25, "carbs": 0, "fat": 20},
        "dal": {"calories": 593, "protein": 25, "carbs": 50, "fat": 18},
        "dhokla": {"calories": 359, "protein": 10, "carbs": 50, "fat": 12},
        "gulab_jamun": {"calories": 150, "protein": 5, "carbs": 80, "fat": 20},
        "idli": {"calories": 81, "protein": 2, "carbs": 15, "fat": 1},
        "jalebi": {"calories": 542, "protein": 2, "carbs": 90, "fat": 20},
        "modak": {"calories": 280, "protein": 4, "carbs": 50, "fat": 8},
        "palak_paneer": {"calories": 327, "protein": 12, "carbs": 18, "fat": 22},
        "poha": {"calories": 721, "protein": 12, "carbs": 88, "fat": 30},
        "rice": {"calories": 270, "protein": 4, "carbs": 60, "fat": 1},
        "roti": {"calories": 327, "protein": 10, "carbs": 58, "fat": 6},
        "samosa": {"calories": 350, "protein": 5, "carbs": 40, "fat": 20},
    }

    # Use the file path for prediction
    prediction = model.predict(image_path)
    prediction_data = prediction.json()

    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    detected_items = []

    for pred in prediction_data["predictions"]:
        food_name = pred.get("class", "Unknown")
        confidence = pred.get("confidence", 0) * 100  # Convert to percentage
        tag_count = pred.get("tags", 1)  # Assuming "tags" represent the tag count

        # Fetch nutritional info
        food_info = calorie_mapping.get(food_name, {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
        calories = tag_count * food_info["calories"]
        protein = tag_count * food_info["protein"]
        carbs = tag_count * food_info["carbs"]
        fat = tag_count * food_info["fat"]

        # Update totals
        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fat += fat

        detected_items.append({
            "Food Item": food_name,
            "Confidence (%)": f"{confidence:.2f}",
            "Tags": tag_count,
            "Calories": calories,
            "Protein (g)": protein,
            "Carbohydrates (g)": carbs,
            "Fat (g)": fat,
        })

    return detected_items, total_calories, total_protein, total_carbs, total_fat

def food_suggestions(calories_needed):
    """Suggest food items to meet the remaining calorie intake."""
    food_items = {
        "Salad": 150,
        "Apple": 95,
        "Banana": 105,
        "Boiled Eggs": 78,
        "Almonds (10 pieces)": 70,
        "Yogurt (1 cup)": 150,
        "Chicken Breast (100g)": 165,
        "Rice (1 cup)": 200,
        "Oatmeal (1 bowl)": 150,
        "Avocado": 160,
        "Cottage Cheese (100g)": 98,
    }

    suggestions = []
    total_calories = 0
    for food, calories in food_items.items():
        if total_calories < calories_needed:
            suggestions.append(f"{food}: {calories} calories")
            total_calories += calories

    return suggestions

def main():
    apply_custom_styles()

    if 'registered' not in st.session_state:
        registration_page()
        return

    st.markdown('<div class="title">🍔 Calorie Detection & Suggestions</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload an image of food", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name

            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            st.write("Detecting calories...")

            detected_items, total_calories, total_protein, total_carbs, total_fat = detect_calories(tmp_file_path)

            st.markdown("### Detected Food Items")
            st.write(pd.DataFrame(detected_items))
            st.markdown(f"### Total Calories: {total_calories}")
            st.markdown(f"### Total Protein: {total_protein}g")
            st.markdown(f"### Total Carbohydrates: {total_carbs}g")
            st.markdown(f"### Total Fat: {total_fat}g")

            # Calculate remaining calories to meet 2000-calorie target
            daily_calories = 2000
            remaining_calories = daily_calories - total_calories

            st.markdown(f"### Remaining Calories to Reach 2000: {remaining_calories} calories")

            # Suggest foods to meet remaining calories
            suggestions = food_suggestions(remaining_calories)
            st.markdown("### Food Suggestions to Meet Your Calorie Goal:")
            for suggestion in suggestions:
                st.write(suggestion)

        except UnidentifiedImageError:
            st.error("The uploaded file is not a valid image.")
    else:
        st.write("Please upload an image to detect calories.")

if __name__ == "__main__":
    main()
