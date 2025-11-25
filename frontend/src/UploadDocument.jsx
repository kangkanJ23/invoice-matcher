import React, { useState, useEffect } from "react";
import API from "./api";

export default function UploadDocument({ defaultCompanyId = "" }) {
  const [companyId, setCompanyId] = useState(defaultCompanyId || "");
  const [docType, setDocType] = useState("PO");
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultCompanyId) setCompanyId(defaultCompanyId);
  }, [defaultCompanyId]);

  const upload = async () => {
    if (!file) return alert("Choose a file");
    if (!companyId) return alert("Enter company ID (create company first)");

    const formData = new FormData();
    formData.append("company_id", companyId);
    formData.append("doc_type", docType);
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await API.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResponse(res.data);
      alert("Uploaded. Document ID: " + res?.data?.data?.document_id);
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Upload Document</h2>

      <input className="w-full border p-2 mb-2" placeholder="Company ID" value={companyId} onChange={e => setCompanyId(e.target.value)} />

      <select className="w-full border p-2 mb-2" value={docType} onChange={e => setDocType(e.target.value)}>
        <option value="PO">PO</option>
        <option value="INVOICE">INVOICE</option>
        <option value="DELIVERY">DELIVERY</option>
      </select>

      <input className="w-full mb-2" type="file" onChange={e => setFile(e.target.files[0])} />

      <button onClick={upload} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded w-full">
        {loading ? "Uploading..." : "Upload"}
      </button>

      {response && (
        <pre className="mt-3 bg-gray-100 p-2 rounded max-h-64 overflow-auto">{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}
