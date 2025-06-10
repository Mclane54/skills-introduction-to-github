const contactBtn = document.getElementById('contactBtn');
const contactSection = document.getElementById('contact');

if (contactBtn && contactSection) {
    contactBtn.addEventListener('click', () => {
        contactSection.classList.toggle('active');
        contactSection.scrollIntoView({ behavior: 'smooth' });
    });
}
