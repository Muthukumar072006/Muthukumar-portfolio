document.addEventListener('DOMContentLoaded', () => {

    const contactForm = document.getElementById('contactForm');
    const responseDiv = document.getElementById('formResponse');

    if (contactForm) {
        contactForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const payload = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                subject: document.getElementById('subject').value,
                message: document.getElementById('message').value
            };

            responseDiv.innerHTML = "⏳ Sending message...";
            responseDiv.className = "form-response";

            try {
                const res = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                if (res.ok) {
                    responseDiv.innerHTML = "✨ " + data.message;
                    responseDiv.className = "form-response success";
                    contactForm.reset();
                } else {
                    responseDiv.innerHTML = "❌ " + data.message;
                    responseDiv.className = "form-response error";
                }
            } catch (err) {
                responseDiv.innerHTML = "❌ Network error. Please try again!";
                responseDiv.className = "form-response error";
            }
        });
    }
});