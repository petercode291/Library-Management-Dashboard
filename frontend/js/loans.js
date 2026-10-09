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

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString("en-IN") : "—";
}

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

async function loadSelectors() {
  const [booksResponse, membersResponse] = await Promise.all([
    fetch("/api/books"),
    fetch("/api/members"),
  ]);

  const books = await booksResponse.json();
  const members = await membersResponse.json();

  const available = books.filter((book) => book.available_copies > 0);
  document.getElementById("bookSelect").innerHTML = available.length
    ? available
        .map(
          (book) =>
            `<option value="${book.book_id}">${escapeHTML(book.title)} (${book.available_copies} available)</option>`,
        )
        .join("")
    : `<option value="">No books available</option>`;

  const activeMembers = members.filter((member) => member.status === "Active");
  document.getElementById("memberSelect").innerHTML = activeMembers.length
    ? activeMembers
        .map(
          (member) =>
            `<option value="${member.member_id}">${escapeHTML(member.first_name)} ${escapeHTML(member.last_name)} (${escapeHTML(member.member_code)})</option>`,
        )
        .join("")
    : `<option value="">No active members</option>`;
}

async function loadLoans() {
  const response = await fetch("/api/loans?active_only=true");
  const loans = await response.json();

  document.getElementById("loansTable").innerHTML = loans.length
    ? loans
        .map(
          (loan) => `
      <tr>
        <td><strong>${escapeHTML(loan.book_title)}</strong></td>
        <td>${escapeHTML(loan.member_name)}</td>
        <td>${formatDate(loan.issue_date)}</td>
        <td>${formatDate(loan.due_date)}</td>
        <td><span class="badge ${loan.status.toLowerCase()}">${loan.status}</span></td>
        <td>${money(loan.fine)}</td>
        <td><button class="action-button" onclick="returnBook(${loan.loan_id})">Return</button></td>
      </tr>`,
        )
        .join("")
    : `<tr><td colspan="7" class="empty">No active loans.</td></tr>`;

  const overdueResponse = await fetch("/api/loans/overdue");
  const overdue = await overdueResponse.json();

  document.getElementById("overdueTable").innerHTML = overdue.length
    ? overdue
        .map(
          (row) => `
      <tr>
        <td>${escapeHTML(row.book_title)}</td>
        <td>${escapeHTML(row.member_name)}</td>
        <td>${formatDate(row.due_date)}</td>
        <td class="danger-text">${row.days_overdue}</td>
        <td class="danger-text">${money(row.calculated_fine)}</td>
      </tr>`,
        )
        .join("")
    : `<tr><td colspan="5" class="empty">No overdue books 🎉</td></tr>`;
}

document
  .getElementById("issueForm")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    data.book_id = Number(data.book_id);
    data.member_id = Number(data.member_id);
    data.days = Number(data.days);

    const response = await fetch("/api/loans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      alert((await response.json()).detail || "Could not issue book.");
      return;
    }

    alert("Book issued successfully.");
    await loadSelectors();
    await loadLoans();
  });

async function returnBook(id) {
  if (!confirm("Mark this book as returned?")) return;

  const response = await fetch(`/api/loans/${id}/return`, { method: "POST" });
  const result = await response.json();

  if (!response.ok) {
    alert(result.detail || "Could not return book.");
    return;
  }

  alert(`Book returned. Fine: ${money(result.fine)}`);
  await loadSelectors();
  await loadLoans();
}

loadSelectors();
loadLoans();
