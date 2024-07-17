# Gen AI Bootstrap Flask

This repo provides:

1. A basic Flask app with bootstrap-flask for UI and flask-wtf for an input form. PDF parsing is also included via pypdf for this demo case (using langchain's importer).
2. A minimal example of calling an LLM via langchain.
3. A Dockerfile to deploy the app to Cloud Run.

To create a virtual environment, install requirements, and set the needed PROJECT_ID env variable:

```
python3 -m venv .tldr
source .tldr/bin/activate
python3 -m pip install -r requirements.txt
export PROJECT_ID=your-project-id-goes-here
```

To run the app:

```
python3 app.py
```

Then visit the IP address printed to your console: [http://127.0.0.1:8080](http://127.0.0.1:8080)

To deactivate the virtual environment:

```
deactivate
```

The rest of the steps to deploy to Cloud Run and enable IAP are documented in this [deck](https://docs.google.com/presentation/d/1V1MhAxdkU7a2ZhHai1OBJPk9lkIzwerUbEVfCJvv0xg/edit#slide=id.gec1f510b50_0_2272).
