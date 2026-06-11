import os
import tempfile
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

import base64
from PIL import Image

# Obter o diretório do script
base_dir = os.path.dirname(os.path.abspath(__file__))


# Configurações iniciais
st.set_page_config(layout="wide")
plt.style.use('ggplot')
sns.set_palette("husl")


# Título do aplicativo com logomarca
col1, col2 = st.columns([1, 3])  # Ajuste as proporções conforme necessário

with col1:
    # Carrega e exibe a imagem da logo
    logo_path = os.path.join(base_dir, "Brasao.PNG")
    logo = Image.open(logo_path)  # Substitua pelo caminho da sua imagem
    st.image(logo, width=400)  # Ajuste a largura conforme necessário

with col2:
    st.title("Análise Exploratória da Educação Especial no ES")


# Carregar os dados
@st.cache_data
def load_data():
    csv_path = os.path.join(base_dir, 'painel_AEE.parquet')
    df = pd.read_parquet(csv_path)
    # Converter ano para string para facilitar filtros
    df['NU_ANO_CENSO'] = df['NU_ANO_CENSO'].astype(str)
    return df

df = load_data()

# Sidebar com filtros
st.sidebar.header("Filtros")


# Filtro de ano - lista suspensa com opção "Todas"
anos = sorted(df['NU_ANO_CENSO'].unique())
opcoes_anos = ['Todos'] + anos

selected_anos = st.sidebar.selectbox(
    'Selecione o(s) ano(s)',
    options=opcoes_anos,
    index=0  # "Todas" selecionado por padrão
)

# Converte a seleção para o formato de lista esperado pelas etapas seguintes
if selected_anos == 'Todos':
    selected_anos = anos
else:
    selected_anos = [selected_anos]


# Filtro de dependência administrativa - lista suspensa com opção "Todas"
dependencias = sorted(df['DC_DEPENDENCIA'].unique())
opcoes_dependencias = ['Todas'] + dependencias

selected_dependencia = st.sidebar.selectbox(
    'Selecione a dependência administrativa',
    options=opcoes_dependencias,
    index=0  # "Todas" selecionado por padrão
)

# Converte a seleção para o formato de lista esperado pelas etapas seguintes
if selected_dependencia == 'Todas':
    selected_dependencias = dependencias
else:
    selected_dependencias = [selected_dependencia]



# Filtro de Atendimento - lista suspensa com opção "Todos"
atendimento = sorted(df['Aluno_AEE'].unique())
opcoes_atendimento = ['Todos'] + atendimento

selected_atendimento = st.sidebar.selectbox(
    'Selecione o(s) Alunos em Atendimento Especializado',
    options=opcoes_atendimento,
    index=0  # "Todas" selecionado por padrão
)

# Converte a seleção para o formato de lista esperado pelas etapas seguintes
if selected_atendimento == 'Todos':
    selected_atendimento = atendimento
else:
    selected_atendimento = [selected_atendimento]


# Filtro de modalidade - lista suspensa com opção "Todas"
modalidades = sorted(df['Modalidade'].unique())
opcoes_modalidades = ['Todas'] + modalidades

selected_modalidades = st.sidebar.selectbox(
    'Selecione a(s) modalidade(s) de ensino',
    options=opcoes_modalidades,
    index=0  # "Todas" selecionado por padrão
)

# Converte a seleção para o formato de lista esperado pelas etapas seguintes
if selected_modalidades == 'Todas':
    selected_modalidades = modalidades
else:
    selected_modalidades = [selected_modalidades]



# Aplicar filtros (.copy() evita SettingWithCopyWarning ao criar colunas depois)
filtered_df = df[
    (df['NU_ANO_CENSO'].isin(selected_anos)) &
    (df['DC_DEPENDENCIA'].isin(selected_dependencias)) &
    (df['Aluno_AEE'].isin(selected_atendimento)) &
    (df['Modalidade'].isin(selected_modalidades))
].copy()

# Mostrar quantidade de registros filtrados
st.sidebar.markdown(f"**Registros encontrados:** {len(filtered_df):,}")

# Seção de análise por tipo de aluno
st.header("Alunos público Alvo da Educação Especial em AEE")
col1, col2 = st.columns(2)

