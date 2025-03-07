// frontend/src/components/ChatWindow.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
const EmojiPicker = React.lazy(() => import('emoji-picker-react'));
import './ChatWindow.css';

const ChatWindow = ({ userId }) => {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const chatEndRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [isStartingNewChat, setIsStartingNewChat] = useState(false);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    console.log('Conversation state:', conversation);
    fetchChatHistory();
  }, [conversation]);

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/history/${userId}`);
      console.log('Raw history response:', response.data);
      const history = response.data.history || [];
      console.log('Processed history:', history);
      setChatHistory(history);

      // If starting a new chat or on initial load, don't auto-select a conversation
      if (isStartingNewChat || (!currentConversationId && !selectedConversation && history.length > 0)) {
        setIsStartingNewChat(false);
        setConversation([]); // Ensure chat window is empty on new chat or initial load
        return;
      }

      // Only load a conversation if currentConversationId is set
      if (currentConversationId) {
        const currentConv = history.find(conv => conv.conversation_id === currentConversationId);
        if (currentConv) {
          setConversation(currentConv.messages.map(msg => ({ user: msg.user, bot: msg.bot })));
          setSelectedConversation(currentConv);
        } else {
          setConversation([]); // Clear if the current conversation is not found
        }
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
      setChatHistory([]);
    }
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    const newMessage = { user: message, bot: '' };
    setConversation([...conversation, newMessage]);
    setMessage('');

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        user_id: userId,
        message,
        conversation_id: currentConversationId
      });
      setConversation((prev) => [...prev, { user: message, bot: response.data.response }]);
      setCurrentConversationId(response.data.conversation_id);
      fetchChatHistory();
    } catch (error) {
      console.error('Error sending message:', error);
      setConversation((prev) => [...prev, { user: message, bot: 'Error: Could not get response' }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const onEmojiClick = (event, emojiObject) => {
    setMessage((prevMessage) => prevMessage + emojiObject.emoji);
    setShowEmojiPicker(false);
  };

  const startNewConversation = async () => {
    try {
      setIsStartingNewChat(true);
      const response = await axios.post(`http://localhost:8000/new-conversation/${userId}`);
      const newConversationId = response.data.conversation_id;
      setCurrentConversationId(newConversationId);
      setConversation([]);
      setSelectedConversation(null);
      fetchChatHistory();
    } catch (error) {
      console.error('Error starting new conversation:', error);
      setIsStartingNewChat(false);
    }
  };

  const selectConversation = (conv) => {
    setSelectedConversation(conv);
    setConversation(conv.messages.map(msg => ({ user: msg.user, bot: msg.bot })));
    setCurrentConversationId(conv.conversation_id);
  };

  return (
    <div className="chat-container flex">
      {/* Side Panel for Chat History */}
      <div className="chat-history">
        <h3 className="history-title">Chat History</h3>
        <button onClick={startNewConversation} className="new-chat-button">
          New Chat
        </button>
        <div className="history-content">
          {chatHistory.length > 0 ? (
            chatHistory.map((conv, idx) => (
              <div
                key={idx}
                className={`history-item ${conv.conversation_id === currentConversationId ? 'active' : ''}`}
                onClick={() => selectConversation(conv)}
              >
                {conv.summary}
              </div>
            ))
          ) : (
            <p className="no-history">No previous chats yet.</p>
          )}
        </div>
      </div>
      {/* Existing Chat Area */}
      <div className="chat-main">
        <div className="chat-window">
          {conversation.map((msg, idx) => (
            <div key={idx} className={`message-group ${msg.user ? 'user' : 'bot'}`}>
              {msg.user && <div className="user-message">{msg.user}</div>}
              {msg.bot && <div className="bot-message">{msg.bot}</div>}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className="input-container">
          <button onClick={() => setShowEmojiPicker(!showEmojiPicker)} className="emoji-button">
            😊
          </button>
          {typeof window !== 'undefined' && showEmojiPicker && (
            <React.Suspense fallback={<div>Loading emoji picker...</div>}>
              <EmojiPicker onEmojiClick={onEmojiClick} />
            </React.Suspense>
          )}
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="chat-input"
          />
          <button onClick={sendMessage} className="send-button">
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;