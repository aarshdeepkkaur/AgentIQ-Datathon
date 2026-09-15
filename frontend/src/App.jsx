import { useState } from "react"; 
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  CloudRain,
  Filter,
  Leaf,
  MapPin,
  Truck,
  Wheat,
} from "lucide-react";
import AIAgentPanel from "./components/AIAgentPanel";

const kpis = [
  {
    title: "Average Market Price",
    value: "₹2,485",
    change: "+8.4%",
    positive: true,
    icon: Wheat,
  },
  {
    title: "Average MSP",
    value: "₹2,275",
    change: "+4.2%",
    positive: true,
    icon: Leaf,
  },
  {
    title: "Price Gap",
    value: "₹210",
    change: "+12.6%",
    positive: true,
    icon: Activity,
  },
  {
    title: "Avg Transit Time",
    value: "7.8 hrs",
    change: "-5.3%",
    positive: true,
    icon: Truck,
  },
];

const mandiData = [
  { name: "Ludhiana", price: 2780, msp: 2275, risk: "Low" },
  { name: "Amritsar", price: 2520, msp: 2275, risk: "Medium" },
  { name: "Patiala", price: 2190, msp: 2275, risk: "High" },
  { name: "Jalandhar", price: 2640, msp: 2275, risk: "Low" },
  { name: "Bathinda", price: 2310, msp: 2275, risk: "Medium" },
];

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Wheat size={24} />
          </div>

          <div>
            <h2>AgentIQ</h2>
            <p>Supply Intelligence</p>
          </div>
        </div>

        <nav className="nav-menu">
          <a className="nav-item active" href="#">
            <Activity size={19} />
            Overview
          </a>

          <a className="nav-item" href="#">
            <MapPin size={19} />
            Mandi Analytics
          </a>

          <a className="nav-item" href="#">
            <Truck size={19} />
            Logistics
          </a>

          <a className="nav-item" href="#">
            <CloudRain size={19} />
            Weather Impact
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>
          <div>
            <strong>System Online</strong>
            <p>Data pipeline active</p>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">AGENTIQ DATATHON · TRACK 3</p>
            <h1>Mandi-to-Market Optimizer</h1>
            <p className="subtitle">
              Monitor agricultural prices, logistics, and supply-chain risks.
            </p>
          </div>

          <div className="topbar-right">
            <span className="live-badge">
              <span className="live-dot"></span>
              Live Monitoring
            </span>
            <div className="profile">AK</div>
          </div>
        </header>

        <section className="filters-panel">
          <div className="filter-heading">
            <Filter size={18} />
            <strong>Market Filters</strong>
          </div>

          <select defaultValue="All Crops">
            <option>All Crops</option>
            <option>Wheat</option>
            <option>Rice</option>
            <option>Maize</option>
          </select>

          <select defaultValue="All Mandis">
            <option>All Mandis</option>
            <option>Ludhiana</option>
            <option>Amritsar</option>
            <option>Patiala</option>
          </select>

          <select defaultValue="Last 30 Days">
            <option>Last 30 Days</option>
            <option>Last 7 Days</option>
            <option>Last 90 Days</option>
          </select>

          <button className="filter-button">Apply Filters</button>
        </section>

        <section className="kpi-grid">
          {kpis.map((kpi) => {
            const Icon = kpi.icon;

            return (
              <div className="kpi-card" key={kpi.title}>
                <div className="kpi-top">
                  <span>{kpi.title}</span>
                  <div className="kpi-icon">
                    <Icon size={20} />
                  </div>
                </div>

                <h2>{kpi.value}</h2>

                <div className="kpi-change">
                  <ArrowUpRight size={16} />
                  {kpi.change}
                  <span>vs previous period</span>
                </div>
              </div>
            );
          })}
        </section>

        <section className="content-grid">
          <div className="panel large-panel">
            <div className="panel-header">
              <div>
                <h3>Market Price vs MSP</h3>
                <p>Current market price comparison across major mandis.</p>
              </div>

              <span className="panel-tag">Wheat · ₹/Quintal</span>
            </div>

            <div className="chart-area">
              {mandiData.map((item) => (
                <div className="bar-row" key={item.name}>
                  <div className="bar-label">
                    <span>{item.name}</span>
                    <strong>₹{item.price}</strong>
                  </div>

                  <div className="bar-track">
                    <div
                      className="market-bar"
                      style={{
                        width: `${(item.price / 3000) * 100}%`,
                      }}
                    ></div>

                    <div
                      className="msp-marker"
                      style={{
                        left: `${(item.msp / 3000) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
              ))}

              <div className="chart-legend">
                <span>
                  <i className="legend-market"></i>
                  Market Price
                </span>

                <span>
                  <i className="legend-msp"></i>
                  MSP Reference
                </span>
              </div>
            </div>
          </div>

          <div className="panel risk-panel">
            <div className="panel-header">
              <div>
                <h3>Supply Chain Risk</h3>
                <p>Overall operational health.</p>
              </div>
            </div>

            <div className="risk-score">
              <div className="score-circle">
                <strong>72</strong>
                <span>/100</span>
              </div>

              <div>
                <span className="risk-label">Moderate Risk</span>
                <p>Some mandis need attention.</p>
              </div>
            </div>

            <div className="risk-line">
              <span>Low Risk</span>
              <strong>2 Mandis</strong>
            </div>

            <div className="risk-line">
              <span>Medium Risk</span>
              <strong>2 Mandis</strong>
            </div>

            <div className="risk-line">
              <span>High Risk</span>
              <strong className="danger-text">1 Mandi</strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>Mandi Performance</h3>
              <p>Price, MSP, and operational risk overview.</p>
            </div>

            <button className="outline-button">Export Report</button>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Mandi</th>
                  <th>Market Price</th>
                  <th>MSP</th>
                  <th>Price Gap</th>
                  <th>Risk Status</th>
                </tr>
              </thead>

              <tbody>
                {mandiData.map((item) => {
                  const gap = item.price - item.msp;

                  return (
                    <tr key={item.name}>
                      <td>
                        <div className="mandi-name">
                          <MapPin size={16} />
                          {item.name}
                        </div>
                      </td>

                      <td>₹{item.price}</td>
                      <td>₹{item.msp}</td>
                      <td className={gap >= 0 ? "positive-text" : "danger-text"}>
                        {gap >= 0 ? "+" : ""}
                        ₹{gap}
                      </td>

                      <td>
                        <span className={`risk-badge ${item.risk.toLowerCase()}`}>
                          {item.risk}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        <section className="ai-banner">
          <div className="ai-symbol">✦</div>

          <div>
            <h3>Ask AgentIQ</h3>
            <p>
              Ask questions in natural language and generate supply-chain
              insights automatically.
            </p>
          </div>

          <button className="ai-button">Open AI Agent →</button>
        </section>
        <AIAgentPanel />
      </main>
    </div>
  );
}

export default App;