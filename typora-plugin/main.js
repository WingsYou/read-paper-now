/**
 * Typora Plugin: arXiv Paper Info Fetcher
 * 自动获取论文信息并插入到文档中
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// 获取脚本路径
const SCRIPT_PATH = path.join(__dirname, '..', 'fetch_paper_info.py');
const PYTHON_CMD = 'python3'; // 或 'python'，根据系统而定

/**
 * 执行 Python 脚本获取论文信息
 */
function fetchPaperInfo(url, maxAuthors = 3) {
  return new Promise((resolve, reject) => {
    const cmd = `${PYTHON_CMD} "${SCRIPT_PATH}" "${url}" --max-authors ${maxAuthors}`;

    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`执行失败: ${stderr || error.message}`));
        return;
      }

      resolve(stdout.trim());
    });
  });
}

/**
 * 从文本中提取 URL
 */
function extractUrl(text) {
  const urlPattern = /(https?:\/\/[^\s]+)/;
  const match = text.match(urlPattern);
  return match ? match[1] : null;
}

/**
 * 主命令：获取论文信息
 */
async function fetchPaperInfoCommand() {
  try {
    // 获取选中的文本
    const selection = this.app.workspace.activeEditor.getSelection();

    if (!selection) {
      this.app.vault.adapter.showMessage('请先选中论文链接');
      return;
    }

    // 提取 URL
    const url = extractUrl(selection);
    if (!url) {
      this.app.vault.adapter.showMessage('未找到有效的 URL');
      return;
    }

    // 显示加载提示
    this.app.vault.adapter.showMessage('正在获取论文信息...');

    // 调用 Python 脚本
    const paperInfo = await fetchPaperInfo(url);

    // 插入到文档中
    const editor = this.app.workspace.activeEditor;
    editor.replaceSelection(paperInfo);

    this.app.vault.adapter.showMessage('论文信息已插入');

  } catch (error) {
    console.error('Error:', error);
    this.app.vault.adapter.showMessage(`错误: ${error.message}`);
  }
}

/**
 * 插件激活
 */
function activate(context) {
  console.log('arXiv Paper Info Plugin activated');

  // 注册命令
  context.subscriptions.push(
    context.commands.registerCommand('fetch-paper-info', fetchPaperInfoCommand)
  );
}

/**
 * 插件停用
 */
function deactivate() {
  console.log('arXiv Paper Info Plugin deactivated');
}

module.exports = {
  activate,
  deactivate
};
