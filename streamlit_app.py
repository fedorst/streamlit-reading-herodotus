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
st.title("The Histories of Herodotus")

df_paths = pd.read_parquet("nlp_paths.parquet")

#if 'book' not in st.session_state:
#    st.session_state['book'] = df_paths.iloc[0].book
#if 'chapter' not in st.session_state:
#    st.session_state['chapter'] = df_paths.iloc[0].chapter
#if 'section' not in st.session_state:
#    st.session_state['section'] = df_paths.iloc[0].section


@st.cache_data
def get_nlp_df(book, chapter, section):
    path = df_paths[
        (df_paths.book == str(book)) & (df_paths.chapter == str(chapter)) & (df_paths.section == str(section))].iloc[0][
        "path"]
    return pd.read_parquet(path)


eng_df = pd.read_parquet("herodotus_books_eng.parquet")


@st.cache_data
def get_eng_text(book, chapter, section):
    text = eng_df[(eng_df["book"] == book) & (eng_df["chapter"] == chapter) & (eng_df["section"] == section)].text_eng
    return "\n".join(text.tolist())
    # path = df_paths[(df_paths.book == str(book)) & (df_paths.chapter == str(chapter)) & (df_paths.section == str(section))].iloc[0]["path"]
    # return pd.read_parquet(path)


col1, col2 = st.columns([3, 1])


def reset_token():
    st.session_state['selected_token'] = ''


st.session_state["curr_idx"] = None
with col1:
    frontcol, midcol, backcol = st.columns([1, 1, 1])
    with frontcol:
        selected_book = st.selectbox(
            "Book",
            df_paths["book"].unique().tolist(),
            on_change=reset_token
        )
    with midcol:
        selected_chapter = st.selectbox(
            "Chapter",
            df_paths[df_paths["book"] == selected_book]["chapter"].unique().tolist(),
            on_change=reset_token
        )
    with backcol:
        selected_section = st.selectbox(
            "Section",
            df_paths[(df_paths["book"] == selected_book) & (df_paths["chapter"] == selected_chapter)][
                "section"].unique().tolist(),
            on_change=reset_token
        )
    st.session_state["curr_idx"] = [selected_book, selected_chapter, selected_section]

df_grc = get_nlp_df(*st.session_state["curr_idx"])
text_eng = get_eng_text(*st.session_state["curr_idx"])

if 'selected_token' not in st.session_state:
    st.session_state['selected_token'] = ''


def sentence_to_annot_text(df_sentence):
    annot_elements = []
    for i, row in df_sentence.iterrows():
        annot_elements.append(row.to_dict())
    return annot_elements


def get_html_element(annot_element):
    if isinstance(annot_element, str):
        return html.escape(annot_element)
    elif isinstance(annot_element, dict):
        selected_token = st.session_state["selected_token"]
        idxtoken_selected = selected_token == str(annot_element["token_id"])
        govtoken_selected = selected_token == str(annot_element["gov_id"])
        return annotation(annot_element,
                          activated=idxtoken_selected or govtoken_selected,
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
                              "font-size": "0.5em",
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
        construct_annotations(sentence_to_annot_text(df_grc))
    )
    st.markdown(text_eng)

if clicked != "":
    st.session_state['selected_token'] = str(clicked)
    st.experimental_rerun()

w = st.session_state['selected_token']
rows = df_grc[df_grc["token_id"].astype(str) == str(w)]
if len(rows) < 1:
    pass
    #print(w, rows)
else:
    row = rows.iloc[0].to_dict()
    with col2:
        st.markdown(f"**Selected**: {row['string']}")
        st.markdown(f"**Lemma**: {row['lemma']}")
        if row["definition"] is not None:
            st.markdown(f"**Definition**: {', '.join(row['definition'])}")
        if len([v for v in row["morph_features"].values() if v is not None]) > 0:
            st.write({k: v for k, v in row['morph_features'].items() if v is not None})
