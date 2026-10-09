async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString("en-IN") : "—";
}

async function loadDashboard() {
  try {
    const [summary, overdue, popular, categories] = await Promise.all([
      getJSON("/api/dashboard/summary"),
      getJSON("/api/loans/overdue"),
      getJSON("/api/dashboard/popular-books"),
      getJSON("/api/dashboard/categories"),
    ]);

    document.getElementById("titleCount").textContent = summary.title_count;
    document.getElementById("totalCopies").textContent = summary.total_copies;
    document.getElementById("availableCopies").textContent =
      summary.available_copies;
    document.getElementById("activeMembers").textContent =
      summary.active_members;
    document.getElementById("activeLoans").textContent = summary.active_loans;
    document.getElementById("overdueLoans").textContent = summary.overdue_loans;

    document.getElementById("overdueTable").innerHTML = overdue.length
      ? overdue
          .slice(0, 8)
          .map(
            (row) => `
          <tr>
            <td><strong>${escapeHTML(row.book_title)}</strong></td>
            <td>${escapeHTML(row.member_name)}</td>
            <td>${formatDate(row.due_date)}</td>
            <td><span class="badge overdue">${row.days_overdue} days</span></td>
            <td class="danger-text">${money(row.calculated_fine)}</td>
          </tr>`,
          )
          .join("")
      : `<tr><td colspan="5" class="empty">No overdue books 🎉</td></tr>`;

    document.getElementById("popularList").innerHTML = popular.length
      ? popular
          .map(
            (row, i) => `
          <div class="rank-row">
            <span>${i + 1}. ${escapeHTML(row.title)}</span>
            <small>${row.times_borrowed} loans</small>
          </div>`,
          )
          .join("")
      : `<div class="empty">No loan history yet.</div>`;

    document.getElementById("categoryGrid").innerHTML = categories
      .map(
        (row) => `
      <div class="category-card">
        <strong>${row.title_count}</strong>
        <span>${escapeHTML(row.category)} · ${row.total_copies} copies</span>
      </div>`,
      )
      .join("");
  } catch (error) {
    console.error(error);
    document.getElementById("overdueTable").innerHTML =
      `<tr><td colspan="5" class="empty">Could not connect to the API.</td></tr>`;
  }
}

function escapeHTML(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[c],
  );
}

loadDashboard();
