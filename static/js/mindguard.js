/* mindguard.js — Shared JS utilities for MindGuard */

// ── CSRF Token ────────────────────────────────────────────────────────────────
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const cookie = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

// ── Emotion Tag Selection ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.emotion-tag').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('selected');
            updateSelectedEmotions();
        });
    });
});

function updateSelectedEmotions() {
    const selected = [...document.querySelectorAll('.emotion-tag.selected')]
        .map(b => b.dataset.emotion);
    const hiddenInput = document.getElementById('selected-emotions');
    if (hiddenInput) hiddenInput.value = selected.join(',');
}

// ── Quick Mood Submit ─────────────────────────────────────────────────────────
async function submitQuickMood() {
    const payload = {
        mood_score: parseInt(document.getElementById('quick-mood-score').value),
        energy_level: parseInt(document.getElementById('quick-energy').value),
        sleep_hours: 0,
        emotions: [...document.querySelectorAll('#emotion-tags .emotion-tag.selected')]
            .map(b => b.dataset.emotion),
        notes: document.getElementById('quick-mood-notes')?.value || '',
    };

    try {
        const resp = await fetch('/mood/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('quickMoodModal'));
            if (modal) modal.hide();
            showToast('Mood logged successfully! 📊', 'success');
        }
    } catch (e) { console.error('Mood submit error:', e); }
}

// ── Wellness Tip ──────────────────────────────────────────────────────────────
async function loadWellnessTip() {
    const card = document.getElementById('wellness-tip-card');
    if (!card) return;
    try {
        const resp = await fetch('/api/wellness/tips');
        const data = await resp.json();
        const tip = data.tip;
        const categoryColors = {
            mindfulness: 'success', physical: 'primary', emotional: 'warning',
            lifestyle: 'info', social: 'secondary', sleep: 'dark',
        };
        const color = categoryColors[tip.category] || 'secondary';
        card.innerHTML = `
            <span class="badge bg-${color} mb-2">${tip.category}</span>
            <h6 class="fw-bold">${tip.title}</h6>
            <p class="text-muted small mb-0">${tip.content}</p>`;
        const loading = document.getElementById('tip-loading');
        if (loading) loading.remove();
    } catch (e) {
        if (card) card.innerHTML = '<p class="text-muted small">Take a deep breath and be kind to yourself today. 💚</p>';
    }
}

// ── Add Wellness Goal ─────────────────────────────────────────────────────────
async function addGoal() {
    const title = document.getElementById('goal-title')?.value.trim();
    if (!title) { showToast('Please enter a goal title', 'warning'); return; }
    const payload = {
        title: title,
        category: document.getElementById('goal-category')?.value || 'other',
        target_days: parseInt(document.getElementById('goal-days')?.value || 7),
    };
    try {
        const resp = await fetch('/profile/goals/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addGoalModal'));
            if (modal) modal.hide();
            location.reload();
        }
    } catch (e) { console.error('Add goal error:', e); }
}

// ── Complete Goal Day ─────────────────────────────────────────────────────────
async function completeGoalDay(goalId, btn) {
    try {
        const resp = await fetch(`/profile/goals/${goalId}/complete`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },
        });
        const data = await resp.json();
        if (data.success) {
            showToast('Great job! Day marked ✅', 'success');
            btn.disabled = true;
            btn.textContent = '✅ Done today!';
        }
    } catch (e) { console.error(e); }
}

// ── Toast Notification ────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'danger' ? 'danger' : 'primary'} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    container.appendChild(toast);
    setTimeout(() => { toast.remove(); }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// ── Show Crisis Banner ────────────────────────────────────────────────────────
function showCrisisBanner() {
    const banner = document.getElementById('crisis-banner');
    if (banner) banner.classList.remove('d-none');
}
