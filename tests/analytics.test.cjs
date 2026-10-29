const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('static/scripts/analytics.js', 'utf8');

function load(id = 'G-TEST123') {
    const listeners = {};
    const tags = [];
    const window = {location: {origin: 'https://fpoimg.com', pathname: '/', search: '?text=private', hash: '#private'}};
    const document = {
        referrer: 'https://example.com/private/path?token=secret',
        getElementById: () => ({dataset: {measurementId: id}}),
        addEventListener: (name, fn) => {listeners[name] = fn;},
        createElement: () => ({}), head: {appendChild: tag => tags.push(tag)}
    };
    vm.runInNewContext(source, {window, document, URL, Date, Set});
    return {window, listeners, tags, calls: () => (window.dataLayer || []).map(call => Array.from(call))};
}

test('property IDs and missing IDs do not enable tracking', () => {
    for (const id of ['', '396709753', 'G-<script>']) {
        const app = load(id);
        assert.equal(app.tags.length, 0);
        assert.equal(app.window.fpoAnalytics, undefined);
    }
});

test('page and action events omit query strings, fragments, and referrer paths', () => {
    const app = load();
    app.window.fpoAnalytics.track('image_url_copy', 'generator');
    const calls = app.calls();
    assert.equal(calls[1][0], 'config');
    assert.equal(calls[1][2].page_location, 'https://fpoimg.com/');
    assert.equal(calls[1][2].page_referrer, 'https://example.com/');
    assert.equal(calls[2][1], 'image_url_copy');
    assert.equal(calls[2][2].event_source, 'generator');
    assert.doesNotMatch(JSON.stringify(calls), /private|secret|token|caption/);
    assert.equal(app.tags[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-TEST123');
});

test('initialization does not count a generate action; only allowed events are accepted', () => {
    const app = load();
    assert.equal(app.calls().filter(call => call[0] === 'event').length, 0);
    app.window.fpoAnalytics.track('arbitrary', 'generator');
    app.window.fpoAnalytics.track('image_generate', 'caption text');
    assert.equal(app.calls().length, 2);
    app.window.fpoAnalytics.track('image_generate', 'generator');
    assert.equal(app.calls().length, 3);
});

test('support click uses only the known provider and handles nested click targets', () => {
    const app = load();
    app.listeners.click({target: {closest: () => ({dataset: {supportProvider: 'github_sponsors'}})}});
    assert.equal(app.calls().at(-1)[1], 'support_click');
    assert.equal(app.calls().at(-1)[2].event_source, 'github_sponsors');
    app.listeners.click({target: {closest: () => null}});
    assert.equal(app.calls().length, 3);
});

test('a failed analytics call does not interrupt an action', () => {
    const app = load();
    app.window.gtag = () => {throw new Error('blocked');};
    assert.doesNotThrow(() => app.window.fpoAnalytics.track('image_generate', 'generator'));
});
