import React, { useState } from "react";
import API from "./api";

export default function MatchForm({ companyId }) {
  const [poId, setPoId] = useState("");
  const [invoiceId, setInvoiceId] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runMatch = async () => {
    if (!companyId) return alert("Company ID required");
    if (!poId || !invoiceId) return alert("Provide both PO ID and Invoice ID");

    setLoading(true);
    try {
      const res = await API.post("/match", { company_id: Number(companyId), po_id: Number(poId), invoice_id: Number(invoiceId) });
      setResult(res.data.data);
    } catch (err) {
      console.error(err);
      alert("Match failed: " + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Run Match (PO ↔ Invoice)</h2>

      <input className="w-full border p-2 mb-2" placeholder="Company ID" value={companyId} readOnly />

      <input className="w-full border p-2 mb-2" placeholder="PO Document ID" value={poId} onChange={e => setPoId(e.target.value)} />
      <input className="w-full border p-2 mb-2" placeholder="Invoice Document ID" value={invoiceId} onChange={e => setInvoiceId(e.target.value)} />

      <button onClick={runMatch} disabled={loading} className="bg-indigo-600 text-white px-4 py-2 rounded w-full">
        {loading ? "Running..." : "Run Match"}
      </button>

      {result && (
        <div className="mt-3">
          <h3 className="font-semibold">Result</h3>
          <pre className="bg-gray-100 p-2 rounded max-h-60 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
          {result.report_path && (
            <div className="mt-2">
              <a href={`http://127.0.0.1:8000/${result.report_path}`} target="_blank" rel="noreferrer" className="text-blue-600 underline">Open Report</a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
