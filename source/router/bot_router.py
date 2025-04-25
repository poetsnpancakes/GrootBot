from fastapi import Depends, APIRouter ,Request ,HTTPException ,Response ,Cookie
from sqlalchemy.orm import Session
from Models.gpt4omini import query_model  
from Utilities.llm_rephrase import llm_rephrase
from Utilities.query_classifier import classify_query
from Utilities.qdrant_search import qdrant_search
from Utilities.sql_query_generator import sql_query
from Utilities.bot_template import bot_template
from Database.sqlDB import get_session
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from Models.gpt4omini import llm
from Request_Model.Chat_Request import ChatRequest
import uuid
import threading



router = APIRouter(prefix="/bot", tags=["bot"])





# Dictionary to hold thread-based memory
thread_memory_store = {}

# Create a lock to manage memory cleanup
memory_lock = threading.Lock()


# Function to generate session ID
def generate_session_id():
    return str(uuid.uuid4())


# Function to create a new memory for a session
def get_memory(session_id):
    with memory_lock:
        if session_id not in thread_memory_store:
            thread_memory_store[session_id] = ConversationBufferMemory()
        return thread_memory_store[session_id]


# Function to delete memory after thread ends
def cleanup_memory(session_id):
    with memory_lock:
        if session_id in thread_memory_store:
            del thread_memory_store[session_id]







@router.post("/query/rephrase")
async def query_rephrase(query : str, request:Request, response:Response):
    #query = request.message
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = generate_session_id()
        response.set_cookie(key="session_id", value=session_id)
        print("Session ID >>>>>>>>>>",session_id)

    memory = get_memory(session_id)

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    #rephrased_query = llm_rewrite(query)
    route = classify_query(query)

    # Step 3: Route accordingly
    if route == "semantic":
        rephrased_query = llm_rephrase(query)
        response_query = qdrant_search(rephrased_query)
        
         # Get LLM response
        answer = conversation.predict(input=response_query)
    
    elif route == "relational":
        relational_query = sql_query(query)
        #results = sql_agent.invoke(rephrased_query)
        answer = conversation.predict(input=relational_query)
    
    else:
        # fallback to plain LLM
        general_query = bot_template(query)
        answer = conversation.predict(input=general_query)


    # # ✅ Persist to memory
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(answer)

    return {
        "session_id": session_id,
        "query": query,
        "route": route,
        "answer": answer
    }

@router.delete("/end_session")
async def end_session(session_id: str):
    if session_id not in thread_memory_store:
        raise HTTPException(status_code=404, detail="Session ID not found.")

    # Delete the memory for the session
    del thread_memory_store[session_id]
    return {"message": f"Session {session_id} ended successfully."}

@router.get("/read_cookie")
async def read_cookie(session_id : str = Cookie(None)):
    return {"session_id":session_id}

@router.get("/get_session_list")
async def get_all_active_sessions():
    """
    Returns a list of all active session IDs in the thread_memory_store.
    """
    return list(thread_memory_store.keys())






    
























