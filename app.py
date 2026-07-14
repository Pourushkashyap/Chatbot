from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from graph import graph, checkpointer_cm,store_cm
from services.title_service import generate_title
from schemas import ChatRequest, ChatResponse
from services.thread_service import get_threads
from services.thread_service import (update_thread,update_title,get_title,create_thread)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event("shutdown")
def shutdown():
    checkpointer_cm.__exit__(None, None, None)
    store_cm.__exit__(None, None, None)


@app.post('/chat',response_model=ChatResponse)
async def chat(request: ChatRequest):
    
    if request.thread_id is None:
        thread_id = create_thread(request.user_id)
    else:
        thread_id = request.thread_id
            
    
    config = {
        'configurable':{
            'thread_id':thread_id,
            'user_id':request.user_id,
        }
    }
    result = graph.invoke(
        {
            'messages':[
                HumanMessage(content=request.message)
            ]
        },
        config=config
    )
    update_thread(thread_id)
    title = get_title(thread_id)
    
    try:
     if title == "New Chat":
        ai_title = generate_title(request.message)
        update_title(thread_id, ai_title)
        title = ai_title
    except Exception as e:
        print(f"Title generation failed: {e}")
        
    return ChatResponse(
        thread_id = thread_id,
        response=result['messages'][-1].content
    )
    
@app.get('/threads/{user_id}')
def get_all_threads(user_id:str):
    rows = get_threads(user_id)
    
    return [
        {
            "thread_id":row[0],
            'title':row[1]
        }
        for row in rows
    ]    
 
 
    
@app.get('/chat/{thread_id}')
def get_chat(thread_id:str,user_id:str):
    config = {
        'configurable':{
            'thread_id':thread_id,
            'user_id':user_id
        }
    }    
    state = graph.get_state(config)
    if state is None or state.values is None:
     return []

    history = []
    messages = state.values.get('messages',[])
    for message in messages:
        history.append({
            'role':message.type,
            'content':message.content
        })
    return history    