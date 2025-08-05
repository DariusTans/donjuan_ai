from langchain.schema.runnable import Runnable
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable.config import RunnableConfig
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from prompt import DONJUANAI_PROMPT_BASIC,DONJUANAI_PROMPT_CHATGAME,DONJUANAI_PROMPT_ANALYZE_IMAGE_CHATGAME
from typing import cast

from langchain_openai import ChatOpenAI
from core import setup_runnable, analyze_image_chatgame
import logging
import chainlit as cl

@cl.author_rename
def rename(orig_author: str):
    rename_dict = {
        "ChatOpenAI": "DonjuanAI for Chatgame V.1",
    }
    return rename_dict.get(orig_author, orig_author)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True, model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template(DONJUANAI_PROMPT_CHATGAME)
    runnable = prompt | model | StrOutputParser()
    logging.info("PROMPT "+ str(prompt))
    
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    # runnable = await setup_runnable()
    cl.user_session.set("runnable", runnable)

@cl.on_chat_resume
async def on_chat_resume(thread):
    # NOT Impremented yet
    pass

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")
    images = []

    for element in message.elements:
        if "image" in element.mime: # image analysis
            await cl.Message(
                content="Image received, processing...",
            ).send()
            with open(element.path, "rb") as image_file:
                image_data = image_file.read()
            
            images.append(image_data)
    
    if len(images) > 0:
        stream = await analyze_image_chatgame(images, DONJUANAI_PROMPT_ANALYZE_IMAGE_CHATGAME)
        if stream:
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    # logging.info(f"Chunk: {content}")
                    await msg.stream_token(content)
            await msg.update()
        else:
            await msg.send("No analysis available for the image.")
    else: # text message
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()