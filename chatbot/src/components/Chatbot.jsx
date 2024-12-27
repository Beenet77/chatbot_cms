import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";
import { IoSend } from "react-icons/io5";
import { FaUser } from "react-icons/fa";
import { RiRobot2Fill } from "react-icons/ri";
import { IoClose } from "react-icons/io5";

const DEFAULT_MASCOT =
  "https://cdn3d.iconscout.com/3d/premium/thumb/chatbot-5374800-4492376.png";
const DEFAULT_CHAT_LOGO =
  "https://cdn-icons-png.flaticon.com/512/1698/1698535.png";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [language, setLanguage] = useState("en");
  const [isLoading, setIsLoading] = useState(false);
  const [logoUrl, setLogoUrl] = useState(null);
  const [masUrl, setMasUrl] = useState(null);
  const [userEmail, setUserEmail] = useState(
    () => localStorage.getItem("userEmail") || ""
  );
  const [userName, setUserName] = useState(
    () => localStorage.getItem("userName") || ""
  );
  const [showForm, setShowForm] = useState(
    () => !localStorage.getItem("userName")
  );
  const messagesEndRef = useRef(null);
  const [showCloseConfirm, setShowCloseConfirm] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchLogo = async () => {
    try {
      const response = await axios.get(`${API_URL}/logo/`);
      console.log("Logo response:", response.data);

      setLogoUrl(
        response.data.main_logo
          ? `${API_URL.replace("/api", "")}${response.data.main_logo}`
          : null
      );
      setMasUrl(
        response.data.mascot_logo
          ? `${API_URL.replace("/api", "")}${response.data.mascot_logo}`
          : null
      );
    } catch (error) {
      console.error("Error fetching logo:", error);
      setLogoUrl(null);
      setMasUrl(null);
    }
  };

  useEffect(() => {
    fetchLogo();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    if (showForm && (!userName.trim() || !userEmail.trim())) {
      alert(
        language === "en"
          ? "Please fill in your name and email"
          : "कृपया आफ्नो नाम र इमेल भर्नुहोस्"
      );
      return;
    }

    const userMessage = {
      type: "user",
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat/`, {
        message: inputMessage,
        language: language,
        ...(showForm && { user_name: userName, user_email: userEmail }),
      });

      if (showForm) {
        setShowForm(false);
      }

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
            : "माफ गर्नुहोस्, ही समस्या आयो। कृपया फेरि प्रयास गर्नुहोस्।",
        source: "error",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (message) => {
    if (message.source === "cms") {
      const responses = message.content.split("\n\n---\n\n");
      return responses.map((response, idx) => (
        <div key={idx} className="cms-response">
          {response.split("\n\n").map((paragraph, pIdx) => (
            <p key={pIdx} className="cms-paragraph">
              {paragraph}
            </p>
          ))}
          {idx < responses.length - 1 && <hr className="response-divider" />}
        </div>
      ));
    }
    return message.content;
  };

  const handleUserInfoSubmit = async (e) => {
    e.preventDefault();
    if (!userName.trim() || !userEmail.trim()) {
      alert(
        language === "en"
          ? "Please fill in your name and email"
          : "कृपया आफ्नो नाम र इमेल भर्नुहोस्"
      );
      return;
    }

    try {
      const userResponse = await axios.post(`${API_URL}/chat/user/`, {
        user_name: userName,
        user_email: userEmail,
      });

      if (userResponse.status === 200 || userResponse.data.status === 400) {
        localStorage.setItem("userName", userName);
        localStorage.setItem("userEmail", userEmail);

        const chatResponse = await axios.post(`${API_URL}/chat/`, {
          message: language === "en" ? "Hello" : "Namaste",
          language: language,
        });

        setShowForm(false);
        const botMessage = {
          type: "bot",
          content: chatResponse.data.bot_response,
          source: chatResponse.data.source,
        };
        setMessages([botMessage]);
      }
    } catch (error) {
      console.error("Error saving user info:", error);
      alert(
        language === "en"
          ? "Error saving information. Please try again."
          : "जानकारी सुरक्षित गर्न मस्या भयो। कृपया पुन: प्रयास गर्न��होस्।"
      );
    }
  };

  const handleClose = () => {
    setShowCloseConfirm(true);
  };

  const handleCloseConfirm = (confirmed) => {
    setShowCloseConfirm(false);
    if (confirmed) {
      localStorage.removeItem("userName");
      localStorage.removeItem("userEmail");
      setIsOpen(false);
      setShowForm(true);
      setUserName("");
      setUserEmail("");
    }
  };

  useEffect(() => {
    const handleTabClose = () => {
      localStorage.removeItem("userName");
      localStorage.removeItem("userEmail");
    };

    window.addEventListener("beforeunload", handleTabClose);

    return () => {
      window.removeEventListener("beforeunload", handleTabClose);
    };
  }, []);

  return (
    <div className="chatbot-container">
      {!isOpen && (
        <button
          className="chat-toggle-button"
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          <div className="mascot-container">
            <img
              src={masUrl || DEFAULT_MASCOT}
              alt="AI Assistant"
              className="mascot-image"
              onError={(e) => {
                console.log("Mascot load error, using default");
                e.target.src = DEFAULT_MASCOT;
              }}
            />
          </div>
        </button>
      )}

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="header-content">
              <img
                src={logoUrl || DEFAULT_CHAT_LOGO}
                alt="Chat Logo"
                className="chat-logo"
                onError={(e) => {
                  console.log("Logo load error, using default");
                  e.target.src = DEFAULT_CHAT_LOGO;
                }}
              />
              <h3>Capital Max Chatbot</h3>
            </div>
            <div className="header-content">
              <button
                className="close-button"
                onClick={handleClose}
                aria-label="Close chat"
              >
                <IoClose />
              </button>
            </div>
          </div>

          <div className="chat-messages">
            {showForm ? (
              <div className="user-info-form">
                <h4>
                  {language === "en"
                    ? "Welcome to Capital Max Assistant"
                    : "Capital Max सहायकमा स्वागत छ"}
                </h4>
                <p>
                  {language === "en"
                    ? "Please provide your information to continue"
                    : "कृपया जारी राख्न आफ्नो जानकारी प्रदान गर्नुहोस्"}
                </p>
                <form onSubmit={handleUserInfoSubmit}>
                  <input
                    type="text"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder={
                      language === "en" ? "Your Name" : "तपाईंको नाम"
                    }
                    required
                  />
                  <input
                    type="email"
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    placeholder={
                      language === "en" ? "Your Email" : "तपाईंको इमेल"
                    }
                    required
                  />
                  <button type="submit">
                    {language === "en"
                      ? "Start Chat"
                      : "कुराकानी सुरु गर्नुहोस्"}
                  </button>
                </form>
              </div>
            ) : (
              <>
                {messages.length === 0 && (
                  <div className="welcome-message">
                    {language === "en"
                      ? `Hello, I am Capital Max! Ask me anything about NEPSE.`
                      : `नमस्ते, म Capital Max हुँ! NEPSE को बारेमा केही सोध्नुहोस्।`}
                  </div>
                )}
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`message ${message.type} ${
                      message.source || ""
                    }`}
                  >
                    <div className="message-content">
                      <div className="message-icon">
                        {message.type === "user" ? (
                          <FaUser />
                        ) : (
                          <RiRobot2Fill />
                        )}
                      </div>
                      <div className="message-text">
                        {formatMessage(message)}
                        {message.source === "cms" && (
                          <div className="message-source">
                            {language === "en"
                              ? "Official Information"
                              : "Adhikarik Janakari"}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="message bot loading">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {!showForm && (
            <form onSubmit={handleSubmit} className="chat-input-form">
              <div className="message-input-container">
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
                  required
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isLoading}
                  aria-label="Send message"
                >
                  <IoSend />
                </button>
              </div>
            </form>
          )}

          {showCloseConfirm && (
            <div className="confirm-overlay">
              <div className="confirm-popup">
                <h4>
                  {language === "en" ? "Close Chat?" : "कुराकानी बन्द गर्ने?"}
                </h4>
                <p>
                  {language === "en"
                    ? "Are you sure you want to end this chat?"
                    : "के तपाईं यो कुराकानी अन्त्य र्न चाहनुहुन्छ?"}
                </p>
                <div className="confirm-buttons">
                  <button
                    onClick={() => handleCloseConfirm(true)}
                    className="confirm-yes"
                  >
                    {language === "en" ? "End" : "हो, बन्द गर्नुहोस्"}
                  </button>
                  <button
                    onClick={() => handleCloseConfirm(false)}
                    className="confirm-no"
                  >
                    {language === "en" ? " Continue" : "होइन, जारी राख्नुहोस्"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Chatbot;
