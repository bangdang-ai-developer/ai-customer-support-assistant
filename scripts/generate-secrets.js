#!/usr/bin/env node

/**
 * NEXTAUTH_SECRET Generator
 * Generates cryptographically secure secrets for NextAuth.js
 */

const crypto = require('crypto');

function generateSecret(length = 32) {
  return crypto.randomBytes(length).toString('base64');
}

console.log('🔐 NEXTAUTH_SECRET Generator');
console.log('============================\n');

// Generate secrets for different environments
const secrets = {
  development: generateSecret(32),
  staging: generateSecret(32),
  production: generateSecret(64) // Longer key for production
};

console.log('Generated NEXTAUTH_SECRET keys:\n');

console.log('📝 For Development (.env.local):');
console.log(`NEXTAUTH_SECRET="${secrets.development}"`);
console.log('');

console.log('🚀 For Staging:');
console.log(`NEXTAUTH_SECRET="${secrets.staging}"`);
console.log('');

console.log('🏢 For Production:');
console.log(`NEXTAUTH_SECRET="${secrets.production}"`);
console.log('');

console.log('⚠️  IMPORTANT SECURITY NOTES:');
console.log('1. Never commit these secrets to version control');
console.log('2. Use different secrets for each environment');
console.log('3. Rotate secrets regularly (every 90 days)');
console.log('4. Store production secrets securely (vault, env variables)');
console.log('5. These keys are used to sign JWT tokens and secure sessions');

// Also generate a JWT signing key for the backend
console.log('\n🔑 For Backend JWT (backend/.env):');
console.log(`SECRET_KEY="${generateSecret(64)}"`);
console.log(`JWT_SECRET="${generateSecret(32)}"`);