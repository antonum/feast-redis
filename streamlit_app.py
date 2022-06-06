import datetime
from collections import OrderedDict
from PIL import Image

import pandas as pd
import shap
import streamlit as st
from matplotlib import pyplot as plt

from credit_model import CreditScoringModel

st.set_page_config(layout="wide")
model = CreditScoringModel(st.secrets.get("redis_connection_string"))
if not model.is_model_trained():
    raise Exception("The credit scoring model has not been trained. Please run run.py.")


def get_loan_request():
    zipcode = st.sidebar.text_input("Zip code", "94109")
    date_of_birth = st.sidebar.date_input(
        "Date of birth", value=datetime.date(year=1986, day=19, month=3)
    )
    ssn_last_four = st.sidebar.text_input(
        "Last four digits of social security number", "3643"
    )
    dob_ssn = f"{date_of_birth.strftime('%Y%m%d')}_{str(ssn_last_four)}"
    age = st.sidebar.slider("Age", 0, 130, 25)
    income = st.sidebar.slider("Yearly Income", 0, 300000, 12000)
    person_home_ownership = st.sidebar.selectbox(
        "Do you own or rent your home?", ("RENT", "MORTGAGE", "OWN")
    )

    employment = st.sidebar.slider(
        "How long have you been employed (months)?", 0, 120, 12
    )

    loan_intent = st.sidebar.selectbox(
        "Why do you want to apply for a loan?",
        (
            "PERSONAL",
            "VENTURE",
            "HOMEIMPROVEMENT",
            "EDUCATION",
            "MEDICAL",
            "DEBTCONSOLIDATION",
        ),
    )

    amount = st.sidebar.slider("Loan amount", 0, 100000, 10000)
    interest = st.sidebar.slider("Preferred interest rate", 1.0, 25.0, 12.0, step=0.1)
    return OrderedDict(
        {
            "zipcode": [int(zipcode)],
            "dob_ssn": [dob_ssn],
            "person_age": [age],
            "person_income": [income],
            "person_home_ownership": [person_home_ownership],
            "person_emp_length": [float(employment)],
            "loan_intent": [loan_intent],
            "loan_amnt": [amount],
            "loan_int_rate": [interest],
        }
    )


# Application
st.title("Loan Application")
#st.write(st.secrets.get("redis_connection_string"))
#st.write(st.secrets.get("redis_connection_string11"))

# Input Side Bar
st.header("User input:")
loan_request = get_loan_request()
df = pd.DataFrame.from_dict(loan_request)
df

# Full feature vector
st.header("Feature vector (user input + zipcode features + user features):")
vector = model._get_online_features_from_feast(loan_request)
ordered_vector = loan_request.copy()
key_list = vector.keys()
key_list = sorted(key_list)
for vector_key in key_list:
    if vector_key not in ordered_vector:
        ordered_vector[vector_key] = vector[vector_key]
df = pd.DataFrame.from_dict(ordered_vector)
df

# Results of prediction
st.header("Application Status (model prediction):")
result = model.predict(loan_request)

if result == 0:
    st.success("Your loan has been approved!")
elif result == 1:
    st.error("Your loan has been rejected!")


# Feature importance
st.header("Feature Importance")

#@st.cache
def cache_func():
    X = pd.read_parquet("creditscore/data/training_dataset_sample.parquet")
    explainer = shap.TreeExplainer(model.classifier)
    return explainer.shap_values(X), X

shap_values, X = cache_func()
left, mid, right = st.columns(3)
with left:
    plt.title("Feature importance based on SHAP values")
    shap.summary_plot(shap_values[1], X)
    st.set_option("deprecation.showPyplotGlobalUse", False)
    st.pyplot(bbox_inches="tight")
    st.write("---")

with mid:
    plt.title("Feature importance based on SHAP values (Bar)")
    shap.summary_plot(shap_values, X, plot_type="bar")
    st.pyplot(bbox_inches="tight")

st.header("Feast Configuration")
left, mid, right = st.columns(3)
with left:
    st.write("feature_store.yaml")
    code = '''project: creditscore
    registry: data/registry.db
    provider: local
    online_store:
        type: redis
        connection_string: yyy.cloud.redislabs.com:14783,password=xxx'''
    st.code(code, language='yaml')

    st.markdown("Create your own free Redis DB at [Redis Cloud](https://app.redislabs.com/#/login)")
with mid:
    image = Image.open('diagram.png')
    st.image(image, caption='Solution diagram')

