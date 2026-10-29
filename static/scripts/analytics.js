/* First-party UI events sent to the configured GA4 web stream. */
(function () {
    'use strict';
    const script = document.getElementById('fpo-analytics');
    const measurementId = script && script.dataset.measurementId;
    if (!/^G-[A-Z0-9]+$/.test(measurementId || '')) return;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    const pageLocation = window.location.origin + window.location.pathname;
    let referrer = '';
    try { referrer = new URL(document.referrer).origin + '/'; } catch (_) { /* No referrer. */ }
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
        page_location: pageLocation,
        page_referrer: referrer,
        allow_google_signals: false,
        allow_ad_personalization_signals: false
    });

    const names = new Set(['image_generate', 'image_url_copy', 'support_click']);
    const contexts = new Set(['generator', 'gradient_builder', 'gradient_preset', 'github_sponsors', 'buy_me_a_coffee']);
    window.fpoAnalytics = {
        track: function (name, context) {
            if (!names.has(name) || !contexts.has(context)) return;
            try {
                window.gtag('event', name, {
                    event_source: context,
                    page_location: pageLocation,
                    page_referrer: referrer
                });
            } catch (_) { /* Analytics must not interrupt the tool. */ }
        }
    };
    document.addEventListener('click', function (event) {
        const link = event.target.closest('a[data-support-provider]');
        if (link) window.fpoAnalytics.track('support_click', link.dataset.supportProvider);
    });

    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.appendChild(tag);
})();
