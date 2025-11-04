# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of GAZ Tank seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues via one of these methods:

1. **Email:** Send details to [security@yourdomain.com] (replace with actual email)
2. **GitHub Security Advisory:** Use the [GitHub Security Advisory](https://github.com/yourusername/GAZTank/security/advisories/new) feature

### What to Include

When reporting a security vulnerability, please include:

- **Type of vulnerability** (e.g., XSS, CSRF, injection, etc.)
- **Affected component** (file path, function name, etc.)
- **Steps to reproduce** the vulnerability
- **Potential impact** of the vulnerability
- **Suggested fix** if you have one
- **Your contact information** for follow-up questions

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 5 business days
- **Status Update:** Every 7 days until resolved
- **Fix Timeline:** Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next scheduled release

### Security Update Process

1. **Verification:** We verify the reported vulnerability
2. **Assessment:** We assess the severity and impact
3. **Development:** We develop and test a fix
4. **Disclosure:** We coordinate disclosure with the reporter
5. **Release:** We release a security update
6. **Announcement:** We publish a security advisory

## Security Best Practices

### For Deployment

When deploying GAZ Tank to production:

1. **Use HTTPS**
   - Enable SSL/TLS certificates (Let's Encrypt recommended)
   - Enable HSTS headers in `.htaccess`

2. **Secure Configuration**
   - Keep `config/deploy.toml` private (already gitignored)
   - Use strong passwords for FTP/SFTP credentials
   - Rotate credentials periodically

3. **Server Configuration**
   - Keep Apache/Nginx updated
   - Enable security headers (CSP, X-Frame-Options, X-Content-Type-Options)
   - Disable directory listing
   - Configure proper file permissions (644 for files, 755 for directories)

4. **Content Security Policy**
   - Review and customize CSP headers in `.htaccess`
   - Whitelist only necessary external domains
   - Use `nonce` or `hash` for inline scripts/styles when possible

5. **Regular Updates**
   - Keep Python dependencies updated: `pip install --upgrade -r requirements.txt`
   - Monitor security advisories for dependencies
   - Review and apply project updates regularly

### For Development

1. **Credentials Management**
   - Never commit credentials to git
   - Use environment variables or gitignored config files
   - Rotate credentials if accidentally exposed

2. **Dependency Security**
   - Review dependencies before installation
   - Use `pip audit` to check for known vulnerabilities
   - Keep dependencies updated

3. **Code Review**
   - Review all pull requests for security issues
   - Use static analysis tools
   - Validate all user inputs

4. **Testing**
   - Test security features (CSP, HSTS, etc.)
   - Verify authentication/authorization
   - Check for XSS, CSRF, injection vulnerabilities

## Known Security Considerations

### Content Security Policy

The default `.htaccess` includes a CSP that allows:
- Scripts from `cdnjs.cloudflare.com` (Prism.js for syntax highlighting)
- Inline styles (for dynamic styling)

**Recommendation:** Review and customize CSP based on your needs.

### External Dependencies

The project loads Prism.js from CDN when syntax highlighting is enabled:
- Source: `cdnjs.cloudflare.com`
- Integrity checks: SRI hashes are used where possible

**Recommendation:** Self-host external libraries for maximum security.

### User-Generated Content

If you allow user-generated content:
- Sanitize all HTML input
- Escape special characters
- Implement Content Security Policy
- Consider using DOMPurify for HTML sanitization

### FTP/FTPS Deployment

Deployment credentials are stored in `config/deploy.toml`:
- File is gitignored by default
- Supports FTPS (secure) and FTP (insecure)

**Recommendation:** 
- Always use FTPS when available
- Consider SFTP or rsync over SSH as alternatives
- Use SSH keys instead of passwords when possible

## Disclosure Policy

We follow **Coordinated Disclosure**:

1. Security issues are kept confidential until a fix is released
2. We coordinate with reporters on disclosure timing
3. We publicly acknowledge reporters (unless they prefer to remain anonymous)
4. We publish security advisories after fixes are released

## Security Acknowledgments

We thank the following researchers for responsibly disclosing security issues:

<!-- List will be populated as issues are reported and fixed -->
- None yet - be the first to help secure GAZ Tank!

## Security Features

### Current Features

- ✅ HTTPS/TLS support with HSTS
- ✅ Content Security Policy (CSP) headers
- ✅ X-Frame-Options protection
- ✅ X-Content-Type-Options nosniff
- ✅ XSS protection headers
- ✅ Secure FTP/FTPS deployment
- ✅ Credential files gitignored
- ✅ No inline JavaScript (except controlled cases)
- ✅ SRI for external resources (where applicable)

### Planned Features

- ⏳ Subresource Integrity (SRI) for all CDN resources
- ⏳ Content sanitization library integration
- ⏳ Automated security scanning in CI/CD
- ⏳ Rate limiting for API endpoints (if added)
- ⏳ CSRF protection (if forms added)

## Additional Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [Content Security Policy Reference](https://content-security-policy.com/)
- [Security Headers Best Practices](https://securityheaders.com/)

## Contact

For security-related questions or concerns:
- Email: [security@yourdomain.com]
- GitHub Security Advisories: [Repository Security Tab]

---

Thank you for helping keep GAZ Tank secure! 🔒