# Widgets de seleção de cores (sidebar)
st.sidebar.subheader("Configurações de Cores")
with st.sidebar.expander("Cores para Gráfico de Pizza 🎨"):
    cor_sim = st.color_picker('Cor para "Sim" (Pizza)', '#1f77b4')
    cor_nao = st.color_picker('Cor para "Não" (Pizza)', '#ff7f0e')

with st.sidebar.expander("Cores para Gráfico de Barras 🎨"):
    cor_barra_sim = st.color_picker('Cor para "Sim" (Barras)', '#1f77b4')
    cor_barra_nao = st.color_picker('Cor para "Não" (Barras)', '#ff7f0e')

col1, col2 = st.columns(2)

with col1:
    # Gráfico de Pizza com cores personalizadas
    fig, ax = plt.subplots(figsize=(8, 6))
    counts = filtered_df['Aluno_AEE'].value_counts()
    cores_pizza = [cor_sim if "Sim" in str(index) else cor_nao for index in counts.index]

    counts.plot(
        kind='pie',
        autopct='%1.1f%%',
        ax=ax,
        colors=cores_pizza,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    ax.set_ylabel('')
    st.pyplot(fig)

with col2:
    # Gráfico de Barras com cores personalizadas
    fig, ax = plt.subplots(figsize=(8, 6))
    paleta = {"Sim": cor_barra_sim, "Não": cor_barra_nao}

    plot = sns.countplot(
        data=filtered_df,
        x='NU_ANO_CENSO',
        hue='Aluno_AEE',
        ax=ax,
        palette=paleta,
        edgecolor='w',
        linewidth=0.5
    )

    # Adicionar os valores nas barras
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(
                f'{int(height)}',
                (p.get_x() + p.get_width() / 2., height),
                ha='center',
                va='center',
                xytext=(0, 5),
                textcoords='offset points',
                fontsize=8
            )

    ax.set_title('Evolução do  AEE Anualmente')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Contagem')
    ax.legend(title='AEE')
    plt.xticks(rotation=45)
    st.pyplot(fig)




# Seção de análise por sexo
st.header("Distribuição por Sexo")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    filtered_df['DC_SEXO'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax, wedgeprops={'edgecolor': 'w', 'linewidth': 1})
    ax.set_ylabel('')
    ax.set_title('Distribuição por Sexo')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    plot = sns.countplot(data=filtered_df, x='NU_ANO_CENSO', hue='DC_SEXO', ax=ax, edgecolor='w')

    # Adicionar os valores nas barras
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Só adiciona texto se a barra tiver altura > 0
            ax.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 5),
                        textcoords='offset points')

    ax.set_title('Evolução por Sexo e Ano')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Contagem')
    ax.legend(title='Sexo')
    st.pyplot(fig)

# Seção de análise por raça/cor
st.header("Distribuição por Raça/Cor")
col1, col2 = st.columns(2)


with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    filtered_df['DC_COR_RACA'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax, wedgeprops={'edgecolor': 'w', 'linewidth': 1})
    ax.set_ylabel('')
    ax.set_title('Distribuição por Raça/Cor')
    st.pyplot(fig)


with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    plot = sns.countplot(data=filtered_df, x='NU_ANO_CENSO', hue='DC_COR_RACA', ax=ax, edgecolor='w')

    # Adicionar os valores nas barras
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Só adiciona texto se a barra tiver altura > 0
            ax.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 5),
                        textcoords='offset points')


    ax.set_title('Evolução por Raça/Cor e Ano')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Contagem')
    ax.legend(title='Raça/Cor', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

# Seção de análise por Faixa Etária
st.header("Distribuição por Faixa Etária")
col1, col2 = st.columns(2)

# Cria lista ordenada das categorias (mesma ordem para ambos os gráficos)
categorias = filtered_df['Faixa_Etaria'].value_counts().index.tolist()

# Gera paleta de cores única para todas as categorias
n_categorias = len(categorias)
paleta_cores = sns.color_palette("husl", n_categorias)  # Paleta fixa para todas as categorias
mapeamento_cores = dict(zip(categorias, paleta_cores))  # Mapeia categoria -> cor

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    # Aplica cores mapeadas na pizza
    cores_pizza = [mapeamento_cores[cat] for cat in categorias]  # Mesma ordem!
    filtered_df['Faixa_Etaria'].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%',
        ax=ax,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1},
        colors=cores_pizza  # Força as cores na ordem correta
    )
    ax.set_ylabel('')
    ax.set_title('Distribuição por Faixa Etária')
    st.pyplot(fig)



