// Add these variables at the beginning of the file
const editModal = document.getElementById("edit-modal");
const editForm = document.getElementById("edit-form");
const closeBtn = document.getElementsByClassName("close")[0];
const saveBtn = document.getElementById("save-btn");

function openEditModal(table, record, event) {
    // Clear previous form fields
    editForm.innerHTML = "";
  
    // Generate form fields based on the table and record
    Object.entries(record).forEach(([key, value]) => {
      const label = document.createElement("label");
      label.textContent = key;
      const input = document.createElement("input");
      input.type = "text";
      input.name = key;
      input.value = value;
      editForm.appendChild(label);
      editForm.appendChild(input);
    });
  
    // Set the table and record ID as data attributes on the form
    editForm.dataset.table = table;
    editForm.dataset.recordId = record.Criminal_ID || record.Crime_ID;
  
    // Open the modal
    editModal.style.display = "block";
  }

// Close the modal when the close button or outside the modal is clicked
closeBtn.onclick = function () {
  editModal.style.display = "none";
};
window.onclick = function (event) {
  if (event.target == editModal) {
    editModal.style.display = "none";
  }
};

// Handle form submission
saveBtn.onclick = function () {
  const formData = new FormData(editForm);
  const table = editForm.dataset.table;
  const recordId = editForm.dataset.recordId;

  // Add table and record ID to the form data
  formData.append("table", table);
  formData.append("record_id", recordId);

  // Send the edited data to the server
  fetch("/edit-record/", {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Close the modal and refresh the table
        editModal.style.display = "none";
        searchRecords();
      } else {
        console.error("Error editing record:", data.error);
      }
    })
    .catch((error) => {
      console.error("Error editing record:", error);
    });
};

function closeEditModal() {
    editModal.style.display = "none";
  }