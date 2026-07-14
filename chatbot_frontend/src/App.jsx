// import Layout from "./components/Layout/Layout";
// import useChat from "./hooks/useChat";

// function App() {
//   const {
//     threads,
//     currentThread,
//     messages,
//     loading,
//     handleNewChat,
//     selectThread,
//     handleSend,
//   } = useChat();

//   return (
//     <Layout
//       chats={threads}
//       currentChat={currentThread}
//       messages={messages}
//       loading={loading}
//       onNewChat={handleNewChat}
//       onSelectChat={selectThread}
//       onSend={handleSend}
//     />
//   );
// }

// export default App;

import React from 'react'
import ChatApp from './ChatApp.jsx'
function App() {
  return (
    <ChatApp/>
  )
}

export default App