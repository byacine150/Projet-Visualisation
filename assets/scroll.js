document.addEventListener('click', function (e) {
    var link = e.target.closest('a[href^="#"]');
    if (!link) return;

    var targetId = link.getAttribute('href').slice(1);
    var target = document.getElementById(targetId);
    if (!target) return;

    e.preventDefault();

    var mainContent = document.querySelector('.main-content');
    if (!mainContent) return;

    var targetRect = target.getBoundingClientRect();
    var containerRect = mainContent.getBoundingClientRect();
    var scrollTop = mainContent.scrollTop + (targetRect.top - containerRect.top);

    mainContent.scrollTo({ top: scrollTop, behavior: 'smooth' });
});
