document.getElementById('table-select').addEventListener('change', function() {
    const selectedTable = this.value;
    const fieldsContainer = document.getElementById('fields-container');
    fieldsContainer.innerHTML = '';

    let fields = [];

    switch (selectedTable) {
        case 'criminals':
            fields = ['Criminal_ID', 'Violent_Stat', 'Probation_Stat', 'Name'];
            break;
        case 'crimes':
            fields = ['Crime_ID', 'Criminal_ID', 'Crime_Code', 'Classification'];
            break;
        case 'charges':
            fields = ['Crime_ID', 'Charge_Status', 'Charge_Date'];
            break;
        case 'sentencing':
            fields = ['Crime_ID', 'Start_Date', 'End_Date', 'Violation_Num', 'Sentence_Type'];
            break;
        case 'criminal_phone':
            fields = ['Criminal_ID', 'Number'];
            break;
        case 'aliases':
            fields = ['Criminal_ID', 'Alias'];
            break;
        case 'address':
            fields = ['Criminal_ID', 'Addr', 'City', 'State', 'Zip_Code'];
            break;
        case 'hearing':
            fields = ['Crime_ID', 'Hearing_Date', 'Appeal_Cutoff_Date'];
            break;
        case 'monetary':
            fields = ['Crime_ID', 'Amount_Fined', 'Amount_Paid', 'Court_Fee', 'Due_Date'];
            break;
        case 'appeals':
            fields = ['Crime_ID', 'Filling_Date', 'Hearing_Date', 'Appeal_Status'];
            break;
        case 'arresting_officers':
            fields = ['Crime_ID', 'Badge_ID'];
            break;
        case 'officer':
            fields = ['Badge_Number', 'Name', 'Precinct', 'Officer_Status'];
            break;
        case 'officer_phone':
            fields = ['Badge_Number', 'Number'];
            break;
    }

    fields.forEach(function(field) {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.setAttribute('for', field);
        label.textContent = field.replace(/_/g, ' ') + ':';

        const input = document.createElement('input');
        input.type = 'text';
        input.id = field;
        input.name = field;

        formGroup.appendChild(label);
        formGroup.appendChild(input);
        fieldsContainer.appendChild(formGroup);
    });
});