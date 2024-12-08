import streamlit as st
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
import io

# RDF namespace
EX = "http://example.org/"

# Function to fetch drug data from an API
def fetch_drug_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching drug data: {e}")
        return []

# Function to fetch disease data from an API
def fetch_disease_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching disease data: {e}")
        return []

# Function to fetch target data from an API
def fetch_target_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching target data: {e}")
        return []

# Function to generate RDF graph from fetched data
def generate_rdf_graph(drug_api, disease_api, target_api):
    g = Graph()

    # Fetch data from APIs
    drugs = fetch_drug_data(drug_api)
    diseases = fetch_disease_data(disease_api)
    targets = fetch_target_data(target_api)

    if not drugs or not diseases or not targets:
        st.error("Missing data from one of the APIs. Please check the inputs.")
        return None

    # Create RDF triples for drugs, diseases, and targets
    for drug in drugs:
        drug_uri = URIRef(EX + drug.get("id", "unknown"))
        g.add((drug_uri, RDF.type, URIRef(EX + "Drug")))

        # Link drugs to diseases they treat
        for disease in diseases:
            disease_uri = URIRef(EX + disease.get("id", "unknown"))
            g.add((drug_uri, URIRef(EX + "treats"), disease_uri))

        # Link drugs to targets
        for target in targets:
            target_uri = URIRef(EX + target.get("id", "unknown"))
            g.add((drug_uri, URIRef(EX + "affects"), target_uri))

    return g

# Function to convert RDF graph to downloadable RDF file
def generate_rdf_downloadable(graph):
    rdf_data = graph.serialize(format="turtle")
    return rdf_data

# Streamlit app
st.title("Drug-Disease-Target RDF Generator")

# Get API URLs from user input
st.subheader("Enter API Endpoints")

drug_api_url = st.text_input("Drug API URL (DrugBank)", "")
disease_api_url = st.text_input("Disease API URL (Disease Ontology)", "")
target_api_url = st.text_input("Target API URL (UniProt)", "")

if drug_api_url and disease_api_url and target_api_url:
    # Generate RDF graph
    rdf_graph = generate_rdf_graph(drug_api_url, disease_api_url, target_api_url)
    
    if rdf_graph:
        # Display the RDF graph as text
        st.subheader("Generated RDF Data")
        st.text(rdf_graph.serialize(format="turtle").decode("utf-8"))
        
        # Provide option to download RDF data
        rdf_data = generate_rdf_downloadable(rdf_graph)
        st.download_button(
            label="Download RDF Data",
            data=rdf_data,
            file_name="drug_disease_target.rdf",
            mime="application/rdf+xml"
        )
else:
    st.write("Please provide valid API URLs to generate RDF data.")
