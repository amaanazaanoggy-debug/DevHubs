/**
 * DevHub Frontend JavaScript
 * Handles AJAX interactions for Star, Like, Bookmark, Follow and Code Copying
 */

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

async function toggleStar(projectId, btn) {
  try {
    const res = await fetch(`/api/star/${projectId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      }
    });

    if (res.status === 401 || res.redirected) {
      window.location.href = '/auth/login';
      return;
    }

    const data = await res.json();
    if (data.success) {
      const starIcon = btn.querySelector('.star-icon');
      const starCount = btn.querySelector('.star-count');
      const starText = btn.querySelector('.star-text');

      if (data.starred) {
        if (starIcon) starIcon.classList.add('text-amber-400', 'fill-amber-400');
        if (starText) starText.textContent = 'Starred';
      } else {
        if (starIcon) starIcon.classList.remove('text-amber-400', 'fill-amber-400');
        if (starText) starText.textContent = 'Star';
      }
      if (starCount) starCount.textContent = data.count;
    }
  } catch (err) {
    console.error('Star error:', err);
  }
}

async function toggleLike(postId, btn) {
  try {
    const res = await fetch(`/api/like/${postId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      }
    });

    if (res.status === 401 || res.redirected) {
      window.location.href = '/auth/login';
      return;
    }

    const data = await res.json();
    if (data.success) {
      const icon = btn.querySelector('.like-icon');
      const count = btn.querySelector('.like-count');

      if (data.liked) {
        if (icon) icon.classList.add('text-rose-500', 'fill-rose-500');
        btn.classList.add('text-rose-500');
      } else {
        if (icon) icon.classList.remove('text-rose-500', 'fill-rose-500');
        btn.classList.remove('text-rose-500');
      }
      if (count) count.textContent = data.count;
    }
  } catch (err) {
    console.error('Like error:', err);
  }
}

async function toggleBookmark(postId, btn) {
  try {
    const res = await fetch(`/api/bookmark/${postId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      }
    });

    if (res.status === 401 || res.redirected) {
      window.location.href = '/auth/login';
      return;
    }

    const data = await res.json();
    if (data.success) {
      const icon = btn.querySelector('.bookmark-icon');
      if (data.bookmarked) {
        if (icon) icon.classList.add('text-indigo-400', 'fill-indigo-400');
      } else {
        if (icon) icon.classList.remove('text-indigo-400', 'fill-indigo-400');
      }
    }
  } catch (err) {
    console.error('Bookmark error:', err);
  }
}

async function toggleFollow(userId, btn) {
  try {
    const res = await fetch(`/api/follow/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      }
    });

    if (res.status === 401 || res.redirected) {
      window.location.href = '/auth/login';
      return;
    }

    const data = await res.json();
    if (data.success) {
      if (data.following) {
        btn.textContent = 'Following';
        btn.classList.remove('bg-gh-subtle', 'text-white');
        btn.classList.add('bg-gh-canvas', 'text-gh-muted', 'border-gh-border');
      } else {
        btn.textContent = 'Follow';
        btn.classList.add('bg-gh-subtle', 'text-white');
        btn.classList.remove('bg-gh-canvas', 'text-gh-muted', 'border-gh-border');
      }
      
      const countEl = document.querySelector(`#followers-count-${userId}`);
      if (countEl) {
        countEl.textContent = data.followers_count;
      }
    }
  } catch (err) {
    console.error('Follow error:', err);
  }
}

function copyCodeToClipboard(button) {
  const container = button.closest('.code-container') || button.closest('pre');
  const codeEl = container ? container.querySelector('code, .code') : null;
  const text = codeEl ? codeEl.innerText : '';
  
  if (text) {
    navigator.clipboard.writeText(text).then(() => {
      const originalText = button.innerHTML;
      button.innerHTML = `
        <svg class="w-3.5 h-3.5 text-emerald-400 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg> Copied!
      `;
      setTimeout(() => {
        button.innerHTML = originalText;
      }, 2000);
    });
  }
}
