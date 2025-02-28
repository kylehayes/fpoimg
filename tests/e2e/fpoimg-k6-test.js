import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metric for tracking error rate
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 5 },  // Ramp up to 5 RPS
    { duration: '1m', target: 5 },   // Stay at 5 RPS for 1 minute
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],  // Less than 1% errors
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    'errors': ['rate<0.01'],         // Custom error threshold
  },
};

// Test variations based on the actual Flask application
const variations = [
  // Basic dimensions
  { path: '300x200', params: {} },
  { path: '500', params: {} },  // Square image
  
  // Text via query parameter
  { path: '400x300', params: { text: 'Test Image' } },
  
  // Text via path parameter
  { path: '400x300/Custom Caption', params: {} },
  
  // Custom colors
  { path: '600x400', params: { bg_color: 'ff0000', text_color: 'ffffff' } },
  
  // Combined parameters
  { path: '300x250', params: { text: 'Preview', bg_color: 'e61919', text_color: 'ffffff' } },
  
  // Edge cases
  { path: '10x10', params: {} },  // Minimum size
  { path: '1000x800', params: { text: 'Large Image' } }
];

export default function() {
  // Randomly select a variation
  const variation = variations[Math.floor(Math.random() * variations.length)];
  
  // Add cache buster to prevent caching
  const params = { ...variation.params, cache_buster: Date.now() };
  
  // Get base URL from environment variable
  const baseUrl = __ENV.BASE_URL || 'https://staging-dot-fpoimg.wl.r.appspot.com';
  const url = `${baseUrl}/${variation.path}`;

  // Make the request
  const response = http.get(url, { params });
  
  // Check if response is valid
  const success = check(response, {
    'is status 200': (r) => r.status === 200,
    'has correct content-type': (r) => r.headers['Content-Type'].includes('image/png'),
    'has non-zero content': (r) => parseInt(r.headers['Content-Length']) > 0,
  });
  
  // Track error rate
  errorRate.add(!success);
  
  // Slight pause to simulate real user behavior (but keep it short to maintain RPS)
  sleep(0.2);
}