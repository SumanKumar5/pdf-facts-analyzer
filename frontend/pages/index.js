import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [pointers, setPointers] = useState(
    "List all dates\nWho signed?\nTotal contract value?"
  );
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return alert("Select a PDF file first");
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    const pointerArray = pointers
      .split("\n")
      .map((p) => p.trim())
      .filter(Boolean);
    form.append("pointers", JSON.stringify(pointerArray));

    const res = await fetch("http://localhost:5000/api/extract", {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    setResult(data);
    setLoading(false);
  }

  return (
    <main style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>PDF Facts Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <br />
        <textarea
          rows={5}
          cols={50}
          value={pointers}
          onChange={(e) => setPointers(e.target.value)}
          style={{ marginTop: 10 }}
        />
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Submit"}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 30 }}>
          <h2>Results</h2>
          {result.pointers.map((p, i) => (
            <div key={i} className="result-box">
              <strong>Query:</strong> {p.query}
              {p.matches.length === 0 && <p>No matches found</p>}
              {p.matches.map((m, j) => (
                <div key={j} className="snippet">
                  <b>Page {m.page}:</b> {m.snippet}
                  <div style={{ color: "#8b949e", fontSize: 13 }}>
                    {m.rationale}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
