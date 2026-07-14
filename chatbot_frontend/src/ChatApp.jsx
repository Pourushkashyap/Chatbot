import { useState, useRef, useEffect } from "react";
import { User, Bot, Send, Loader2, Plus, MessageSquare } from "lucide-react";


const API_URL = "http://localhost:8000";
const USER_ID = "user_1"; 

export default function ChatApp() {
  const [threads, setThreads] = useState([]); 
  const [threadId, setThreadId] = useState(null);
  const [messages, setMessages] = useState([]); 
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [threadsLoading, setThreadsLoading] = useState(true);
  const bottomRef = useRef(null);

  useEffect(() => {
    loadThreads();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

 async function loadThreads() {

    setThreadsLoading(true);

    try{

        const res=await fetch(
            `${API_URL}/threads/${USER_ID}`
        );

        const data=await res.json();

        setThreads(data);

    }

    catch(err){

        console.log(err);

    }

    finally{

        setThreadsLoading(false);

    }

}

  async function openThread(id){

    if(id===threadId)
        return;

    setLoading(true);

    try{

        const res=await fetch(

            `${API_URL}/chat/${id}?user_id=${USER_ID}`

        );

        const history=await res.json();

        setThreadId(id);

        setMessages(

            history.map(msg=>({

                role:msg.role==="human"?"human":"ai",

                content:msg.content

            }))

        );

    }

    catch(err){

        console.log(err);

    }

    finally{

        setLoading(false);

    }

}

  function startNewChat() {
    setThreadId(null);
    setMessages([]);
    setInput("");
  }

  async function sendMessage(){

    const text=input.trim();

    if(!text || loading)
        return;

    setMessages(prev=>[

        ...prev,

        {

            role:"human",

            content:text

        }

    ]);

    setInput("");

    setLoading(true);

    try{

        const res=await fetch(

            `${API_URL}/chat`,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    user_id:USER_ID,

                    thread_id:threadId,

                    message:text

                })

            }

        );

        const data=await res.json();
        const isNewThread = threadId === null;
        
        setThreadId(data.thread_id);

        setMessages(prev=>[

            ...prev,

            {

                role:"ai",

                content:data.response

            }

        ]);
        if (isNewThread) {
    await loadThreads();
    setTimeout(async () => {
        await loadThreads();
    }, 1000);
} else {
    setThreads(prev => {
        const updated = [...prev];

        const index = updated.findIndex(
            t => t.thread_id === data.thread_id
        );

        if (index !== -1) {
            const thread = updated[index];

            updated.splice(index, 1);

            updated.unshift(thread);
        }

        return updated;
    });
}
    }

    catch(err){

        setMessages(prev=>[

            ...prev,

            {

                role:"ai",

                content:"Server Error"

            }

        ]);

    }

    finally{

        setLoading(false);

    }

}

  function handleKeyDown(e) {
     if (loading) {

        e.preventDefault();

        return;

    }

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        sendMessage();

    }
  }

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-[#EDEDED]">
      <style>{`
        .sidebar-scroll::-webkit-scrollbar { width: 6px; }
        .sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
        .sidebar-scroll::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 999px; }
        .sidebar-scroll::-webkit-scrollbar-thumb:hover { background: #3A3A3A; }
        .sidebar-scroll { scrollbar-width: thin; scrollbar-color: #2A2A2A transparent; }
      `}</style>

    
      <div className="w-64 shrink-0 flex flex-col border-r border-white/10 min-h-0">
        <div className="p-3 shrink-0">
          <button
            onClick={startNewChat}
            className="w-full flex items-center gap-2 rounded-lg border border-white/10 hover:bg-[#171717] px-3 py-2 text-sm transition-colors"
          >
            <Plus size={15} className="text-[#F2A93B]" />
            New chat
          </button>
        </div>

        <div className="sidebar-scroll flex-1 min-h-0 overflow-y-auto px-2 pb-3 space-y-0.5">
          {threadsLoading && (
            <p className="text-xs text-[#9A9A9A] px-3 py-2">Loading chats…</p>
          )}

          {!threadsLoading && threads.length === 0 && (
            <p className="text-xs text-[#9A9A9A] px-3 py-2">No chats yet.</p>
          )}

          {threads.map((t) => (
            <button
              key={t.thread_id}
              onClick={() => openThread(t.thread_id)}
              className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-left truncate transition-colors ${
                t.thread_id === threadId
                  ? "bg-[#F2A93B]/10 text-[#F2A93B]"
                  : "hover:bg-[#171717] text-[#D4D4D4]"
              }`}
            >
              <MessageSquare size={14} className="shrink-0 opacity-70" />
              <span className="truncate">{t.title || "New Chat"}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Chat panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
          <div className="w-9 h-9 rounded-full bg-[#F2A93B]/10 flex items-center justify-center">
            <Bot size={18} className="text-[#F2A93B]" />
          </div>
          <div>
            <p className="text-sm font-medium leading-none">Agent</p>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#F2A93B] animate-pulse" />
              <span className="text-xs text-[#9A9A9A]">
                {loading ? "thinking…" : "online"}
              </span>
            </div>
          </div>
        </div>

       
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.length === 0 && !loading && (
            <p className="text-center text-sm text-[#9A9A9A] mt-10">
              Say something to start the conversation.
            </p>
          )}

          {messages.map((m, i) => {
            const isUser = m.role === "human";
            return (
              <div
                key={i}
                className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="w-7 h-7 shrink-0 rounded-full bg-[#171717] border border-white/10 flex items-center justify-center">
                    <Bot size={14} className="text-[#F2A93B]" />
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                      ? "bg-[#F2A93B] text-[#1A1206] rounded-br-sm"
                      : "bg-[#171717] border border-white/10 rounded-bl-sm"
                  }`}
                >
                  {m.content}
                </div>
                {isUser && (
                  <div className="w-7 h-7 shrink-0 rounded-full bg-[#F2A93B]/10 flex items-center justify-center">
                    <User size={14} className="text-[#F2A93B]" />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex items-end gap-2 justify-start">
              <div className="w-7 h-7 shrink-0 rounded-full bg-[#171717] border border-white/10 flex items-center justify-center">
                <Bot size={14} className="text-[#F2A93B]" />
              </div>
              <div className="bg-[#171717] border border-white/10 rounded-2xl rounded-bl-sm px-4 py-2.5">
                <Loader2 size={14} className="animate-spin text-[#9A9A9A]" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-white/10 px-4 py-3">
          <div className="flex items-end gap-2 bg-[#171717] border border-white/10 rounded-xl px-3 py-2">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message the agent…"
              className="flex-1 bg-transparent resize-none outline-none text-sm py-1.5 placeholder:text-[#9A9A9A] max-h-32"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="w-8 h-8 shrink-0 rounded-lg bg-[#F2A93B] disabled:bg-white/10 disabled:text-[#9A9A9A] flex items-center justify-center transition-colors"
            >
              <Send size={15} className={loading || !input.trim() ? "" : "text-[#1A1206]"} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
