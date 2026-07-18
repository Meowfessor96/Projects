document.getElementById('save').addEventListener('click', () => {
  const groqKey = document.getElementById('groq_key').value;
  const ghToken = document.getElementById('gh_token').value;
  
  chrome.storage.local.set({ groq_key: groqKey, gh_token: ghToken }, () => {
    const status = document.getElementById('status');
    status.textContent = 'Configuration saved successfully!';
    setTimeout(() => { status.textContent = ''; }, 2500);
  });
});

document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get(['groq_key', 'gh_token'], (result) => {
    if (result.groq_key) document.getElementById('groq_key').value = result.groq_key;
    if (result.gh_token) document.getElementById('gh_token').value = result.gh_token;
  });
});
