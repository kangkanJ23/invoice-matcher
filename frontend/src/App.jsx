import React, { useState } from "react";
import CompanyForm from "./CompanyForm";
import UploadDocument from "./UploadDocument";
import DocumentsList from "./DocumentsList";
import MatchForm from "./MatchForm";

export default function App() {
  const [companyId, setCompanyId] = useState("");

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto py-6 px-4">
          <h1 className="text-2xl font-bold">Invoice Matcher — Demo</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-4">
        <CompanyForm onCreated={(id) => setCompanyId(String(id))} />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UploadDocument defaultCompanyId={companyId} />
          <MatchForm companyId={companyId} />
        </div>

        <div className="mt-6">
          <DocumentsList companyId={companyId} />
        </div>
      </main>
    </div>
  );
}

