import { useEffect, useState } from "react";
import axios from "axios";
import {
  Sun, LayoutDashboard, Plus, Search, LogOut, Upload, FileText,
  AlertCircle, RefreshCw, Download, ArrowLeft, CheckCircle2
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";
const money = (value) =>
  Number(value || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });

export default function App() {
  const [token, setToken] = useState(sessionStorage.getItem("token") || "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [leads, setLeads] = useState([]);
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [billId, setBillId] = useState(null);
  const [billConfirmed, setBillConfirmed] = useState(false);
  const [quote, setQuote] = useState(null);
  const [project, setProject] = useState(null);

  const [leadForm, setLeadForm] = useState({
    name: "", phone: "", owner_or_tenant: "owner", roof_type: "RCC",
    roof_area: "", monthly_bill: "", pincode: "", language: "en", consent: true
  });
  const [billForm, setBillForm] = useState({
    consumer_no: "", tariff: "Residential", sanctioned_load: "", monthly_units: ""
  });

  const headers = { Authorization: `Bearer ${token}` };

  async function login(e) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const body = new URLSearchParams();
      body.append("username", email.trim());
      body.append("password", password);
      const res = await axios.post(`${API}/api/auth/login`, body, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });
      sessionStorage.setItem("token", res.data.access_token);
      setToken(res.data.access_token);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not connect to the server.");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    sessionStorage.removeItem("token");
    setToken("");
    setLeads([]);
    setSelected(null);
    setQuote(null);
    setProject(null);
    setPage("dashboard");
  }

  async function loadLeads() {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/api/leads`, { headers });
      setLeads(res.data);
    } catch (err) {
      if (err.response?.status === 401) logout();
      else setMessage(err.response?.data?.detail || "Could not load enquiries.");
    }
  }

  useEffect(() => {
    if (token) loadLeads();
  }, [token]);

  async function openLead(lead) {
    setBusy(true);
    setMessage("");
    setQuote(null);
    setProject(null);
    setBillId(null);
    setBillConfirmed(false);
    try {
      const res = await axios.get(`${API}/api/leads/${lead.id}`, { headers });
      setSelected(res.data);
      setPage("detail");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not open enquiry.");
    } finally {
      setBusy(false);
    }
  }

  async function createLead(e) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const payload = {
        ...leadForm,
        roof_area: Number(leadForm.roof_area),
        monthly_bill: Number(leadForm.monthly_bill),
        consent: leadForm.consent
      };
      const res = await axios.post(`${API}/api/leads`, payload);
      setMessage(`Enquiry created successfully. Reference #${res.data.lead_id}.`);
      setLeadForm({
        name: "", phone: "", owner_or_tenant: "owner", roof_type: "RCC",
        roof_area: "", monthly_bill: "", pincode: "", language: "en", consent: true
      });
      await loadLeads();
      const created = await axios.get(`${API}/api/leads/${res.data.lead_id}`, { headers });
      setSelected(created.data);
      setPage("detail");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Please check the enquiry details.");
    } finally {
      setBusy(false);
    }
  }

  async function uploadBill(e) {
    e.preventDefault();
    const file = e.currentTarget.elements.bill?.files?.[0];
    if (!file || !selected) {
      setMessage("Choose an electricity bill image first.");
      return;
    }
    setBusy(true);
    setMessage("");
    setQuote(null);
    setBillConfirmed(false);
    const data = new FormData();
    data.append("file", file);
    try {
      const res = await axios.post(
        `${API}/api/leads/${selected.id}/bill/upload`, data, { headers }
      );
      setBillId(res.data.bill_id);
      const extracted = res.data.extracted_fields || {};
      setBillForm({
        consumer_no: extracted.consumer_no?.value || "",
        tariff: extracted.tariff?.value || "Residential",
        sanctioned_load: extracted.sanctioned_load?.value ?? "",
        monthly_units: extracted.monthly_units?.value ?? ""
      });
      setMessage(
        res.data.status === "extracted"
          ? "Bill uploaded. Review the extracted details, then confirm."
          : "Bill saved. Enter the bill details manually, then confirm."
      );
    } catch (err) {
      setMessage(err.response?.data?.detail || "Bill upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmBill(e) {
    e.preventDefault();
    if (!billId) return;
    if (!billForm.monthly_units || Number(billForm.monthly_units) <= 0) {
      setMessage("Enter valid monthly units before confirming.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      await axios.put(`${API}/api/bills/${billId}/confirm`, {
        consumer_no: billForm.consumer_no || null,
        tariff: billForm.tariff || null,
        sanctioned_load: billForm.sanctioned_load !== ""
          ? Number(billForm.sanctioned_load) : null,
        monthly_units: Number(billForm.monthly_units)
      }, { headers });
      setBillConfirmed(true);
      setMessage("Bill confirmed. You can now generate the solar quotation.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Could not confirm bill details.");
    } finally {
      setBusy(false);
    }
  }

  async function generateQuote() {
    if (!selected || !billForm.monthly_units) return;
    setBusy(true);
    setMessage("");
    try {
      const res = await axios.post(
        `${API}/api/leads/${selected.id}/quote`,
        { monthly_units: Number(billForm.monthly_units) },
        { headers }
      );
      setQuote(res.data);
      setPage("quotation");
      await loadLeads();
      setMessage("Quotation generated successfully.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Could not generate quotation. Check that dated subsidy, price and tariff rules are configured.");
    } finally {
      setBusy(false);
    }
  }

  function downloadQuotePDF() {
    // Browser print dialog allows staff to choose "Save as PDF".
    window.print();
  }

  async function createProject() {
    if (!quote?.quote_id) return;
    setBusy(true);
    setMessage("");
    try {
      const res = await axios.post(`${API}/api/quotes/${quote.quote_id}/project`, {}, { headers });
      setProject(res.data);
      setMessage("Project created. Save the tracking link for the homeowner.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Could not create project. It may already exist for this quotation.");
    } finally {
      setBusy(false);
    }
  }

  const filtered = leads.filter((lead) =>
    `${lead.name || ""} ${lead.phone || ""} ${lead.pincode || ""}`
      .toLowerCase().includes(search.toLowerCase())
  );

  if (!token) {
    return (
      <main className="login-page">
        <section className="login-card">
          <div className="brand-mark"><Sun size={27} /></div>
          <p className="eyebrow">ROOFTOP SOLAR · VIDARBHA</p>
          <h1 style={{ color: "#17251f", opacity: 1 }}>Surya Setu</h1>
          <p className="muted">A simpler way to manage solar enquiries.</p>
          <form onSubmit={login} className="form-stack">
            <label>Email address<input type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} required /></label>
            <label>Password<input type="password" value={password}
              onChange={(e) => setPassword(e.target.value)} required /></label>
            {message && <p className="notice error">{message}</p>}
            <button className="primary full" disabled={busy}>
              {busy ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="login-foot">Staff access only</p>
        </section>
      </main>
    );
  }

  const q = quote?.quotation;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Sun size={23} /></div>
          <div><strong>Surya Setu</strong><small>Solar operations</small></div>
        </div>
        <p className="nav-label">WORKSPACE</p>
        <button className={`nav-item ${page === "dashboard" ? "active" : ""}`}
          onClick={() => { setPage("dashboard"); setSelected(null); setQuote(null); }}>
          <LayoutDashboard size={18} /> Overview
        </button>
        <button className={`nav-item ${page === "new" ? "active" : ""}`}
          onClick={() => { setPage("new"); setSelected(null); }}>
          <Plus size={18} /> Add a lead
        </button>
        <div className="sidebar-bottom">
          <div className="location-note"><span className="status-dot" /> Nagpur · Vidarbha</div>
          <button className="nav-item" onClick={logout}><LogOut size={18} /> Sign out</button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="eyebrow">SURYA SETU / STAFF</span>
            <h2>{page === "new" ? "New enquiry" : page === "quotation" ? "Quotation" : "Overview"}</h2>
          </div>
          <button className="icon-button" onClick={loadLeads} title="Refresh enquiries">
            <RefreshCw size={17} />
          </button>
        </header>

        {message && (
          <div className="notice">
            <AlertCircle size={17} /><span>{message}</span>
            <button onClick={() => setMessage("")}>×</button>
          </div>
        )}

        {page === "dashboard" && !selected && (
          <>
            <section className="welcome-row">
              <div><p className="eyebrow">LEAD MANAGEMENT</p>
                <h1>Good work starts with a conversation.</h1>
                <p className="muted">Keep track of enquiries and move each home closer to solar.</p>
              </div>
              <button className="primary" onClick={() => setPage("new")}><Plus size={17} /> Add lead</button>
            </section>
            <section className="stats-row">
              <div className="stat-card"><span>Total enquiries</span><strong>{leads.length}</strong><small>All recorded leads</small></div>
              <div className="stat-card"><span>High priority</span><strong>{leads.filter(x => x.score === "High").length}</strong><small>Suitable for a site visit</small></div>
              <div className="stat-card"><span>Follow-up needed</span><strong>{leads.filter(x => x.next_step).length}</strong><small>Review next steps</small></div>
            </section>
            <section className="panel">
              <div className="panel-heading">
                <div><h3>Recent enquiries</h3><p className="muted">Your current lead pipeline</p></div>
                <div className="search-box"><Search size={16} /><input placeholder="Search name or phone"
                  value={search} onChange={e => setSearch(e.target.value)} /></div>
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Customer</th><th>Phone</th><th>Priority</th><th>Monthly bill</th><th /></tr></thead>
                  <tbody>
                    {filtered.map(lead => (
                      <tr key={lead.id}>
                        <td><strong>{lead.name}</strong><small className="cell-sub">#{lead.id}</small></td>
                        <td>{lead.phone}</td>
                        <td><span className={`pill ${lead.score === "High" ? "green" : "neutral"}`}>{lead.score || "Pending"}</span></td>
                        <td>₹{money(lead.monthly_bill)}</td>
                        <td><button className="text-button" onClick={() => openLead(lead)}>Open →</button></td>
                      </tr>
                    ))}
                    {filtered.length === 0 && <tr><td colSpan="5" className="empty">No enquiries found. Add your first lead to get started.</td></tr>}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}

        {page === "new" && (
          <section className="panel form-panel">
            <div className="panel-heading"><div><h3>Register an enquiry</h3><p className="muted">A few details to help the team plan the next step.</p></div></div>
            <form onSubmit={createLead} className="form-grid">
              <label>Customer name<input value={leadForm.name} required onChange={e => setLeadForm({...leadForm, name:e.target.value})} /></label>
              <label>Mobile number<input value={leadForm.phone} maxLength="10" required onChange={e => setLeadForm({...leadForm, phone:e.target.value})} /></label>
              <label>Property ownership<select value={leadForm.owner_or_tenant} onChange={e => setLeadForm({...leadForm, owner_or_tenant:e.target.value})}><option value="owner">Owner</option><option value="tenant">Tenant</option></select></label>
              <label>Roof type<select value={leadForm.roof_type} onChange={e => setLeadForm({...leadForm, roof_type:e.target.value})}><option value="RCC">RCC</option><option value="Tin">Tin / metal</option><option value="Tiled">Tiled</option><option value="Other">Other</option></select></label>
              <label>Approx. roof area (sq. ft.)<input type="number" min="1" value={leadForm.roof_area} required onChange={e => setLeadForm({...leadForm, roof_area:e.target.value})} /></label>
              <label>Monthly electricity bill (₹)<input type="number" min="0" value={leadForm.monthly_bill} required onChange={e => setLeadForm({...leadForm, monthly_bill:e.target.value})} /></label>
              <label>Pincode<input value={leadForm.pincode} maxLength="6" required onChange={e => setLeadForm({...leadForm, pincode:e.target.value})} /></label>
              <label>Preferred language<select value={leadForm.language} onChange={e => setLeadForm({...leadForm, language:e.target.value})}><option value="en">English</option><option value="mr">Marathi</option><option value="hi">Hindi</option></select></label>
              <label className="check-label"><input type="checkbox" checked={leadForm.consent} onChange={e => setLeadForm({...leadForm, consent:e.target.checked})} required /> Customer has agreed to be contacted.</label>
              <div className="form-actions"><button type="button" className="secondary" onClick={() => setPage("dashboard")}>Cancel</button><button className="primary" disabled={busy}>{busy ? "Saving..." : "Save enquiry"}</button></div>
            </form>
          </section>
        )}

        {page === "detail" && selected && (
          <section className="panel">
            <button className="back-button" onClick={() => { setPage("dashboard"); setSelected(null); }}>← Back to enquiries</button>
            <div className="detail-heading">
              <div><p className="eyebrow">ENQUIRY #{selected.id}</p><h1>{selected.name}</h1><p className="muted">{selected.phone} · {selected.pincode}</p></div>
              <span className={`pill ${selected.score === "High" ? "green" : "neutral"}`}>{selected.score || "Pending"}</span>
            </div>
            <div className="detail-grid">
              <div><small>Property</small><strong>{selected.owner_or_tenant} · {selected.roof_type}</strong></div>
              <div><small>Monthly bill</small><strong>₹{money(selected.monthly_bill)}</strong></div>
              <div><small>Roof area</small><strong>{selected.roof_area} sq. ft.</strong></div>
              <div><small>Recommended next step</small><strong>{selected.next_step || "To be assessed"}</strong></div>
            </div>
            <div className="section-divider" />
            <h3>Electricity bill</h3>
            <p className="muted">Upload a bill image. If automatic extraction is unavailable, enter the details manually.</p>
            {!billConfirmed && (
              <>
                <form onSubmit={uploadBill} className="upload-form">
                  <label className="file-picker"><Upload size={18} /> Choose bill image<input name="bill" type="file" accept="image/jpeg,image/png,image/webp" required /></label>
                  <button className="primary" disabled={busy}>{busy ? "Uploading..." : "Upload bill"}</button>
                </form>
                {billId && (
                  <form onSubmit={confirmBill} className="manual-box">
                    <h4><FileText size={17} /> Review and confirm bill details</h4>
                    <div className="form-grid">
                      <label>Consumer number<input value={billForm.consumer_no} onChange={e => setBillForm({...billForm, consumer_no:e.target.value})} /></label>
                      <label>Tariff category<input value={billForm.tariff} onChange={e => setBillForm({...billForm, tariff:e.target.value})} /></label>
                      <label>Sanctioned load (kW)<input type="number" min="0" step="0.1" value={billForm.sanctioned_load} onChange={e => setBillForm({...billForm, sanctioned_load:e.target.value})} /></label>
                      <label>Monthly units (kWh)<input type="number" min="1" required value={billForm.monthly_units} onChange={e => setBillForm({...billForm, monthly_units:e.target.value})} /></label>
                    </div>
                    <button className="primary" disabled={busy}>{busy ? "Confirming..." : "Confirm bill details"}</button>
                  </form>
                )}
              </>
            )}
            {billConfirmed && (
              <div className="manual-box">
                <p><CheckCircle2 size={18} /> Bill details confirmed · {billForm.monthly_units} units/month</p>
                <button className="primary" onClick={generateQuote} disabled={busy}>{busy ? "Calculating..." : "Generate quotation"}</button>
              </div>
            )}
          </section>
        )}

        {page === "quotation" && selected && q && (
          <section className="panel quote-print">
            <button className="back-button no-print" onClick={() => setPage("detail")}><ArrowLeft size={16} /> Back to enquiry</button>
            <div className="quote-heading">
              <div><p className="eyebrow">SURYA SETU · ROOFTOP SOLAR</p><h1>Solar quotation estimate</h1><p>Prepared for {selected.name} · Enquiry #{selected.id}</p></div>
              <div className="brand-mark no-print"><Sun size={24} /></div>
            </div>
            <div className="quote-highlight">
              <span>Recommended system size</span><strong>{q.system_kw} kW</strong><small>Based on {q.monthly_units} monthly units</small>
            </div>
            <div className="quote-lines">
              <div><span>Estimated system price</span><strong>₹{money(q.system_price)}</strong></div>
              <div><span>Estimated government subsidy</span><strong>− ₹{money(q.subsidy)}</strong></div>
              <div className="quote-total"><span>Estimated net cost</span><strong>₹{money(q.net_cost)}</strong></div>
              <div><span>Estimated annual savings</span><strong>₹{money(q.estimated_yearly_savings)}</strong></div>
              <div><span>Indicative payback period</span><strong>{q.estimated_payback_years ? `${Number(q.estimated_payback_years).toFixed(1)} years` : "Not available"}</strong></div>
            </div>
            <p className="quote-disclaimer">{q.subsidy_note}</p>
            <ul className="quote-assumptions">{(q.assumptions || []).map((item, i) => <li key={i}>{item}</li>)}</ul>
            <div className="form-actions no-print">
              <button className="secondary" onClick={downloadQuotePDF}><Download size={16} /> Print / Save as PDF</button>
              <button className="primary" onClick={createProject} disabled={busy || !!project}>{project ? "Project created" : busy ? "Creating..." : "Create project"}</button>
            </div>
            {project && (
              <div className="manual-box no-print">
                <h4><CheckCircle2 size={17} /> Project created successfully</h4>
                <p>Tracking link for the homeowner:</p>
                <a href={`${window.location.origin}/status/${project.public_status_token}`} target="_blank" rel="noreferrer">
                  {`${window.location.origin}/status/${project.public_status_token}`}
                </a>
                <p className="muted">The public tracking page needs a frontend route to display the timeline; the backend status API is available.</p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
