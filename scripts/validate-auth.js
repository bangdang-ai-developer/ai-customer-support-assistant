#!/usr/bin/env node

/**
 * NextAuth Configuration Validator
 * Validates environment variables and authentication setup
 */

require('dotenv').config({ path: '.env.local' });

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(color, message) {
  console.log(color + message + colors.reset);
}

function checkRequired(name, value, minLength = 0) {
  if (!value) {
    log(colors.red, `❌ ${name} is missing`);
    return false;
  }
  
  if (minLength && value.length < minLength) {
    log(colors.yellow, `⚠️  ${name} is too short (${value.length} chars, minimum ${minLength})`);
    return false;
  }
  
  log(colors.green, `✅ ${name} is configured (${value.length} chars)`);
  return true;
}

console.log('\n🔐 NextAuth Configuration Validator');
console.log('=====================================\n');

let allValid = true;

// Check NEXTAUTH_SECRET
log(colors.blue, '1. Checking NEXTAUTH_SECRET...');
if (!checkRequired('NEXTAUTH_SECRET', process.env.NEXTAUTH_SECRET, 32)) {
  allValid = false;
  log(colors.red, '   💡 Generate with: node generate-secrets.js');
  log(colors.red, '   💡 Or use: openssl rand -base64 32');
}

// Check NEXTAUTH_URL
log(colors.blue, '\n2. Checking NEXTAUTH_URL...');
if (!checkRequired('NEXTAUTH_URL', process.env.NEXTAUTH_URL)) {
  allValid = false;
  log(colors.red, '   💡 Set to: http://localhost:3000 (development)');
} else {
  // Validate URL format
  try {
    new URL(process.env.NEXTAUTH_URL);
    log(colors.green, '   ✅ URL format is valid');
  } catch (error) {
    log(colors.red, '   ❌ Invalid URL format');
    allValid = false;
  }
}

// Check API URLs
log(colors.blue, '\n3. Checking API configuration...');
checkRequired('NEXT_PUBLIC_API_URL', process.env.NEXT_PUBLIC_API_URL);
checkRequired('NEXT_PUBLIC_WS_URL', process.env.NEXT_PUBLIC_WS_URL);

// Check optional but recommended settings
log(colors.blue, '\n4. Checking optional configurations...');
if (process.env.GOOGLE_AI_API_KEY) {
  log(colors.green, '✅ GOOGLE_AI_API_KEY is configured');
} else {
  log(colors.yellow, '⚠️  GOOGLE_AI_API_KEY not set (AI features will be limited)');
}

if (process.env.DATABASE_URL) {
  log(colors.green, '✅ DATABASE_URL is configured');
} else {
  log(colors.yellow, '⚠️  DATABASE_URL not set (using fallback)');
}

// Security checks
log(colors.blue, '\n5. Security validation...');

if (process.env.NODE_ENV === 'production') {
  if (process.env.NEXTAUTH_SECRET && process.env.NEXTAUTH_SECRET.length < 64) {
    log(colors.yellow, '⚠️  Consider using longer NEXTAUTH_SECRET in production (64+ chars)');
  }
  
  if (process.env.NEXTAUTH_URL && !process.env.NEXTAUTH_URL.startsWith('https://')) {
    log(colors.red, '❌ NEXTAUTH_URL should use HTTPS in production');
    allValid = false;
  }
} else {
  log(colors.cyan, 'ℹ️  Running in development mode');
}

// Check for common mistakes
log(colors.blue, '\n6. Common issues check...');

if (process.env.NEXTAUTH_SECRET === 'your-nextauth-secret-key-32-chars-minimum') {
  log(colors.red, '❌ You\'re using the example NEXTAUTH_SECRET! Please generate a real one.');
  allValid = false;
}

if (process.env.NEXTAUTH_SECRET && process.env.NEXTAUTH_SECRET.includes(' ')) {
  log(colors.red, '❌ NEXTAUTH_SECRET should not contain spaces');
  allValid = false;
}

// Summary
console.log('\n' + '='.repeat(40));
if (allValid) {
  log(colors.green, '🎉 All checks passed! Your NextAuth setup looks good.');
  log(colors.cyan, '\nNext steps:');
  log(colors.cyan, '1. Start the development server: npm run dev');
  log(colors.cyan, '2. Visit: http://localhost:3000');
  log(colors.cyan, '3. Test authentication with demo accounts');
  console.log('\nDemo Accounts:');
  console.log('• Demo User: demo@biwoco.com / demo123');
  console.log('• Admin User: admin@biwoco.com / admin123');
  console.log('• Or use "Continue as Guest"');
} else {
  log(colors.red, '❌ Some issues found. Please fix the above errors.');
  log(colors.yellow, '\n📖 For help, check: NEXTAUTH_SETUP.md');
  process.exit(1);
}

// Show environment file status
console.log('\n📁 Environment files:');
const fs = require('fs');
const envFiles = ['.env.local', '.env', '.env.example'];
envFiles.forEach(file => {
  if (fs.existsSync(file)) {
    log(colors.green, `✅ ${file} exists`);
  } else {
    log(colors.yellow, `⚠️  ${file} not found`);
  }
});

console.log('\n🔐 Security reminder:');
console.log('• Never commit .env.local or .env to version control');
console.log('• Use different secrets for each environment');
console.log('• Rotate secrets regularly (every 90 days)');
console.log('• Keep secrets secure and never share them');

console.log('');