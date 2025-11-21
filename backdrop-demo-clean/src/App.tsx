import React from "react";

export default function App() {
  return (
    <>
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
