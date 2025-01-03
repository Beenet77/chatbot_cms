import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import Chatbot from "./components/Chatbot";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div className="min-h-screen bg-gray-100">
        <Chatbot />
      </div>
    </>
  );
}

export default App;
