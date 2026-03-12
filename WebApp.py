import os
import io
import pandas as pd
import streamlit as st

from src.retrieval import fetch_openalex_works
from src.cleaning import clean_works_dataframe
from src.keyword_processing import extract_keywords_column
from src.analysis import (
    build_year_count,
    build_cooccurrence_matrix,
    detect_keyword_communities
)
from src.visualization import (
    plot_year_trend,
    plot_wordcloud,
    plot_cooccurrence_network,
    plot_cluster_network
)


st.set_page_config(
    page_title="PyCiteMap",
    page_icon="📚",
    layout="wide"
)


def ensure_dirs():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)


@st.cache_data(show_spinner=False)
def run_pipeline(query: str, max_results: int):
    ensure_dirs()

    raw_df = fetch_openalex_works(query, max_results=max_results)
    clean_df = clean_works_dataframe(raw_df)

    clean_df["keywords_list"] = extract_keywords_column(clean_df)

    year_counts = build_year_count(clean_df)
    G = build_cooccurrence_matrix(clean_df["keywords_list"], min_cooccurrence=2)
    communities = detect_keyword_communities(G)

    return raw_df, clean_df, year_counts, G, communities


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


st.title("📚 PyCiteMap")
st.caption("Automated bibliometric analysis from open scholarly resources")

with st.sidebar:
    st.header("参数设置")
    query = st.text_input(
        "检索关键词",
        value="companion ai elderly care"
    )
    max_results = st.slider(
        "最大检索数量",
        min_value=20,
        max_value=5000,
        value=100,
        step=20
    )
    run_button = st.button("开始分析", use_container_width=True)

st.markdown("### 功能")
st.write("输入关键词后，系统将自动检索文献、清洗数据，并生成发文趋势图、关键词词云图、关键词共现网络和关键词聚类网络。")

if run_button:
    with st.spinner("正在检索与分析，请稍候..."):
        try:
            raw_df, clean_df, year_counts, G, communities = run_pipeline(query, max_results)

            st.success("分析完成！")

            col1, col2, col3 = st.columns(3)
            col1.metric("原始文献数", len(raw_df))
            col2.metric("清洗后文献数", len(clean_df))
            col3.metric("网络节点数", G.number_of_nodes())

            st.markdown("---")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["数据预览", "发文趋势", "关键词词云", "共现网络", "聚类网络"]
            )

            with tab1:
                st.subheader("清洗后数据预览")
                st.dataframe(
                    clean_df[["title", "publication_year", "source", "cited_by_count"]].head(50),
                    use_container_width=True
                )

                st.download_button(
                    label="下载清洗后 CSV",
                    data=dataframe_to_csv_bytes(clean_df),
                    file_name="openalex_clean.csv",
                    mime="text/csv"
                )

            with tab2:
                st.subheader("Publication Trend")
                fig1 = plot_year_trend(year_counts)
                st.pyplot(fig1, use_container_width=True)

            with tab3:
                st.subheader("Keyword Word Cloud")
                fig2 = plot_wordcloud(clean_df["keywords_list"])
                if fig2 is not None:
                    st.pyplot(fig2, use_container_width=True)
                else:
                    st.warning("当前关键词不足，无法生成词云图。")

            with tab4:
                st.subheader("Keyword Co-occurrence Network")
                fig3 = plot_cooccurrence_network(G)
                if fig3 is not None:
                    st.pyplot(fig3, use_container_width=True)
                else:
                    st.warning("当前网络为空，无法生成共现网络图。")

            with tab5:
                st.subheader("Keyword Cluster Network")
                fig4 = plot_cluster_network(G, communities)
                if fig4 is not None:
                    st.pyplot(fig4, use_container_width=True)
                else:
                    st.warning("当前网络为空，无法生成聚类网络图。")

        except Exception as e:
            st.error(f"运行失败：{e}")
else:
    st.info("请在左侧输入关键词并点击“开始分析”。")