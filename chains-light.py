from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_aws import BedrockEmbeddings

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_aws import ChatBedrock

from langchain_neo4j import Neo4jVector

from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from typing import List, Any
from utils import BaseLogger, extract_title_and_question, format_docs
from langchain_google_genai import GoogleGenerativeAIEmbeddings

AWS_MODELS = (
    "ai21.jamba-instruct-v1:0",
    "amazon.titan",
    "anthropic.claude",
    "cohere.command",
    "meta.llama",
    "mistral.mi",
)


def load_embedding_model(embedding_model_name: str, logger=BaseLogger(), config={}):
    if embedding_model_name == "ollama":
        embeddings = OllamaEmbeddings(
            base_url=config["ollama_base_url"], model="llama2"
        )
        dimension = 4096
        logger.info("Embedding: Using Ollama")
    elif embedding_model_name == "openai":
        embeddings = OpenAIEmbeddings()
        dimension = 1536
        logger.info("Embedding: Using OpenAI")
    elif embedding_model_name == "aws":
        embeddings = BedrockEmbeddings()
        dimension = 1536
        logger.info("Embedding: Using AWS")
    elif embedding_model_name == "google-genai-embedding-001":
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        dimension = 768
        logger.info("Embedding: Using Google Generative AI Embeddings")
    else:
        # Default to Ollama instead of HuggingFace for light build
        logger.warning(f"Unknown embedding model '{embedding_model_name}', defaulting to Ollama")
        embeddings = OllamaEmbeddings(
            base_url=config["ollama_base_url"], model="llama2"
        )
        dimension = 4096
        logger.info("Embedding: Using Ollama (default)")
    return embeddings, dimension


def load_llm(llm_name: str, logger=BaseLogger(), config={}):
    if llm_name in ["gpt-4", "gpt-4o", "gpt-4-turbo"]:
        logger.info("LLM: Using GPT-4")
        return ChatOpenAI(temperature=0, model_name=llm_name, streaming=True)
    elif llm_name == "gpt-3.5":
        logger.info("LLM: Using GPT-3.5")
        return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True)
    elif llm_name == "claudev2":
        logger.info("LLM: ClaudeV2")
        return ChatBedrock(
            model_id="anthropic.claude-v2",
            model_kwargs={"temperature": 0.0, "max_tokens_to_sample": 1024},
            streaming=True,
        )
    elif llm_name.startswith(AWS_MODELS):
        logger.info(f"LLM: {llm_name}")
        return ChatBedrock(
            model_id=llm_name,
            model_kwargs={"temperature": 0.0, "max_tokens_to_sample": 1024},
            streaming=True,
        )

    elif len(llm_name):
        logger.info(f"LLM: Using Ollama: {llm_name}")
        return ChatOllama(
            temperature=0,
            base_url=config["ollama_base_url"],
            model=llm_name,
            streaming=True,
            # seed=2,
            top_k=10,  # A higher value (100) will give more diverse answers, while a lower value (10) will be more conservative.
            top_p=0.3,  # Higher value (0.95) will lead to more diverse text, while a lower value (0.5) will generate more focused text.
            num_ctx=3072,  # Sets the size of the context window used to generate the next token.
        )
    logger.info("LLM: Using GPT-3.5")
    return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", streaming=True)


def configure_llm_only_chain(llm):
    """
    This function creates a simple LLM chain for processing queries.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You are a helpful AI assistant. Answer the user's question to the best of your ability."
            ),
            HumanMessagePromptTemplate.from_template("{question}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    return chain


def configure_qa_rag_chain(llm, embeddings, embeddings_store_url, username, password):
    """
    This function creates a QA chain with RAG (Retrieval Augmented Generation) functionality.
    """
    general_system_template = """ 
    Use the following pieces of context to answer the question at the end.
    The context contains question-answer pairs and their links from Stackoverflow. 
    You should prefer information from accepted or more upvoted answers.
    Make sure to rely on the information from the context and not on your training data.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ----
    {summaries}
    ----
    Each answer you provide should include a "Sources" section that lists the links of the retrieved documents that were used to answer the question.
    If citing the documents you retrived, please cite it in the format: [Answer by {author} on Stackoverflow]({link}).

    Question: {question}
    """
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)

    qa_chain = configure_retriever(embeddings, embeddings_store_url, username, password)

    chain = (
        RunnableParallel(
            {
                "summaries": qa_chain,
                "question": RunnablePassthrough(),
            }
        )
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    return chain


def configure_retriever(embeddings, embeddings_store_url, username, password):
    """
    Configures a retriever for documents based on vector similarity search.
    """
    vector_store = Neo4jVector.from_existing_index(
        embeddings,
        url=embeddings_store_url,
        username=username,
        password=password,
        database="neo4j",  # neo4j by default
        index_name="stackoverflow",  # vector by default
        text_node_property="body",  # text by default
        keyword_index_name="entity",  # entity by default, if keyword_index_name is None, it will not be used
        search_type="hybrid",  # "vector", "hybrid" (default) or "hybrid"
        node_label="Question",  # Document by default
    )
    # Neo4jVector.from_existing_graph(
    #     embeddings,
    #     url=embeddings_store_url,
    #     username=username,
    #     password=password,
    #     index_name="stackoverflow",
    #     node_label="Question",
    #     text_node_properties=["title", "body"],
    #     embedding_node_property="embedding",
    # )
    retriever = vector_store.as_retriever(search_kwargs={"k": 6})
    return format_docs | retriever


def get_memory():
    return []
