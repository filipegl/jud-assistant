import streamlit as st
from utils.llm_adapter import LLMAdapter
from utils.task_handlers import summarize_acordao, classify_acordao, extract_entities, qa_acordao
from ocr.file_handler import extract_text
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Analisador de Processos Judiciais",
    page_icon=":page_facing_up:",
    layout="wide",
)


llm = LLMAdapter(
    provider="openai",
    model_name="gpt-4.1-nano",
    api_key=os.getenv("OPENAI_API_KEY")
)


summary = st.session_state["summary"] if "summary" in st.session_state else None
categories = st.session_state["categories"] if "categories" in st.session_state else None
entities = st.session_state["entities"] if "entities" in st.session_state else None


@st.cache_data
def cached_extract_text(file_path, **kwargs) -> str:
    return extract_text(file_path, **kwargs)


_, left_col, right_col, _ = st.columns([0.05, 0.6, 0.3, 0.05])  # percentages of the column widths
with left_col:
    st.title("Analisador de Processos Judiciais")

    uploaded_file = st.file_uploader(
        label="Faça upload do arquivo do processo (PDF ou imagem):",
        type=["pdf", "png", "jpg"],
        help="Você pode fazer upload de um arquivo para extração automática do texto.",
    )

    if uploaded_file:
        with st.spinner("Extraindo texto do arquivo. Isto pode levar alguns segundos..."):
            try:
                extracted_text = cached_extract_text(uploaded_file)
                st.session_state["acordao"] = extracted_text

                st.success("Texto extraído com sucesso! Você pode editá-lo abaixo.")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    acordao = st.text_area(
        label="Ou cole o texto do acórdão aqui:",
        value=st.session_state.get("acordao", ""),
        height=300,
        help="Cole o texto completo do acórdão, incluindo ementa, decisão e fundamentos jurídicos.",
    )

    st.session_state["acordao"] = acordao

    if st.button("Gerar Análise", type="primary", use_container_width=True):
        if not acordao.strip():
            st.warning("Por favor, forneça o texto do acórdão antes de continuar.")
        else:
            with st.spinner("Resumindo o acórdão..."):
                summary = summarize_acordao(llm, acordao)
                st.session_state["summary"] = summary
            with st.spinner("Classificando o acórdão..."):
                categories = classify_acordao(llm, acordao)
                st.session_state["categories"] = categories
            with st.spinner("Extraindo entidades..."):
                entities = extract_entities(llm, acordao)
                st.session_state["entities"] = entities

    if summary or categories or entities:
        if st.button("Limpar Tudo", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if summary:
        st.subheader("Resumo do Acórdão")
        st.write(summary)

    if categories:
        st.subheader("Classificação")
        st.pills(
            "Categorias do Processo:",
            options=["penal", "cível", "trabalhista", "tributário", "administrativo", "outro"],
            default=categories.categoria_do_processo,
            selection_mode="multi",
        )
        st.pills(
            "Decisão:",
            options=["favorável", "desfavorável", "neutro"],
            default=categories.decisao,
            selection_mode="single",
        )

    if entities:
        st.subheader("Entidades Relevantes")
        with st.expander("Detalhes do Processo"):
            st.markdown(f"**Classe do Processo:** {entities.descricao_classe_processo}")
            st.markdown(f"**Número do Processo:** {entities.numero_processo}")
            st.markdown(f"**Entidade Julgadora:** {entities.entidade_julgadora}")
            st.markdown(f"**Relator:** {entities.relator}")
            st.markdown(f"**Data de Publicação:** {entities.data_publicacao}")
            st.markdown(f"**Data da Decisão:** {entities.data_decisao}")

        with st.expander("Pessoas Citadas"):
            if entities.pessoas_citadas:
                pessoas_data = [{"Nome": p.nome, "Cargo": p.cargo or "N/A"} for p in entities.pessoas_citadas]
                st.table(pessoas_data)
            else:
                st.write("Nenhuma pessoa citada.")

        with st.expander("Fundamentos Jurídicos"):
            if entities.fundamentos_juridicos:
                st.write("Lista de fundamentos jurídicos citados:")
                for fundamento in entities.fundamentos_juridicos:
                    st.markdown(f"- {fundamento}")
            else:
                st.write("Nenhum fundamento jurídico encontrado.")

with right_col:  # QA human input
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    st.subheader("Perguntas e Respostas")
    st.write("Faça perguntas sobre o acórdão ao lado. O assistente responderá com base no texto do processo.")

    if not acordao:
        st.warning("Cole o texto do acórdão para fazer perguntas.")
        st.session_state["chat_history"] = []
        st.stop()

    messages = st.container(height=300)
    for message in st.session_state["chat_history"]:
        if message[0] == "user":
            messages.chat_message("user").write(message[1])
        elif message[0] == "assistant":
            messages.chat_message("assistant").write(message[1])

    if prompt := st.chat_input("Pergunte sobre o acórdão ao lado"):
        messages.chat_message("user").write(prompt)
        with st.spinner("Processando..."):
            response = qa_acordao(llm, acordao, prompt, st.session_state["chat_history"])

        messages.chat_message("assistant").write(response)

    if st.button("Limpar histórico de perguntas", type="tertiary"):
        st.session_state["chat_history"] = []
        st.rerun()
