document.getElementById("search-btn").addEventListener("click", function () {
  const selectedTable = document.getElementById("table-select").value;
  const searchValue = document.getElementById("search-input").value;
  const resultsContainer = document.getElementById("results-container");
  resultsContainer.innerHTML = "";
  if (selectedTable && searchValue) {
    closeEditModal();
    fetch("/perform-search/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        table: selectedTable,
        search_value: searchValue,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const results = data.results;
          if (results.length > 0) {
            const table = document.createElement("table");
            const headerRow = document.createElement("tr");
      
            // Create table header
            Object.keys(results[0]).forEach((key) => {
              const th = document.createElement("th");
              th.textContent = key;
              headerRow.appendChild(th);
            });
      
            const actionsTh = document.createElement("th");
            actionsTh.textContent = "Actions";
            headerRow.appendChild(actionsTh);
      
            table.appendChild(headerRow);
      
            // Create table rows
            results.forEach((entry) => {
              const row = document.createElement("tr");
            
              Object.values(entry).forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
              });
            
              const actionsCell = document.createElement("td");
            
              const editBtn = document.createElement("button");
              editBtn.textContent = "Edit";
              editBtn.addEventListener("click", function (event) {
                if (confirm("Are you sure you want to edit this record?")) {
                  openEditModal(selectedTable, entry, event);
                }
              });
              
              const deleteBtn = document.createElement("button");
              deleteBtn.textContent = "Delete";
              deleteBtn.addEventListener("click", function () {
                if (confirm("Are you sure you want to delete this record?")) {
                  deleteRecord(selectedTable, entry);
                }
              });
            
              actionsCell.appendChild(editBtn);
              actionsCell.appendChild(deleteBtn);
              row.appendChild(actionsCell);
            
              table.appendChild(row);
            });
      
            resultsContainer.appendChild(table);
          } else {
            resultsContainer.textContent = "No matching records found.";
          }
        } else {
          resultsContainer.textContent = "Error: " + data.error;
        }
      })
      .catch((error) => {
        console.error("Error searching records:", error);
        resultsContainer.textContent =
          "An error occurred while searching records.";
      });
  }
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


function deleteRecord(table, record) {
  // Send a request to delete the record from the server
  fetch("/delete-record/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      table: table,
      record_id: record.Criminal_ID || record.Crime_ID,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Remove the deleted record from the table
        // ...
      } else {
        console.error("Error deleting record:", data.error);
      }
    })
    .catch((error) => {
      console.error("Error deleting record:", error);
    });
}

