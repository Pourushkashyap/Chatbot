from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph import START,END, StateGraph
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage, RemoveMessage, SystemMessage,AIMessage
from typing import TypedDict, Annotated, List
from langgraph.store.base import BaseStore
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langchain_core.runnables import RunnableConfig
import uuid
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
import math
load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

class State(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    summary: str
    
class MemoryItem(BaseModel):
    text:str = Field(description='Atomic user memory')
    is_new:bool = Field(description='True if new, false if duplicate')
    
class MemoryDecision(BaseModel):
    should_write: bool
    memories: List[MemoryItem] = Field(default_factory=list)
    
memory_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

memory_extractor = memory_llm.with_structured_output(MemoryDecision)

SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant with memory capabilities.
If user-specific memory is available, use it to personalize 
your responses based on what you know about the user.

Your goal is to provide relevant, friendly, and tailored 
assistance that reflects the user’s preferences, context, and past interactions.

If the user’s name or relevant personal context is available, always personalize your responses by:
    – Always Address the user by name (e.g., "Sure, Nitish...") when appropriate
    – Referencing known projects, tools, or preferences (e.g., "your MCP server python based project")
    – Adjusting the tone to feel friendly, natural, and directly aimed at the user

Avoid generic phrasing when personalization is possible.

TOOLS

You have access to external tools.

Use Calculator whenever:
- arithmetic
- algebra
- percentages
- statistics
- mathematical expressions

Use Tavily Search whenever:
- user asks recent news
- current events
- latest information
- internet lookup
- facts after your knowledge cutoff
- weather
- sports
- companies
- prices

Never make up information that should come from Search.

If no tool is needed,
answer directly.

Do not answer from your own knowledge when a Search tool is required.
Always call the appropriate tool first.


Use personalization especially in:
    – Greetings and transitions
    – Help or guidance tailored to tools and frameworks the user uses
    – Follow-up messages that continue from past context

Always ensure that personalization is based only on known user details and not assumed.

In the end suggest 3 relevant further questions based on the current response and user profile

The user’s memory (which may be empty) is provided as: {user_details_content}
"""

MEMORY_PROMPT = """You are responsible for updating and maintaining accurate user memory.

CURRENT USER DETAILS (existing memories):
{user_details_content}

TASK:
- Review the user's latest message.
- Extract user-specific info worth storing long-term (identity, stable preferences, ongoing projects/goals).
- For each extracted item, set is_new=true ONLY if it adds NEW information compared to CURRENT USER DETAILS.
- If it is basically the same meaning as something already present, set is_new=false.
- Keep each memory as a short atomic sentence.
- No speculation; only facts stated by the user.
- If there is nothing memory-worthy, return should_write=false and an empty list.
"""

def remember_node(state: State,config:RunnableConfig,*,store:BaseStore):
    user_id = config['configurable']['user_id']
    ns = ('user',user_id,'details')
    items = store.search(ns)
    
    existing = "\n".join(it.value.get('data',"") for it in items) if items else "(empty)"
    
    last_messages = state['messages'][-1].content
    decision:MemoryDecision = memory_extractor.invoke(
        [
            SystemMessage(content=MEMORY_PROMPT.format(user_details_content=existing)),
            {'role':'user','content':last_messages}
        ]
    )
    
    if decision.should_write:
        for mem in decision.memories:
            if mem.is_new and mem.text.strip():
                store.put(
                    ns,
                    str(uuid.uuid4()),
                    {
                        'data':mem.text.strip()
                        }
                    )
    return {}


@tool
def calculator(expression:str):
    """
    Evaluate a mathematical expression.
    
    Example:
    23*45
    sqrt(81)+15
    """
    
    try:
        return str(eval(expression, {"__builtins__": {}}, math.__dict__))
    except Exception as e:
        return str(e)
    

search_tool = TavilySearchResults(max_results=5)


tools = [calculator,search_tool]
tool_llm = llm.bind_tools(tools)

def chat(state:State,config:RunnableConfig,*,store:BaseStore):
    user_id = config['configurable']['user_id']
    ns = ('user',user_id,'details')
    items = store.search(ns)
    user_details = "\n".join(it.value.get('data',"") for it in items) if items else ""
    
    messages = []
    summary = state.get('summary',"")
    if summary:
        messages.append({
            'role':'system',
            'content':f'conversatiion summary:\n{summary}'
        })
    system_msg = SystemMessage(
        content=SYSTEM_PROMPT_TEMPLATE.format(user_details_content=user_details or "(empty)")
        
    )   
     
    messages.extend(state['messages'])    
    
    response = tool_llm.invoke([system_msg] + messages)
    
    return {'messages':[response]}





    
def summarize_conversation(state:State):
    existing_summary = state.get('summary',"")
    if existing_summary:
        prompt = (
            f"Existing summary:\n{existing_summary}\n\n."
            "extend the summary using the new conversation above."
        )
    else:
        prompt = 'Summarize the conversation above.'
        
    message_for_summary = state['messages'] + [HumanMessage(content=prompt)]
    response = llm.invoke(message_for_summary)   
    
    message_to_delte = state['messages'][:-4]
    return {'summary':response.content,
            'messages':[RemoveMessage(id=m.id) for m in message_to_delte]
            }     
    
    
def should_summarize(state:State):
    return len(state.get("messages", [])) > 6

tool_node = ToolNode(tools)

def should_continue(state: State):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "summarize"
def check_summary_node(state:State):
    return {}

DB_URI = "postgresql://postgres:postgres@localhost:5442/chatbot"

g = StateGraph(State)
g.add_node('chat',chat)
g.add_node('summarize',summarize_conversation)
g.add_node('remember',remember_node)
g.add_node('tools',tool_node)
g.add_node('check_summary',check_summary_node)

g.add_edge(START,'remember')
g.add_edge('remember','chat')
g.add_conditional_edges('chat',should_continue,{'tools':'tools','summarize':'check_summary'})
g.add_edge('tools','chat')
g.add_conditional_edges('check_summary',should_summarize,{True:'summarize',False:END})
g.add_edge('summarize',END)

checkpointer_cm = PostgresSaver.from_conn_string(DB_URI)
store_cm = PostgresStore.from_conn_string(DB_URI)

checkpointer = checkpointer_cm.__enter__()
store = store_cm.__enter__()

checkpointer.setup()
store.setup()

graph = g.compile(
    checkpointer=checkpointer,
    store=store
)


                    