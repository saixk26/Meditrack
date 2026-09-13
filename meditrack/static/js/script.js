/* =============================================================
   MediTrack - Global JavaScript
   Sidebar toggle | Live search | Delete confirmation | Toasts
   Image preview | Dynamic counters | Responsive sidebar
   ============================================================= */

document.addEventListener('DOMContentLoaded', function () {
    initSidebarToggle();
    initLiveSearch();
    initDeleteConfirm();
    initToasts();
    initDynamicCounters();
});

/* --------------------------- SIDEBAR TOGGLE --------------------------- */
function initSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggle');
    if (!toggleBtn) return;

    toggleBtn.addEventListener('click', function () {
        if (window.innerWidth <= 992) {
            document.body.classList.toggle('sidebar-open');
        } else {
            document.body.classList.toggle('sidebar-collapsed');
        }
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
        if (window.innerWidth <= 992 && document.body.classList.contains('sidebar-open')) {
            const sidebar = document.getElementById('sidebar');
            if (!sidebar.contains(e.target) && e.target !== toggleBtn && !toggleBtn.contains(e.target)) {
                document.body.classList.remove('sidebar-open');
            }
        }
    });
}

/* --------------------------- LIVE SEARCH (client-side table filter) --------------------------- */
function initLiveSearch() {
    const searchInput = document.getElementById('liveSearch');
    const table = document.getElementById('medicineTable');
    if (!searchInput || !table) return;

    // NOTE: The primary search already happens server-side via form submit
    // (see the surrounding <form>). This adds an *instant* client-side
    // filter on top, for a snappier feel while typing, before the user
    // presses Enter / the Search button which re-queries the server.
    searchInput.addEventListener('keyup', function (e) {
        const query = this.value.toLowerCase();
        const rows = table.matches('tbody') ? table.querySelectorAll('tr') : table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            if (row.id === 'emptyCartRow') return;
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
        // Submit the real search on Enter for authoritative, paginated results
        if (e.key === 'Enter') {
            this.form?.submit();
        }
    });
}

/* --------------------------- DELETE CONFIRMATION --------------------------- */
function initDeleteConfirm() {
    document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
        btn.addEventListener('click', function () {
            const formId = this.dataset.form;
            const form = document.getElementById(formId);
            if (!form) return;

            if (confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                form.submit();
            }
        });
    });
}

/* --------------------------- TOAST NOTIFICATIONS --------------------------- */
function initToasts() {
    document.querySelectorAll('.toast').forEach(toastEl => {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    });
}

/**
 * Programmatically show a toast message (used by JS-driven validation,
 * e.g. the billing cart screen).
 */
function showToastMsg(message, type = 'info') {
    const container = document.querySelector('.toast-container');
    if (!container) { alert(message); return; }

    const icons = {
        success: 'fa-circle-check', danger: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation', info: 'fa-circle-info',
    };
    const wrapper = document.createElement('div');
    wrapper.className = `toast align-items-center text-bg-${type} border-0 show mb-2`;
    wrapper.setAttribute('role', 'alert');
    wrapper.innerHTML = `
        <div class="d-flex">
            <div class="toast-body"><i class="fa-solid ${icons[type] || icons.info} me-2"></i>${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    container.appendChild(wrapper);
    new bootstrap.Toast(wrapper, { delay: 4000 }).show();
}

/* --------------------------- DYNAMIC COUNTERS (animated stat numbers) --------------------------- */
function initDynamicCounters() {
    document.querySelectorAll('.stat-card h3').forEach(el => {
        const target = parseInt(el.textContent.replace(/[^0-9]/g, ''), 10);
        if (isNaN(target)) return;
        let current = 0;
        const step = Math.max(1, Math.ceil(target / 30));
        const prefix = el.textContent.trim().startsWith('₹') ? '₹' : '';

        const interval = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }
            el.textContent = prefix + current;
        }, 20);
    });
}
