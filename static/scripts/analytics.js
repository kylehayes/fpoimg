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
    const placements = new Set(['generator_card', 'support_section', 'docs_note']);
    window.fpoAnalytics = {
        track: function (name, context, placement) {
            if (!names.has(name) || !contexts.has(context)) return;
            try {
                const params = {
                    event_source: context,
                    page_location: pageLocation,
                    page_referrer: referrer
                };
                if (name === 'support_click' && placements.has(placement)) {
                    params.support_placement = placement;
                }
                window.gtag('event', name, params);
            } catch (_) { /* Analytics must not interrupt the tool. */ }
        }
    };
    document.addEventListener('click', function (event) {
        const link = event.target.closest('a[data-support-provider]');
        if (link) window.fpoAnalytics.track('support_click', link.dataset.supportProvider, link.dataset.supportPlacement);
    });

    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.appendChild(tag);
})();
