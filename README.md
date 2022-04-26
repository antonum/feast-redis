# Feast + Redis demo application

Adaptation of https://github.com/feast-dev/feast-aws-credit-scoring-tutorial using Redis as Online Store and default local files as Offline Store.

## Setup 

Install feast/redis:
```
pip install 'feast[redis]'
```
Init feast repo
```
cd creditscore
feast apply
```
Materialize features to Redis
```
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
feast materialize-incremental $CURRENT_TIME
```
return to the main directory and train the model
```
cd ..
python run.py
```

## Interactive demo
```
streamlit run streamlit_app.py
```

## Redis Connection
In order to store connection string/password in streamlit secrets, this project overrides redis connection string.

To supply your own - add file `.streamlit/secrets.toml` with the following content:
```
redis_connection_string = "yyy.cloud.redislabs.com:14783,password=xxx"
```

For Streamlit Cloud - add the same string to the project secrets.