/**
 * Typora Plugin: arXiv Paper Info Fetcher
 * Automatically fetch paper information and insert into document
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get script path
const SCRIPT_PATH = path.join(__dirname, '..', 'fetch_paper_info.py');
const PYTHON_CMD = 'python3'; // or 'python', depending on system

/**
 * Execute Python script to fetch paper information
 * @param {string} url - Paper URL
 * @param {number} maxAuthors - Maximum number of authors to display
 * @param {boolean} useGoogleScholar - Whether to prioritize Google Scholar
 */
function fetchPaperInfo(url, maxAuthors = 3, useGoogleScholar = false) {
  return new Promise((resolve, reject) => {
    let cmd = `${PYTHON_CMD} "${SCRIPT_PATH}" "${url}" --max-authors ${maxAuthors}`;

    if (useGoogleScholar) {
      cmd += ' --use-google-scholar-citations';
    }

    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`Execution failed: ${stderr || error.message}`));
        return;
      }

      resolve(stdout.trim());
    });
  });
}

/**
 * Extract URL from text
 */
function extractUrl(text) {
  const urlPattern = /(https?:\/\/[^\s]+)/;
  const match = text.match(urlPattern);
  return match ? match[1] : null;
}

/**
 * Main command: Fetch paper information (Fast mode)
 */
async function fetchPaperInfoCommand() {
  try {
    // Get selected text
    const selection = this.app.workspace.activeEditor.getSelection();

    if (!selection) {
      this.app.vault.adapter.showMessage('Please select a paper link first');
      return;
    }

    // Extract URL
    const url = extractUrl(selection);
    if (!url) {
      this.app.vault.adapter.showMessage('No valid URL found');
      return;
    }

    // Show loading message
    this.app.vault.adapter.showMessage('Fetching paper information...');

    // Call Python script
    const paperInfo = await fetchPaperInfo(url, 3, false);

    // Insert into document
    const editor = this.app.workspace.activeEditor;
    editor.replaceSelection(paperInfo);

    this.app.vault.adapter.showMessage('Paper information inserted');

  } catch (error) {
    console.error('Error:', error);
    this.app.vault.adapter.showMessage(`Error: ${error.message}`);
  }
}

/**
 * Main command: Fetch paper information (Google Scholar mode)
 */
async function fetchPaperInfoGSCommand() {
  try {
    // Get selected text
    const selection = this.app.workspace.activeEditor.getSelection();

    if (!selection) {
      this.app.vault.adapter.showMessage('Please select a paper link first');
      return;
    }

    // Extract URL
    const url = extractUrl(selection);
    if (!url) {
      this.app.vault.adapter.showMessage('No valid URL found');
      return;
    }

    // Show loading message
    this.app.vault.adapter.showMessage('Fetching paper information (Google Scholar)...');

    // Call Python script with Google Scholar priority
    const paperInfo = await fetchPaperInfo(url, 3, true);

    // Insert into document
    const editor = this.app.workspace.activeEditor;
    editor.replaceSelection(paperInfo);

    this.app.vault.adapter.showMessage('Paper information inserted (Google Scholar)');

  } catch (error) {
    console.error('Error:', error);
    this.app.vault.adapter.showMessage(`Error: ${error.message}`);
  }
}

/**
 * Plugin activation
 */
function activate(context) {
  console.log('arXiv Paper Info Plugin activated');

  // Register commands
  context.subscriptions.push(
    context.commands.registerCommand('fetch-paper-info', fetchPaperInfoCommand),
    context.commands.registerCommand('fetch-paper-info-gs', fetchPaperInfoGSCommand)
  );
}

/**
 * Plugin deactivation
 */
function deactivate() {
  console.log('arXiv Paper Info Plugin deactivated');
}

module.exports = {
  activate,
  deactivate
};