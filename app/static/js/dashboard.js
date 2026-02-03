document.addEventListener('DOMContentLoaded', () => {
    // Current State
    let currentView = 'companies'; // 'companies' or 'employees'
    let selectedCompany = null;
    let editId = null; // Track if we are editing

    // Elements
    const mainTitle = document.getElementById('mainTitle');
    const statsGrid = document.getElementById('statsGrid');
    const dataTable = document.getElementById('dataTable');
    const dataHeader = document.getElementById('dataHeader');
    const addBtn = document.getElementById('addBtn');
    const companySelector = document.getElementById('companySelector');

    // API Functions
    async function apiFetch(endpoint) {
        try {
            const response = await fetch(`/api${endpoint}`);
            if (!response.ok) throw new Error('API Error');
            return await response.json();
        } catch (error) {
            console.error(error);
            // alert('Error fetching data');
        }
    }

    async function apiPost(endpoint, data) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('API Error');
            return await response.json();
        } catch (error) {
            console.error(error);
            alert('Error saving data');
        }
    }

    async function apiPut(endpoint, data) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('API Error');
            return await response.json();
        } catch (error) {
            console.error(error);
            alert('Error updating data');
        }
    }

    async function apiDelete(endpoint) {
        try {
            const response = await fetch(`/api${endpoint}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('API Error');
            return await response.json();
        } catch (error) {
            console.error(error);
            alert('Error deleting data');
        }
    }

    // Load Overview
    async function loadCompaniesView() {
        currentView = 'companies';
        mainTitle.textContent = 'Companies Dashboard';
        addBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Company';
        addBtn.className = 'btn btn-primary';
        addBtn.onclick = window.openAddModal;
        companySelector.style.display = 'none';
        document.getElementById('top5Section').style.display = 'block';

        const data = await apiFetch('/dashboard/all-data');
        if (!data) return;
        renderStats(data.companies, data.summary);
        renderCompaniesTable(data.companies);

        // Automatic fetch for top companies
        loadTop5Companies();
    }

    async function loadEmployeesView(companyName = null) {
        currentView = 'employees';
        selectedCompany = companyName;
        mainTitle.textContent = companyName ? `${companyName} Employees` : 'All Employees';
        addBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Employee';
        addBtn.className = 'btn btn-primary';
        addBtn.onclick = window.openAddModal;
        companySelector.style.display = 'flex';
        document.getElementById('top5Section').style.display = 'block';

        // Load Company Radios
        await renderCompanyRadios();

        const endpoint = companyName
            ? `/employees/filter?company=${encodeURIComponent(companyName)}`
            : '/employees';

        const employees = await apiFetch(endpoint);
        if (!employees) return;
        renderStatsForEmployees(employees);
        renderEmployeesTable(employees);

        // Automatic fetch for top companies
        loadTop5Companies();
    }

    async function loadLogsView() {
        currentView = 'logs';
        mainTitle.textContent = 'Audit & Security Logs';
        addBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Clear Logs';
        addBtn.className = 'btn btn-danger';
        addBtn.onclick = clearLogs;
        companySelector.style.display = 'none';
        document.getElementById('top5Section').style.display = 'none';

        const logs = await apiFetch('/logs');
        if (!logs) return;
        renderStatsForLogs(logs);
        renderLogsTable(logs);
    }

    async function clearLogs() {
        if (confirm('Permanently clear all audit logs?')) {
            await apiDelete('/logs');
            loadLogsView();
        }
    }

    async function renderCompanyRadios() {
        const companies = await apiFetch('/companies');
        if (!companies) return;

        let html = `
            <div class="radio-group">
                <input type="radio" id="all" name="comp_select" ${!selectedCompany ? 'checked' : ''} 
                       onchange="window.loadEmployeesView()">
                <label for="all">All Companies</label>
            </div>
        `;

        companies.forEach(company => {
            const name = company.company_name || company.name;
            html += `
                <div class="radio-group">
                    <input type="radio" id="comp_${company.companies_id || company.id}" name="comp_select" 
                           ${selectedCompany === name ? 'checked' : ''} 
                           onchange="window.loadEmployeesView('${name}')">
                    <label for="comp_${company.companies_id || company.id}">${name}</label>
                </div>
            `;
        });

        companySelector.innerHTML = html;
    }

    function renderStats(companies, summary = null) {
        const totalCompanies = summary ? summary.total_companies : companies.length;
        const totalEmployees = summary ? summary.total_employees : companies.reduce((acc, c) => acc + (c.employees ? c.employees.length : 0), 0);
        const totalSalary = summary ? summary.total_salary : companies.reduce((acc, c) => {
            return acc + (c.employees ? c.employees.reduce((eAcc, e) => eAcc + e.salary, 0) : 0);
        }, 0);

        statsGrid.innerHTML = `
            <div class="stat-card fade-in">
                <h3>Total Companies</h3>
                <div class="value">${totalCompanies}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.1s">
                <h3>Total Employees</h3>
                <div class="value">${totalEmployees}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.2s">
                <h3>Total Monthly Budget</h3>
                <div class="value">$${totalSalary.toLocaleString()}</div>
            </div>
        `;
    }

    function renderStatsForEmployees(employees) {
        const totalSalary = employees.reduce((acc, e) => acc + e.salary, 0);
        const avgSalary = employees.length ? (totalSalary / employees.length).toFixed(2) : 0;

        statsGrid.innerHTML = `
            <div class="stat-card fade-in">
                <h3>Emp Count</h3>
                <div class="value">${employees.length}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.1s">
                <h3>Total Salary</h3>
                <div class="value">$${totalSalary.toLocaleString()}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.2s">
                <h3>Avg Salary</h3>
                <div class="value">$${parseFloat(avgSalary).toLocaleString()}</div>
            </div>
        `;
    }

    function renderStatsForLogs(logs) {
        const errors = logs.filter(l => l.level === 'ERROR').length;
        const warnings = logs.filter(l => l.level === 'WARNING').length;

        statsGrid.innerHTML = `
            <div class="stat-card fade-in">
                <h3>Total Events</h3>
                <div class="value">${logs.length}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.1s">
                <h3>Errors</h3>
                <div class="value" style="color: var(--danger-color)">${errors}</div>
            </div>
            <div class="stat-card fade-in" style="animation-delay: 0.2s">
                <h3>Warnings</h3>
                <div class="value" style="color: #fbbf24">${warnings}</div>
            </div>
        `;
    }

    function renderCompaniesTable(companies) {
        dataHeader.innerHTML = `
            <tr>
                <th>Company Name</th>
                <th>Location</th>
                <th>Employees</th>
                <th>Actions</th>
            </tr>
        `;

        dataTable.innerHTML = companies.map(c => {
            const name = c.company_name || c.name;
            const empCount = c.employees ? c.employees.length : 0;
            return `
                <tr class="fade-in">
                    <td><strong style="color: var(--primary-color)">${name}</strong></td>
                    <td>${c.location || 'N/A'}</td>
                    <td><span class="company-badge" onclick="window.loadEmployeesView('${name}')">${empCount} Members</span></td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="window.openEditModal('companies', ${JSON.stringify(c).replace(/"/g, '&quot;')})">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="window.deleteCompany(${c.companies_id || c.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function renderEmployeesTable(employees) {
        dataHeader.innerHTML = `
            <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Salary</th>
                <th>Company</th>
                <th>Actions</th>
            </tr>
        `;

        dataTable.innerHTML = employees.map(e => `
            <tr class="fade-in">
                <td><strong>${e.employee_name}</strong></td>
                <td>${e.role}</td>
                <td>$${e.salary.toLocaleString()}</td>
                <td><span class="company-badge">${e.company_name}</span></td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="window.openEditModal('employees', ${JSON.stringify(e).replace(/"/g, '&quot;')})">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="window.deleteEmployee(${e.employee_id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async function loadTop5Companies() {
        const top5 = await apiFetch('/dashboard/top-companies');
        if (!top5) return;

        const top5Body = document.getElementById('top5Body');
        if (!top5Body) return;

        if (top5.length === 0) {
            top5Body.innerHTML = `
                <tr>
                    <td colspan="3" style="text-align: center; padding: 2rem; color: var(--text-secondary);">No data yet. Create companies and employees first.</td>
                </tr>
            `;
            return;
        }

        top5Body.innerHTML = top5.map(row => `
            <tr class="fade-in top5-row">
                <td>${row.company_name}</td>
                <td class="top5-employee">${row.employee_name}</td>
                <td class="top5-salary">$${row.salary.toLocaleString()}</td>
            </tr>
        `).join('');
    }

    function renderLogsTable(logs) {
        dataHeader.innerHTML = `
            <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Event Message</th>
                <th>Trace Details</th>
            </tr>
        `;

        if (logs.error) {
            dataTable.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color:var(--danger-color)">${logs.error}</td></tr>`;
            return;
        }

        if (Array.isArray(logs) && logs.length === 0) {
            dataTable.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;">No logs found. Try performing some actions.</td></tr>`;
            return;
        }

        dataTable.innerHTML = logs.map(l => {
            const levelClass = `level-${l.level.toLowerCase()}`;
            const date = new Date(l.timestamp).toLocaleString();

            // Premium details rendering
            let detailsHtml = '';
            if (l.details) {
                if (l.details.type === 'audit_log') {
                    const statusColor = l.details.status_code >= 400 ? 'var(--danger-color)' : 'var(--accent-color)';
                    detailsHtml = `
                        <div style="display:flex; gap:0.5rem; align-items:center;">
                            <span class="company-badge" style="background:rgba(255,255,255,0.05); color:var(--text-primary); border-color:var(--glass-border)">${l.details.method}</span>
                            <span class="company-badge" style="border-color:${statusColor}; color:${statusColor}; background:transparent">${l.details.status_code}</span>
                            <code style="font-size:0.75rem; color:var(--text-secondary)">${l.details.path}</code>
                        </div>
                    `;
                } else {
                    const strDetails = JSON.stringify(l.details);
                    detailsHtml = `<span class="log-details" title='${strDetails}'>${strDetails}</span>`;
                }
            }

            return `
                <tr class="fade-in">
                    <td class="log-timestamp">${date}</td>
                    <td><span class="log-level ${levelClass}">${l.level}</span></td>
                    <td style="color:var(--text-primary)">${l.message}</td>
                    <td>${detailsHtml}</td>
                </tr>
            `;
        }).join('');
    }

    // Modal Handling
    const modal = document.getElementById('crudModal');
    window.openAddModal = () => {
        editId = null;
        const title = currentView === 'companies' ? 'Add New Company' : 'Add New Employee';
        document.getElementById('modalTitle').textContent = title;

        let formHtml = '';
        if (currentView === 'companies') {
            formHtml = `
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="compName" class="form-control" required placeholder="Goggle, Amzon...">
                </div>
                <div class="form-group">
                    <label>Location</label>
                    <input type="text" id="compLoc" class="form-control" placeholder="New York, Remote...">
                </div>
            `;
        } else {
            formHtml = `
                <div class="form-group">
                    <label>Employee Name</label>
                    <input type="text" id="empName" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <input type="text" id="empRole" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Salary</label>
                    <input type="number" id="empSalary" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="empComp" class="form-control" value="${selectedCompany || ''}" required>
                </div>
            `;
        }

        document.getElementById('formFields').innerHTML = formHtml;
        modal.style.display = 'flex';
    };

    window.openEditModal = (type, data) => {
        editId = type === 'companies' ? (data.companies_id || data.id) : data.employee_id;
        document.getElementById('modalTitle').textContent = type === 'companies' ? 'Edit Company' : 'Edit Employee';

        let formHtml = '';
        if (type === 'companies') {
            formHtml = `
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="compName" class="form-control" value="${data.company_name || data.name}" required>
                </div>
                <div class="form-group">
                    <label>Location</label>
                    <input type="text" id="compLoc" class="form-control" value="${data.location || ''}">
                </div>
            `;
        } else {
            formHtml = `
                <div class="form-group">
                    <label>Employee Name</label>
                    <input type="text" id="empName" class="form-control" value="${data.employee_name}" required>
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <input type="text" id="empRole" class="form-control" value="${data.role}" required>
                </div>
                <div class="form-group">
                    <label>Salary</label>
                    <input type="number" id="empSalary" class="form-control" value="${data.salary}" required>
                </div>
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="empComp" class="form-control" value="${data.company_name}" required>
                </div>
            `;
        }

        document.getElementById('formFields').innerHTML = formHtml;
        modal.style.display = 'flex';
    };

    window.hideModal = () => {
        modal.style.display = 'none';
    };

    document.getElementById('crudForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (currentView === 'companies') {
            const data = {
                company_name: document.getElementById('compName').value,
                location: document.getElementById('compLoc').value
            };
            if (editId) {
                await apiPut(`/companies/${editId}`, data);
            } else {
                await apiPost('/companies', data);
            }
            loadCompaniesView();
        } else {
            const data = {
                name: document.getElementById('empName').value,
                role: document.getElementById('empRole').value,
                salary: parseFloat(document.getElementById('empSalary').value),
                company_name: document.getElementById('empComp').value
            };
            if (editId) {
                await apiPut(`/employees/${editId}`, data);
            } else {
                await apiPost('/employees', data);
            }
            loadEmployeesView(selectedCompany);
        }
        window.hideModal();
    });

    window.deleteCompany = async (id) => {
        if (confirm('Are you sure? This will also delete all employees in this company.')) {
            await apiDelete(`/companies/${id}`);
            loadCompaniesView();
        }
    };

    window.deleteEmployee = async (id) => {
        if (confirm('Delete this employee?')) {
            await apiDelete(`/employees/${id}`);
            loadEmployeesView(selectedCompany);
        }
    };

    window.loadCompaniesView = loadCompaniesView;
    window.loadEmployeesView = loadEmployeesView;
    window.loadLogsView = loadLogsView;

    loadCompaniesView();
});
