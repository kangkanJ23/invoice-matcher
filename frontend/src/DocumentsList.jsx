import React, { useState, useEffect } from "react";
import API from "./api";

export default function DocumentsList({ companyId }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [parsed, setParsed] = useState(null);

  useEffect(() => {
    if (companyId) loadDocs();
    else setDocs([]);
    // eslint-disable-next-line
  }, [companyId]);

  const loadDocs = async () => {
    setLoading(true);
    try {
      // There's no dedicated list API; we fetch by scanning DB via /api/docs? (we don't have that)
      // So we will fetch companies -> (not ideal). Instead, use a simple approach: maintain uploaded doc IDs in response.
      // For now, try to fetch all docs by calling DB via /api/documents/{id} is not feasible without IDs.
      // We'll provide a simple workaround: attempt to call /api/companies to get nothing. Better approach: ask backend for a list route.
      // But to keep moving, we will poll an assumed endpoint: GET /api/documents?company_id=ID (you can add it to backend).
      const res = await API.get("/documents", { params: { company_id: companyId } });
      setDocs(res.data.data.documents || []);
    } catch (err) {
      // If backend doesn't have this route yet, show uploaded docs from manual upload (user can use Swagger to check)
      setDocs([]);
      console.warn("Could not fetch documents list. Add GET /api/documents?company_id= to backend for full list.");
    } finally {
      setLoading(false);
    }
  };

  const getDocument = async (docId) => {
    try {
      const res = await API.get(`/documents/${docId}`);
      setSelectedDoc(res.data.data);
      setParsed(res.data.data.parsed_json ? JSON.parse(res.data.data.parsed_json) : null);
    } catch (err) {
      alert("Failed to load document");
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow mt-4">
      <h2 className="font-semibold mb-2">Documents</h2>

      {!companyId && <div className="text-sm text-gray-500">Create or select a company to see documents.</div>}

      {companyId && (
        <>
          <div className="flex gap-2 items-center mb-2">
            <button onClick={loadDocs} className="bg-gray-200 px-3 py-1 rounded">Refresh</button>
            <div className="text-sm text-gray-600">company_id: {companyId}</div>
          </div>

          {loading && <div>Loading...</div>}

          {!loading && docs.length === 0 && <div className="text-sm text-gray-500">No documents found. Use Upload to add documents.</div>}

          <ul className="space-y-2">
            {docs.map(d => (
              <li key={d.id} className="border rounded p-2 flex justify-between items-center">
                <div>
                  <div className="font-medium">{d.doc_type}</div>
                  <div className="text-sm text-gray-600">ID: {d.id} — {d.filename}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => getDocument(d.id)} className="bg-blue-500 text-white px-3 py-1 rounded">View</button>
                </div>
              </li>
            ))}
          </ul>

          {selectedDoc && (
            <div className="mt-4 p-3 border rounded bg-gray-50">
              <h3 className="font-semibold">Document {selectedDoc.id}</h3>
              <div className="text-sm"><strong>Type:</strong> {selectedDoc.doc_type}</div>
              <div className="text-sm"><strong>Filename:</strong> {selectedDoc.filename}</div>
              <div className="mt-2">
                <h4 className="font-semibold">Parsed JSON</h4>
                <pre className="bg-white p-2 rounded max-h-56 overflow-auto">{selectedDoc.parsed_json || selectedDoc.ocr_text || "No parsed data"}</pre>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
