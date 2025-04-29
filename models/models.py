from pydantic import BaseModel, Field
from typing import Optional


class Classification(BaseModel):
    """Classificação do acórdão"""
    categoria_do_processo: Optional[list[str]] = Field(
        description="Possíveis categorias: administrativo; cível; penal; trabalhista; tributário; outro"
    )
    decisao: Optional[str] = Field(
        description="Decisão do acórdão (i.e., favorável, desfavorável ou neutro)"
    )


class Persons(BaseModel):
    """Modelo para as pessoas citadas no acórdão"""
    nome: Optional[str] = Field(description="Nome próprio da pessoa")
    cargo: Optional[str] = Field(description="Cargo ou função da pessoa")


class StructuredAcordao(BaseModel):
    """Modelo estruturado para o acórdão"""
    descricao_classe_processo: Optional[str] = Field(
        description="Descrição da classe do processo (e,g., Recurso Especial, Agravo de Instrumento)"
    )
    numero_processo: Optional[str] = Field(description="Número do processo")
    entidade_julgadora: Optional[str] = Field(
        description="Entidade julgadora (e.g., Primeira Turma, Camara Criminal, etc.)"
    )
    relator: Optional[str] = Field(description="Relator")
    pessoas_citadas: Optional[list[Persons]] = Field(description="Nome e cargo/função das pessoas citadas")
    data_publicacao: Optional[str] = Field(description="Data da publicação no formato DD/MM/YYYY")
    data_decisao: Optional[str] = Field(description="Data da decisão no formato DD/MM/YYYY")
    fundamentos_juridicos: Optional[list[str]] = Field(description="Principais fundamentos jurídicos")
