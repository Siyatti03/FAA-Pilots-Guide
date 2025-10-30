import React from "react";

export default function App() {
  return (
    <>
      <style>{`
        :root{
          --topBar:#1d2631;
          --brandBlue:#243e90;
          --navChip:#eef2f6;
          --divider:#eceff3;
          --sidebarItem:#f3f5f8;
          --panelRight:#dde2e9;
          --cardWhite:#ffffff;
          --blueA:#3B82F6;   /* primary blue */
          --blueB:#2563EB;   /* secondary blue */
          --rowBg:#eff2f5;
          --rowBar:#cfd6de;
          --rowSquare:#bcc7df;
          --page:#ffffff;
        }
        *{box-sizing:border-box}
        html,body,#root{height:100%}
        body{margin:0;background:var(--page);color:#111;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
        .container{max-width:1120px;margin:0 auto}
        .topbar{background:var(--topBar);height:20px}
        .row{display:flex;align-items:center}
        .space-x-14{gap:56px}
        .space-x-6{gap:24px}
        .pxy{padding:24px 24px}
        .px{padding-left:24px;padding-right:24px}
        .divider{background:var(--divider);height:36px}
        .brand{width:224px;height:36px;background:var(--brandBlue);border-radius:3px}
        .chip{width:112px;height:24px;background:var(--navChip);border-radius:3px}
        .chip-long{width:160px;height:24px;background:var(--navChip);border-radius:3px}
        .search{width:256px;height:36px;background:var(--navChip);border-radius:3px}
        .grid{display:grid;grid-template-columns:1fr;gap:24px}
        .grid-12{display:grid;grid-template-columns:repeat(12,1fr);gap:24px}
        .col-3{grid-column:span 3}
        .col-4{grid-column:span 4}
        .col-8{grid-column:span 8}
        .col-9{grid-column:span 9}
        .sidebar-item{height:40px;background:var(--sidebarItem);border-radius:3px}
        .card{height:300px;background:var(--cardWhite);border-radius:3px}
        .rpanel{height:300px;background:var(--panelRight);border-radius:3px}
        .btnA,.btnB{height:40px;width:160px;border-radius:3px}
        .btnA{background:var(--blueA)}
        .btnB{background:var(--blueB)}
        .rowItem{display:flex;align-items:center;justify-content:space-between;background:var(--rowBg);border-radius:3px;padding:16px}
        .rowBar{height:16px;width:256px;background:var(--rowBar);border-radius:3px}
        .rowSquare{height:28px;width:28px;background:var(--rowSquare);border-radius:3px}
        .h-24{height:24px}
        .mt-6{margin-top:24px}

        @media (max-width: 900px){
          .hide-md{display:none}
          .grid-12{grid-template-columns:1fr}
          .col-3,.col-4,.col-8,.col-9{grid-column:span 1}
        }
      `}</style>

      {/* Top dark bar */}
      <div className="topbar" />

      {/* Brand + chips + search */}
      <div className="container">
        <div className="row pxy space-x-14">
          <div className="brand" />
          <div className="row hide-md space-x-6">
            <div className="chip" />
            <div className="chip" />
            <div className="chip" />
            <div className="chip" />
            <div className="chip" />
            <div className="chip-long" />
          </div>
          <div className="search hide-md" style={{ marginLeft: "auto" }} />
        </div>
      </div>

      {/* Thin divider band */}
      <div className="divider" />

      {/* Main content area */}
      <div className="container px">
        <div className="grid-12 mt-6">
          {/* Left sidebar list */}
          <aside className="col-3">
            <div className="grid" style={{ gap: 16 }}>
              {Array.from({ length: 10 }).map((_, i) => (
                <div className="sidebar-item" key={i} />
              ))}
            </div>
          </aside>

          {/* Center + Right */}
          <section className="col-9">
            <div className="grid-12">
              {/* Center white card + buttons */}
              <div className="col-8">
                <div className="card" />
                <div className="row mt-6 space-x-6">
                  <div className="btnA" />
                  <div className="btnB" />
                </div>
              </div>

              {/* Right panel */}
              <div className="col-4">
                <div className="rpanel" />
              </div>
            </div>

            {/* Four rows */}
            <div className="grid mt-6" style={{ gap: 16 }}>
              {Array.from({ length: 4 }).map((_, i) => (
                <div className="rowItem" key={i}>
                  <div className="rowBar" />
                  <div className="rowSquare" />
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="h-24" />
      </div>
    </>
  );
}
