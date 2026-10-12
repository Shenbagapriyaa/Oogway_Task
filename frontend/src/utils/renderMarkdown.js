import DOMPurify from 'dompurify';
import { marked } from 'marked';

const MARKDOWN_SANITIZE_OPTIONS = {
  FORBID_TAGS: ['embed', 'form', 'iframe', 'img', 'math', 'object', 'style', 'svg'],
  FORBID_ATTR: ['style']
};

export function renderMarkdown(source) {
  return DOMPurify.sanitize(marked.parse(source), MARKDOWN_SANITIZE_OPTIONS);
}