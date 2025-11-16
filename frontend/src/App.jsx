import React from "react";
import SidePanel from "./components/SidePanel";
import CodeViewer from "./components/CodeViewer";
import AssistantPanel from "./components/AssistantPanel";

export default function App() {
  return (
    <div className="w-full h-screen bg-gray-100 p-6 grid grid-cols-3 gap-6">
      <SidePanel />
      <div className="col-span-2 flex flex-col gap-4">
        <CodeViewer />
        <AssistantPanel />
      </div>
    </div>
  );
}