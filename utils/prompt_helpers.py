from utils import acordao_example


summary_prompt_string = """Escreva um resumo estruturado do acórdão a seguir com a seguinte estrutura:
    **Ementa Resumida:**
    <Resumo da ementa do acórdão>
    **Decisão Resumida:**
    <Resumo da decisão do acórdão>"""

classification_prompt_string = """Classifique o acórdão de acordo com as seguintes categorias:
    - Categoria (list[str]): administrativo; cível; penal; trabalhista; tributário; outro.
    - Decisão (str): favorável, desfavorável ou neutro.

Classifique as propriedades mencionadas baseando-se apenas nas informações do acórdão.
"""

extraction_prompt_string = "Você é especializado localizar e extrair entidades em acórdãos. " \
    "Não forneça explicações adicionais ou informações não solicitadas. " \
    "Se não conseguir identificar algum dos campos, deixe em branco. " \
    """Em um acordão, você deve encontrar os seguintes campos:
    - Descrição da classe do processo (e,g., Recurso Especial, Agravo de Instrumento)
    - Número do processo
    - Entidade julgadora (e.g., Primeira Turma, Segunda Turma, Camara Criminal, etc.)
    - Nome do relator
    - Lista dos nome e cargos/funções das pessoas citadas
    - Data da decisão (formato DD/MM/YYYY)
    - Data da publicação (formato DD/MM/YYYY)
    - Lista dos fundamentos jurídicos (i.e, artigos, leis, súmulas citadas)"""


def summary_chat_messages(text):
    return [
        ("system", summary_prompt_string),
        ("user", text),
    ]


def extraction_chat_messages(text):
    return [
        ("system", extraction_prompt_string),
        ("user", acordao_example.maria_da_penha),
        ("assistant", """{{
    "descricao_classe_processo":"HABEAS CORPUS",
    "numero_processo":"0800888-20.2015.8.15.0000",
    "entidade_julgadora":"Câmara Criminal",
    "relator":"Des. Joás de Brito Pereira Filho",
    "pessoas_citadas":[
        "Persons(nome='Mario Felix de Menezes', cargo='Impetrante/Advogado')",
        "Persons(nome='Alexsandro Barbosa Guedes', cargo='Paciente')",
        "Persons(nome='JUIZ DE DIREITO', cargo='Autoridade coatora')"
    ],
    "data_publicacao": None,
    "data_decisao":"31/07/2015",
    "fundamentos_juridicos":[
        "Lei nº 11.340/06",
        "artigos relacionados à Lei Maria da Penha",
        "Precedentes do STJ: HC n. 126.912/SP, Ministra Maria Thereza de Assis Moura, Dje 12/4/2010"
    ]
}}"""),
        ("user", text)
    ]


def classification_chat_messages(text):
    return [
        ("system", classification_prompt_string),
        ("user", text),
    ]


def human_input_chat_messages(text):
    return [("system", f"Você é um assistente jurídico. "
             f"Responda às perguntas com base apenas no seguinte acórdão:\n\n{text}")]
