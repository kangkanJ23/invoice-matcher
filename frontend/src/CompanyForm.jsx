import React, { useState } from "react";
import API from "./api";

export default function CompanyForm({ onCreated }) {
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!name) return alert("Company name required");
    setLoading(true);
    try {
      // API expects query/form params; using Axios params style for GET-like form
      const res = await API.post("/companies", null, {
        params: { name, contact_person: contact, email },
      });
      const id = res?.data?.data?.company_id;
      alert("Company created: id=" + id);
      setName(""); setContact(""); setEmail("");
      if (onCreated && id) onCreated(id);
    } catch (err) {
      console.error(err);
      alert("Failed to create company: " + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Create Company</h2>
      <input className="w-full border p-2 mb-2" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <input className="w-full border p-2 mb-2" placeholder="Contact person" value={contact} onChange={e => setContact(e.target.value)} />
      <input className="w-full border p-2 mb-2" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <div className="flex gap-2">
        <button onClick={submit} disabled={loading} className="bg-green-600 text-white px-3 py-2 rounded">
          {loading ? "Creating..." : "Create"}
        </button>
      </div>
    </div>
  );
}