with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    # Usa o mapeamento de cores e ordem definidos
    plot = sns.countplot(
        data=filtered_df,
        x='NU_ANO_CENSO',
        hue='Faixa_Etaria',
        ax=ax,
        edgecolor='w',
        palette=mapeamento_cores,  # Mesmo mapeamento
        hue_order=categorias  # Mesma ordem da pizza
    )

    # Adicionar os valores nas barras (código existente)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(
                f'{int(height)}',
                (p.get_x() + p.get_width() / 2., height),
                ha='center', va='center',
                xytext=(0, 5),
                textcoords='offset points'
            )

    ax.set_title('Evolução por Faixa Etária e Ano')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Contagem')
    ax.legend(title='Faixa Etária', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)




# Seção de análise por município
st.header("Distribuição por Município")

# Mostrar os top 10 municípios
top_municipios = filtered_df['DC_MUNICIPIO'].value_counts().nlargest(10)

fig, ax = plt.subplots(figsize=(12, 6))
# Gera exatamente o número de cores necessário (husl padrão só dá 6)
bars = ax.barh(
    top_municipios.index,
    top_municipios.values,
    color=sns.color_palette("husl", len(top_municipios))
)

# Adicionar valores com estilo
for bar in bars:
    width = bar.get_width()
    ax.text(width + (0.01 * max(top_municipios.values)),  # Posição X dinâmica
            bar.get_y() + bar.get_height()/2,             # Posição Y centralizada
            f'{width:,}',                                 # Valor formatado
            va='center',
            ha='left',
            fontsize=10,
            fontweight='bold',
            color='dimgrey')

ax.set_title('Top 10 Municípios por Número de Matrículas', pad=20)
ax.set_xlabel('Número de Matrículas')
ax.set_ylabel('Município')
ax.grid(axis='x', linestyle='--', alpha=0.7)

# Remover bordas desnecessárias
sns.despine(left=True)

plt.tight_layout()
st.pyplot(fig)


# Seção de análise por deficiência
st.header("Distribuição por Tipo de Deficiência")

# Processar as deficiências (pode haver múltiplas por aluno)
# .explode() substitui o antigo split(expand=True).stack() e evita FutureWarning
deficiencias = (
    filtered_df['deficiencia']
    .dropna()
    .str.split(',')
    .explode()
    .str.strip()
)
deficiencias = deficiencias[deficiencias != '']
deficiencias_counts = deficiencias.value_counts()

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    deficiencias_counts.plot(kind='bar', ax=ax)

    # Adicionar os valores nas barras (usa ax.patches, não a variável 'plot' antiga)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Só adiciona texto se a barra tiver altura > 0
            ax.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 5),
                        textcoords='offset points')


    ax.set_title('Tipos de Deficiência')
    ax.set_xlabel('Tipo de Deficiência')
    ax.set_ylabel('Contagem')
    plt.xticks(rotation=80)
    st.pyplot(fig)

with col2:
    # Relação entre deficiência e modalidade
    if not filtered_df.empty:
        # Pegar apenas a primeira deficiência listada para simplificar
        filtered_df['deficiencia_primaria'] = filtered_df['deficiencia'].str.split(',').str[0].str.strip()
        cross_tab = pd.crosstab(filtered_df['Modalidade'], filtered_df['deficiencia_primaria'])

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlGnBu', ax=ax)
        ax.set_title('Relação entre Modalidade e Deficiência')
        ax.set_xlabel('Deficiência Primária')
        ax.set_ylabel('Modalidade')
        st.pyplot(fig)

# Mostrar dados brutos
if st.checkbox('Mostrar dados filtrados'):
    st.subheader('Dados Filtrados')
    st.dataframe(filtered_df)
