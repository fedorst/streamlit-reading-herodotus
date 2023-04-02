import streamlit as st
from util import annotation
import html
from htbuilder import H, HtmlElement, styles
import pandas as pd
from st_click_detector import click_detector
import os

st.set_page_config(
    page_title="Reading Herodotus",
    page_icon="🏛️",
    layout="wide",
    # initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://github.com/fedorst/streamlit-playground",
    }
)

if 'book' not in st.session_state:
    st.session_state['book'] = 1

all_books = [p.name.split(".parquet")[0].split("herodotus_book_")[1] for p in os.scandir() if "herodotus_book" in p.name]

@st.cache_data
def get_herodotus_df(book):
    path = f"herodotus_book_{book}.parquet"
    df_book1 = pd.read_parquet(path)
    return df_book1

df_book = get_herodotus_df(st.session_state['book'])

st.title(f"Herodotus book {st.session_state['book']}")
col1, col2 = st.columns([3, 1])

sentence_min, sentence_max = df_book.sentence.min(), df_book.sentence.max()

def reset_token():
    st.session_state['selected_token'] = ''

with col1:
    frontcol, midcol, _ = st.columns([1,1,2])
    with frontcol:
        selected_book = st.selectbox(
            "Select book",
            all_books,
        )
    with midcol:
        selected_sentence = st.number_input(
            f'Select sentence ({sentence_min}-{sentence_max})',
            sentence_min,
            sentence_max,
            on_change=reset_token)

df_sentence = df_book[df_book.sentence == int(selected_sentence)]

if 'selected_token' not in st.session_state:
    st.session_state['selected_token'] = ''


def sentence_to_annot_text(df_sentence):
    annot_elements = []
    for i, row in df_sentence.iterrows():
        annot_elements.append(row.to_dict())
    annot_elements.append(".")
    return annot_elements


def get_html_element(annot_element):
    if isinstance(annot_element, str):
        return html.escape(annot_element)
    elif isinstance(annot_element, dict):
        selected_token = st.session_state["selected_token"]
        idxtoken_selected = selected_token == str(annot_element["idxtoken"])
        govtoken_selected = selected_token == str(annot_element["idxgovernor"])
        return annotation(annot_element,
                          activated=(idxtoken_selected or govtoken_selected),
                          background="blue" if idxtoken_selected else ("green" if govtoken_selected else ""),
                          style={
                              "display": "inline-block",
                              "position": "relative",
                              "text-decoration": "none",
                              "color": "white"
                          },
                          annot_style={
                              "transform": "translateX(-50%)",
                              "position": "absolute",
                              "left": "50%",
                              "bottom": "60%",
                              "font-size": "0.6em",
                              "white-space": "nowrap"
                          })
    else:
        raise Exception("Oh noes!")


@st.cache_data
def construct_annotations(annot_elements):
    new_annots = [get_html_element(a) for a in annot_elements]
    out = H.div()
    for a in new_annots:
        out(a)
    return str(out)


with col1:
    clicked = click_detector(
        construct_annotations(sentence_to_annot_text(df_sentence))
    )

if clicked != "":
    w = str(clicked)
    # print("setting session state to", w)
    st.session_state['selected_token'] = w
    st.experimental_rerun()


w = st.session_state['selected_token']
if w != "":
    row = df_sentence[df_sentence["idxtoken"].astype(str) == str(w)].iloc[0].to_dict()
    #used_cols = ["string", "lemma", "upos", "sentence", "string_beta", "lemma_beta", "definition", "detail", "morph_features", "idxtoken", "idxgovernor"]
    with col2:
        st.markdown(f"**Selected**: {row['string']}")
        st.markdown(f"**Lemma**: {row['lemma']}")
        if row["definition"] is not None:
            st.markdown(f"**Definition**: {', '.join(row['definition'])}")
        if len([v for v in row["morph_features"].values() if v is not None]) > 0:
            st.write({k:v for k,v in row['morph_features'].items() if v is not None})

    #st.dataframe(row[["string", "lemma", "definition", "detail"]].head(1))

    #st.markdown(f"**{clicked} clicked**" if clicked != "" else "**No click**")
