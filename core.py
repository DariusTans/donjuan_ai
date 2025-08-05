from operator import itemgetter
import chainlit as cl
from langchain_openai import ChatOpenAI, OpenAIEmbeddings 
from langchain.schema.runnable import RunnableParallel
from langchain.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY
from prompt import DONJUANAI_PROMPT_CHATGAME
from langchain.schema import StrOutputParser
from vectordb import get_vector_store
import base64
from openai import AsyncOpenAI


# Initialize AsyncOpenAI client
async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def setup_runnable():
    '''
      setup runnable for chain and memory
    '''
    memory = cl.user_session.get("memory")
    embedding = OpenAIEmbeddings(model="text-embedding-3-small",api_key=OPENAI_API_KEY)
    def get_history():
        return memory.load_memory_variables({})["history"]

    vector_store = get_vector_store(embedding)
    retriever = vector_store.as_retriever(search_kwargs={"k": 6})


    llm = ChatOpenAI(
        streaming=True,
        temperature=0,
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY
    )
    prompt  = ChatPromptTemplate.from_template(DONJUANAI_PROMPT_CHATGAME)
    runnable = (
        RunnableParallel({
          "context": lambda x: retriever.get_relevant_documents(x["question"]),
          "question": itemgetter("question"),
          "history": lambda x: get_history()
        })
        | prompt
        | llm
        | StrOutputParser()
    )
    return runnable

# Function to call OpenAI for image analysis
async def analyze_image_chatgame(images : list, prompt, model="gpt-4.1", max_tokens=500):
    # Convert the image data to base64
    encoded_images = []
    for image_data in images:
        encoded_image = base64.b64encode(image_data).decode("utf-8")
        encoded_images.append(encoded_image)

    # Create the data URL with the base64-encoded image
    image_urls = [f"data:image/jpeg;base64,{encoded_image}" for encoded_image in encoded_images]
    images = [{"type": "image_url", "image_url": {"url": image_url}} for image_url in image_urls]
    content = [
        {"type": "text", "text": prompt}
    ]
    content.extend(images)
    print(f"Content: {content}")
    # Create the request with the new format
    stream = await async_openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an AI image analyst."},
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=max_tokens,
        stream=True,
    )

    return stream
