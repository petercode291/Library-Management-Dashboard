function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[c]));
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString("en-IN") : "—";
}

async function loadMembers() {
  const search = document.getElementById("memberSearch").value;
  const response = await fetch(`/api/members?search=${encodeURIComponent(search)}`);
  const members = await response.json();

  document.getElementById("membersTable").innerHTML = members.length
    ? members.map(member => `
      <tr>
        <td>${escapeHTML(member.member_code)}</td>
        <td><strong>${escapeHTML(member.first_name)} ${escapeHTML(member.last_name)}</strong></td>
        <td>${escapeHTML(member.email)}</td>
        <td>${escapeHTML(member.phone || "—")}</td>
        <td>${formatDate(member.membership_date)}</td>
        <td><span class="badge ${member.status.toLowerCase()}">${member.status}</span></td>
        <td>
          <button class="action-button"
            onclick="toggleMember(${member.member_id}, '${member.status}')">
            ${member.status === "Active" ? "Deactivate" : "Activate"}
          </button>
        </td>
      </tr>`).join("")
    : `<tr><td colspan="7" class="empty">No members found.</td></tr>`;
}

function toggleForm() {
  document.getElementById("memberForm").classList.toggle("hidden");
}

document.getElementById("memberSearch").addEventListener("input", loadMembers);

document.getElementById("addMemberForm").addEventListener("submit", async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));

  const response = await fetch("/api/members", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    alert((await response.json()).detail || "Could not add member.");
    return;
  }

  event.target.reset();
  toggleForm();
  loadMembers();
});

async function toggleMember(id, status) {
  const nextStatus = status === "Active" ? "Inactive" : "Active";
  const response = await fetch(`/api/members/${id}`, {
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({status: nextStatus})
  });

  if (!response.ok) {
    alert((await response.json()).detail || "Could not update member.");
    return;
  }

  loadMembers();
}

loadMembers();
