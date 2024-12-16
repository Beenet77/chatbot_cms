import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [language, setLanguage] = useState("en");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: "user",
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/api/chat/", {
        message: inputMessage,
        language: language,
      });

      const botMessage = {
        type: "bot",
        content: response.data.bot_response,
        source: response.data.source,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        type: "bot",
        content:
          language === "en"
            ? "Sorry, I encountered an error. Please try again."
            : "Maaf garnuhos, kehi samasya aayo. Pheri prayas garnuhos.",
        source: "error",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (message) => {
    if (message.source === "cms") {
      return message.content.split("\n\n").map((paragraph, idx) => (
        <p key={idx} className="cms-paragraph">
          {paragraph}
        </p>
      ));
    }
    return message.content;
  };

  return (
    <div className="chatbot-container">
      {!isOpen && (
        <button
          className="chat-toggle-button"
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          <span role="img" aria-label="chat">
            💬
          </span>{" "}
          {language === "en" ? "NEPSE Assistant" : "NEPSE Sahayog"}
        </button>
      )}

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>{language === "en" ? "NEPSE Assistant" : "NEPSE Sahayog"}</h3>
            <div className="header-controls">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="language-selector"
              >
                <option value="en">English</option>
                <option value="ne">Nepali</option>
              </select>
              <button
                className="close-button"
                onClick={() => setIsOpen(false)}
                aria-label="Close chat"
              >
                ×
              </button>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                {language === "en"
                  ? "Hello! Ask me anything about NEPSE."
                  : "Namaste! NEPSE ko barema kehi sodhnus."}
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.type} ${message.source || ""}`}
              >
                {formatMessage(message)}
                {message.source === "cms" && (
                  <div className="message-source">
                    {language === "en"
                      ? "Official Information"
                      : "Adhikarik Janakari"}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="message bot loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                language === "en"
                  ? "Type your message..."
                  : "Aafno sandesh type garnus..."
              }
              aria-label="Chat input"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              aria-label="Send message"
            >
              {language === "en" ? "Send" : "Pathaunus"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
