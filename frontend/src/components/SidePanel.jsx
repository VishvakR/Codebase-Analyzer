import React, { useState, useEffect} from "react";
import {toast, Toaster} from 'react-hot-toast'
import apiPath from "../utils/apiPath";

export default function SidePanel() {
  const [repoUrl, setRepoUrl] = useState("");
  const [tree, setTree] = useState([])
  const [source, setSource] = useState("")
  async function ingestClick(){
    if(!repoUrl){
        toast.error("Enter the repo URL")
    }
    else{
        try {
            toast.success("Repo is Downloading")
            const res = await fetch(apiPath.clonerepo, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: repoUrl }),
        });

        const data = await res.json();
        console.log("Ingested: ", data);
        } catch (err) {
            console.error("Error ingesting:", err);
            toast.error("Sorry we got some error")
        }
        
    }
  }
  useEffect(() => {
    fetch(apiPath.treestructure)
      .then(res => res.json())
      .then(data => setTree(data.tree))
      .catch(err => {
        console.error(err)
        toast.error("Sorry Failed to fetch")
      });
  }, [repoUrl]);

  useEffect(() => {
    fetch(apiPath.source)
      .then(res => res.json())
      .then(data => setSource(data.src))
      .catch(err => console.error(err));
  }, [repoUrl]);
  
  const treeString = tree.join("\n");

  function onReset(){
    toast.success("Memory has been reset")
    fetch(apiPath.resetmemory)
      .then(res => res.json())
      .then(data => console.log(data))
      .catch(err => console.error(err))

  }

  return (
    <div className="col-span-1 bg-white p-6 rounded-2xl shadow">
      <h2 className="text-xl font-semibold mb-4">Codebase Investigator</h2>

      <p className="text-sm font-medium">Status:</p>
      <input className="w-full border rounded-xl p-2 bg-gray-100 mb-4" value="Idle" readOnly />

      <p className="text-sm font-medium">Repository URL</p>
      <div className="flex gap-2 mt-1 mb-4">
        <input
          type="text"
          placeholder="https://github.com/org/repo"
          className="flex-1 border p-2 rounded-xl"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />
        <button className="px-4 py-2 bg-purple-500 rounded-xl text-white font-semibold hover:bg-purple-600" onClick={ingestClick}> Ingest</button>
        <Toaster />
      </div>

      <p className="text-sm font-medium mb-1">Source</p>
      <div className="w-full h-24 border rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 text-sm mb-4">{source || <p>No Source yet.</p>}</div>

      <p className="text-sm font-medium">File Tree Explorer</p>
      <pre className="bg-gray-900 text-green-300 text-sm p-4 rounded-xl h-48 overflow-auto mt-2">
        {treeString || <p>No responses yet.</p>}
      </pre> 

      <div className="flex gap-2 mt-4">
        <button className="bg-red-600 text-white px-4 py-2 rounded-xl font-medium" onClick={onReset}>Reset Memory</button>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-xl font-medium">Download</button>
      </div>
    </div>
  );
}