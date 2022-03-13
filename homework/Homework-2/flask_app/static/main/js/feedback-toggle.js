/* toggles feeback form to show/hide */

const feedbackButton = document.getElementById('feedback-btn-container');
const form = document.getElementById('feedback-form-container');
feedbackButton.addEventListener('click', () => {
    form.classList.toggle('show');
});