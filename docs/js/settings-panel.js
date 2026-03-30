/**
 * 史记知识库 - 配置面板交互脚本
 * 用于控制语法高亮等显示选项
 */

(function() {
    'use strict';

    // 等待 DOM 加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // 获取元素
        const settingsToggle = document.getElementById('settings-toggle');
        const settingsPanel = document.getElementById('settings-panel');
        const syntaxHighlightCheckbox = document.getElementById('syntax-highlight');

        if (!settingsToggle || !settingsPanel || !syntaxHighlightCheckbox) {
            console.warn('配置面板元素未找到');
            return;
        }

        // 从 localStorage 加载配置
        const savedHighlight = localStorage.getItem('shiji-syntax-highlight');
        if (savedHighlight !== null) {
            const isEnabled = savedHighlight === 'true';
            syntaxHighlightCheckbox.checked = isEnabled;
            updateSyntaxHighlight(isEnabled);
        }

        // 切换面板显示/隐藏
        settingsToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            settingsPanel.classList.toggle('active');
        });

        // 点击面板外关闭
        document.addEventListener('click', function(e) {
            if (!settingsPanel.contains(e.target) &&
                !settingsToggle.contains(e.target) &&
                settingsPanel.classList.contains('active')) {
                settingsPanel.classList.remove('active');
            }
        });

        // 点击面板内不关闭
        settingsPanel.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // 语法高亮开关
        syntaxHighlightCheckbox.addEventListener('change', function() {
            const isEnabled = this.checked;
            updateSyntaxHighlight(isEnabled);
            // 保存到 localStorage
            localStorage.setItem('shiji-syntax-highlight', isEnabled);
        });

        // ESC 键关闭面板
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && settingsPanel.classList.contains('active')) {
                settingsPanel.classList.remove('active');
            }
        });
    }

    /**
     * 更新语法高亮状态
     * @param {boolean} enabled - 是否启用语法高亮
     */
    function updateSyntaxHighlight(enabled) {
        if (enabled) {
            document.body.classList.remove('syntax-highlight-off');
        } else {
            document.body.classList.add('syntax-highlight-off');
        }
    }
})();
