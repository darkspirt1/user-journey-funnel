import { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from "recharts";
import "./App.css";

const API = "http://localhost:8000/api";
const COLORS = ["#47c5ff", "#e8ff47", "#ff6b35", "#ff4757"];

export default function App() {
  const [funnel, setFunnel] = useState(null);
  const [insights, setInsights] = useState(null);
  const [segments, setSegments] = useState({});
  const [filters, setFilters] = useState({ device: "all", location: "all", source: "all", age_group: "all" });
  const [loading, setLoading] = useState(true);

  const fetchFunnel = async (f) => {
    const res = await axios.get(`${API}/funnel`, { params: f });
    setFunnel(res.data);
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        const [funnelRes, insightsRes, dev, src, loc, age] = await Promise.all([
          axios.get(`${API}/funnel`, { params: filters }),
          axios.get(`${API}/insights`),
          axios.get(`${API}/segments/device`),
          axios.get(`${API}/segments/source`),
          axios.get(`${API}/segments/location`),
          axios.get(`${API}/segments/age`),
        ]);
        setFunnel(funnelRes.data);
        setInsights(insightsRes.data);
        setSegments({
          device: dev.data.segments,
          source: src.data.segments,
          location: loc.data.segments,
          age: age.data.segments,
        });
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    init();
  }, []);

  const handleFilter = (key, val) => {
    const next = { ...filters, [key]: val };
    setFilters(next);
    fetchFunnel(next);
  };

  if (loading || !funnel || !insights) return <div className="loading">LOADING FUNNEL DATA...</div>;

  const purchases = funnel.stages.find(s => s.stage === "Purchase");
  const visits = funnel.stages.find(s => s.stage === "Visit");

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-left">
          <h1>User Journey <span>Funnel</span></h1>
          <p>Conversion analytics · drop-off analysis · segment insights</p>
        </div>
        <div className="live-badge"><span className="live-dot" />Live Data</div>
      </div>

      {/* Filters */}
      <div className="filters">
        {[
          { key: "device", label: "Device", opts: ["all", "mobile", "desktop"] },
          { key: "location", label: "Location", opts: ["all", "IN", "US", "EU", "APAC"] },
          { key: "source", label: "Source", opts: ["all", "organic", "paid", "referral", "social"] },
          { key: "age_group", label: "Age Group", opts: ["all", "18-24", "25-34", "35-44", "45+"] },
        ].map(f => (
          <div className="filter-group" key={f.key}>
            <label>{f.label}</label>
            <select value={filters[f.key]} onChange={e => handleFilter(f.key, e.target.value)}>
              {f.opts.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
        ))}
      </div>

      {/* KPIs — sourced from funnel so they update with filters */}
      <div className="kpi-row">
        <div className="kpi-card">
          <div className="kpi-label">Total Visitors</div>
          <div className="kpi-value">{visits.users.toLocaleString()}</div>
          <div className="kpi-sub">last 60 days</div>
        </div>
        <div className="kpi-card blue">
          <div className="kpi-label">Total Purchases</div>
          <div className="kpi-value">{purchases.users}</div>
          <div className="kpi-sub">completed orders</div>
        </div>
        <div className="kpi-card orange">
          <div className="kpi-label">Overall Conversion</div>
          <div className="kpi-value">{funnel.overall_conversion_pct}%</div>
          <div className="kpi-sub">visit → purchase</div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-label">Biggest Leak</div>
          <div className="kpi-value" style={{ fontSize: "1rem", marginTop: 6 }}>{funnel.biggest_leakage}</div>
          <div className="kpi-sub">{purchases && `${funnel.stages.find(s => s.stage === "Purchase").drop_pct}% lost at checkout`}</div>
        </div>
      </div>

      {/* Funnel + Drop-off */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title"><span>▌</span>Conversion Funnel</div>
          {funnel.stages.map((stage) => (
            <div className="funnel-stage" key={stage.stage}>
              <div className="funnel-stage-header">
                <span className="funnel-stage-name">{stage.stage}</span>
                <div className="funnel-stage-meta">
                  <span>{stage.users.toLocaleString()} users</span>
                  <span>{stage.pct_of_total}%</span>
                  {stage.drop_pct !== null && (
                    <span className="drop-badge">-{stage.drop_pct}%</span>
                  )}
                </div>
              </div>
              <div className="funnel-bar-bg">
                <div className="funnel-bar-fill" style={{ width: `${stage.pct_of_total}%` }} />
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-title"><span>▌</span>Drop-off at Each Transition</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={Object.entries(insights.drop_offs).map(([k, v]) => ({ stage: k, drop: v }))}>
              <XAxis dataKey="stage" tick={{ fill: "#6b6b80", fontSize: 10, fontFamily: "DM Mono" }} />
              <YAxis tick={{ fill: "#6b6b80", fontSize: 11, fontFamily: "DM Mono" }} unit="%" />
              <Tooltip contentStyle={{ background: "#1e1e2e", border: "1px solid #e8ff47", borderRadius: 8, fontFamily: "DM Mono", fontSize: 12, color: "#f0f0f5" }} formatter={v => [`${v}%`, "Conversion"]} />
              <Bar dataKey="drop" radius={[4, 4, 0, 0]} fill="#ff4757" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Device + Source */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title"><span>▌</span>Device Segments</div>
          <table className="seg-table">
            <thead><tr><th>Device</th><th>Visits</th><th>Signup%</th><th>Cart%</th><th>Overall</th></tr></thead>
            <tbody>
              {segments.device?.map(s => (
                <tr key={s.segment}>
                  <td style={{ fontWeight: 600 }}>{s.segment}</td>
                  <td>{s.visits.toLocaleString()}</td>
                  <td>{s.signup_rate}%</td>
                  <td>{s.cart_rate}%</td>
                  <td><span className={`seg-badge ${s.overall_conversion > 5 ? "high" : s.overall_conversion > 3 ? "mid" : "low"}`}>{s.overall_conversion}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="card-title"><span>▌</span>Traffic Source Segments</div>
          <table className="seg-table">
            <thead><tr><th>Source</th><th>Visits</th><th>Signup%</th><th>Cart%</th><th>Overall</th></tr></thead>
            <tbody>
              {segments.source?.map(s => (
                <tr key={s.segment}>
                  <td style={{ fontWeight: 600 }}>{s.segment}</td>
                  <td>{s.visits.toLocaleString()}</td>
                  <td>{s.signup_rate}%</td>
                  <td>{s.cart_rate}%</td>
                  <td><span className={`seg-badge ${s.overall_conversion > 5 ? "high" : s.overall_conversion > 3 ? "mid" : "low"}`}>{s.overall_conversion}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Location + Age */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title"><span>▌</span>Location Conversion</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={segments.location?.map(s => ({ name: s.segment, conv: s.overall_conversion }))}>
              <XAxis dataKey="name" tick={{ fill: "#6b6b80", fontSize: 11, fontFamily: "DM Mono" }} />
              <YAxis tick={{ fill: "#6b6b80", fontSize: 11, fontFamily: "DM Mono" }} unit="%" />
              <Tooltip contentStyle={{ background: "#1e1e2e", border: "1px solid #e8ff47", borderRadius: 8, fontFamily: "DM Mono", fontSize: 12, color: "#f0f0f5" }} formatter={v => [`${v}%`, "Conversion"]} />
              <Bar dataKey="conv" radius={[4, 4, 0, 0]}>
                {segments.location?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title"><span>▌</span>Age Group Segments</div>
          <table className="seg-table">
            <thead><tr><th>Age</th><th>Visits</th><th>Signup%</th><th>Cart%</th><th>Overall</th></tr></thead>
            <tbody>
              {segments.age?.map(s => (
                <tr key={s.segment}>
                  <td style={{ fontWeight: 600 }}>{s.segment}</td>
                  <td>{s.visits.toLocaleString()}</td>
                  <td>{s.signup_rate}%</td>
                  <td>{s.cart_rate}%</td>
                  <td><span className={`seg-badge ${s.overall_conversion > 5 ? "high" : s.overall_conversion > 3 ? "mid" : "low"}`}>{s.overall_conversion}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Avg Time */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title"><span>▌</span>Avg Time Spent Per Step (seconds)</div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={Object.entries(insights.avg_time_per_step).map(([k, v]) => ({ step: k.replace("_", " "), seconds: v }))}>
            <XAxis dataKey="step" tick={{ fill: "#6b6b80", fontSize: 11, fontFamily: "DM Mono" }} />
            <YAxis tick={{ fill: "#6b6b80", fontSize: 11, fontFamily: "DM Mono" }} />
            <Tooltip contentStyle={{ background: "#1e1e2e", border: "1px solid #e8ff47", borderRadius: 8, fontFamily: "DM Mono", fontSize: 12, color: "#f0f0f5" }} formatter={v => [`${v}%`, "Conversion"]} />
            <Bar dataKey="seconds" radius={[4, 4, 0, 0]}>
              {Object.keys(insights.avg_time_per_step).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recommendations */}
      <div className="card">
        <div className="card-title"><span>▌</span>Fix Recommendations</div>
        {insights.recommendations.map((r, i) => (
          <div className="rec-item" key={i}>
            <div className={`rec-impact ${r.impact}`}>{r.impact}</div>
            <div>
              <div className="rec-issue">{r.issue}</div>
              <div className="rec-fix">{r.fix}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}