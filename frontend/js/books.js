function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[c]));
}

async function loadBooks() {
  const search = document.getElementById("bookSearch").value;
  const response = await fetch(`/api/books?search=${encodeURIComponent(search)}`);
  const books = await response.json();

  document.getElementById("booksTable").innerHTML = books.length
    ? books.map(book => `
      <tr>
        <td>${escapeHTML(book.isbn)}</td>
        <td><strong>${escapeHTML(book.title)}</strong></td>
        <td>${escapeHTML(book.author)}</td>
        <td>${escapeHTML(book.category)}</td>
        <td>${book.total_copies}</td>
        <td>${book.available_copies}</td>
        <td><button class="action-button" onclick="deleteBook(${book.book_id})">Delete</button></td>
      </tr>`).join("")
    : `<tr><td colspan="7" class="empty">No books found.</td></tr>`;
}

function toggleForm() {
  document.getElementById("bookForm").classList.toggle("hidden");
}

document.getElementById("bookSearch").addEventListener("input", loadBooks);

document.getElementById("addBookForm").addEventListener("submit", async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  data.total_copies = Number(data.total_copies);
  if (data.publication_year) data.publication_year = Number(data.publication_year);
  else data.publication_year = null;

  const response = await fetch("/api/books", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    alert((await response.json()).detail || "Could not add book.");
    return;
  }

  event.target.reset();
  toggleForm();
  loadBooks();
});

async function deleteBook(id) {
  if (!confirm("Delete this book? Books with loan history cannot be deleted.")) return;
  const response = await fetch(`/api/books/${id}`, {method: "DELETE"});
  if (!response.ok) {
    alert((await response.json()).detail || "Could not delete book.");
    return;
  }
  loadBooks();
}

loadBooks();
