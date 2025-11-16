import React, { useState, useEffect } from "react";
import apiPath from "../utils/apiPath";

export default function CodeViewer() {
  const [selectedFile, setSelectedFile] = useState("Choose the file");
  const [data, setData] = useState([]);
  const [listFile, setListFile] = useState([]);
  const [show, setShow] = useState("");
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingCode, setLoadingCode] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoadingFiles(true);
      try {
        const res = await fetch(apiPath.listfiles);
        const json = await res.json();
        setData(json.files);
        const firstElements = json.files.map(file => file[0]);
        setListFile(firstElements);
      } catch (err) {
        console.error("Error:", err);
      } finally {
        setLoadingFiles(false);
      }
    };

    fetchData();
  }, []);

  const getFilePath = (fileName) => {
    if (!data || data.length === 0) return null;
    const match = data.find(item => item[0] === fileName);
    return match ? match[1] : null;
  };

  async function whenSwitch(e) {
    const newFile = e.target.value;
    setSelectedFile(newFile);
    setShow("");
    setLoadingCode(true);

    try {
      const filePath = getFilePath(newFile);

      const res = await fetch(apiPath.codeviewer, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dir: filePath }),
      });

      const data = await res.json();
      setShow(data.fileText);
      console.log("response:", data);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoadingCode(false);
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow flex flex-col flex-1">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold">Code Viewer</h2>

        {loadingFiles ? (
          <span>Loading files...</span>
        ) : (
          <select
            value={selectedFile}
            onChange={whenSwitch}
            className="border rounded-xl p-2"
          >
            {listFile.map((item, index) => (
              <option key={index} value={item}>
                {item}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="flex-1 min-h-0">
        <div
          className="bg-gray-900 text-gray-300 p-4 rounded-xl 
                    whitespace-pre font-mono text-sm
                    overflow-auto h-[450px] min-h-0"
        >
          {loadingCode ? (
            <span className="text-yellow-400">Loading code...</span>
          ) : (
            <>
              <span className="text-green-400">// Showing: {selectedFile}</span>
              {"\n"}
              <span className="text-blue-400">// Code below: </span>
              {"\n\n"}
              {show}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
