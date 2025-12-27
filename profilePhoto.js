// В функцию switchLanguage добавьте:
const profilePhoto = document.getElementById('profile-photo');
if (profilePhoto) {
    const enAlt = profilePhoto.getAttribute('data-en-alt');
    const ruAlt = profilePhoto.getAttribute('data-ru-alt');
    if (enAlt && ruAlt) {
        profilePhoto.alt = lang === 'en' ? enAlt : ruAlt;
    }
}