import React, { useState } from "react";
import apiPath from "../utils/apiPath";

export default function AssistantPanel() {
  const [ques, setQues] = useState("");
  const [answer, setAnswer] = useState("");
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendQues() {
    if (!ques.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await fetch(apiPath.asschat, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: ques }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Server Error");
      }

      const data = await res.json();
      setSource(data.source);
      setAnswer(data.answer);
      console.log("Ingested: ", data);
    } catch (err) {
      console.error("Error fetching answer:", err);
      setAnswer("Error: " + (err.message || "Something went wrong"));
      setSource("");
    } finally {
      setLoading(false);
      setQues("");
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow">
      <h3 className="font-medium mb-2">Assistant Response</h3>

      <div className="w-full max-h-60 overflow-auto border rounded-xl bg-gray-50 text-gray-600 mb-4 p-5">
        {loading ? <p>Loading...</p> : answer ? <p>{answer}</p> : <p>No responses yet.</p>}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={ques}
          placeholder="Ask about the repo..."
          className="flex-1 border p-2 rounded-xl"
          onChange={(event) => setQues(event.target.value)}
        />
        <button
          className="bg-green-600 text-white px-4 py-2 rounded-xl font-medium"
          onClick={sendQues}
          disabled={loading}
        >
          Send
        </button>
        <button
          className="bg-gray-300 px-4 py-2 rounded-xl font-medium"
          onClick={() => setQues("")}
        >
          Clear
        </button>
      </div>
    </div>
  );
}
