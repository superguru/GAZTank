/**
 * JavaScript Updater using Babel AST
 * 
 * Updates JavaScript files using proper AST parsing and transformation
 * This ensures syntax safety and handles edge cases properly.
 * 
 * Usage: node js_updater.mjs
 * Input: JSON config via stdin
 * Output: SUCCESS or error message
 */

import fs from 'fs';
import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import generate from '@babel/generator';

// Read config from stdin
let configData = '';
process.stdin.setEncoding('utf-8');

process.stdin.on('data', chunk => {
    configData += chunk;
});

process.stdin.on('end', () => {
    try {
        const config = JSON.parse(configData);
        updateJavaScript(config);
        process.stdout.write('SUCCESS');
        process.exit(0);
    } catch (error) {
        process.stderr.write(`ERROR: ${error.message}\n${error.stack}\n`);
        process.exit(1);
    }
});

/**
 * Update JavaScript file with new branding values
 * @param {Object} config - Configuration object
 * @param {string} config.filePath - Path to JavaScript file
 * @param {string} config.siteName - New site name
 * @param {string} config.description - New site description
 */
function updateJavaScript(config) {
    const { filePath, siteName, description } = config;
    
    // Read the JavaScript file
    const code = fs.readFileSync(filePath, 'utf-8');
    
    // Parse the JavaScript into an AST
    const ast = parse(code, {
        sourceType: 'module',
        plugins: ['jsx'] // Support JSX just in case
    });
    
    // Track what we've updated
    let updatesCount = 0;
    
    // Traverse the AST and make updates
    traverse.default(ast, {
        /**
         * Handle template literals like `${pageTitle} - My Awesome Site`
         */
        TemplateLiteral(path) {
            const { quasis, expressions } = path.node;
            
            // Look for patterns: ${pageTitle} - <Site Name>
            // or ${expr} - <Site Name>
            if (expressions.length >= 1 && quasis.length >= 2) {
                const firstExpr = expressions[0];
                const secondQuasi = quasis[1];
                
                // Check if first expression is ${pageTitle} or similar
                const isPageTitle = 
                    (firstExpr.type === 'MemberExpression' && 
                     firstExpr.property?.name === 'pageTitle') ||
                    (firstExpr.type === 'Identifier' && 
                     firstExpr.name === 'pageTitle');
                
                // Check if the text after contains " - " followed by text
                if (isPageTitle && secondQuasi.value.raw.match(/^\s*-\s+/)) {
                    // Update the site name part after the dash
                    const newRaw = ` - ${siteName}`;
                    const newCooked = ` - ${siteName}`;
                    
                    // Preserve any trailing characters (like closing backtick handled by quasis[2])
                    secondQuasi.value.raw = newRaw;
                    secondQuasi.value.cooked = newCooked;
                    updatesCount++;
                }
            }
        },
        
        /**
         * Handle regular string literals
         */
        StringLiteral(path) {
            const value = path.node.value;
            
            // Replace exact matches of "My Awesome Site"
            if (value === 'My Awesome Site') {
                path.node.value = siteName;
                updatesCount++;
            }
            
            // Replace the full description string
            if (value.includes('Welcome to My Awesome Site')) {
                path.node.value = description;
                updatesCount++;
            }
        }
    });
    
    // Generate code from the modified AST
    const output = generate.default(ast, {
        retainLines: false,
        compact: false,
        concise: false,
        quotes: 'single',
        retainFunctionParens: true
    }, code);
    
    // Write the updated code back to the file
    fs.writeFileSync(filePath, output.code, 'utf-8');
    
    // Log to stderr (won't interfere with stdout SUCCESS message)
    process.stderr.write(`Updated ${updatesCount} location(s) in ${filePath}\n`);
}
